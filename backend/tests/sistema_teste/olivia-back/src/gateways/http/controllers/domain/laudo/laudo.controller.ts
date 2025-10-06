import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { randomBytes } from 'crypto';
import {
  BadRequestException,
  Body,
  Controller,
  Get,
  NotFoundException,
  Param,
  Post,
  Res,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { getRepository } from '@/infrastructure/databases/typeorm/postgres/database.providers';
import { LaudoOlivia } from '@/domains/domain/model-entities';
import { Usuario } from '@/domains/domain/model-entities/usuario.entity';
import minioClient, { MINIO_BUCKET } from '@/infrastructure/minio/minio.client';

@Controller('api')
export class LaudoController {
  private async removeFile(filePath?: string): Promise<void> {
    if (!filePath) return;
    try {
      await fs.promises.unlink(filePath);
    } catch {}
  }

  private extractCpf(sub?: string): string {
    if (!sub || typeof sub !== 'string') {
      throw new BadRequestException("O campo 'sub' (CPF) é obrigatório.");
    }
    const cpf = sub.replace(/\D/g, '');
    if (!cpf) {
      throw new BadRequestException("O campo 'sub' deve conter um CPF válido.");
    }
    return cpf;
  }

  private generateFileName(lpco: string, type: 'usuario' | 'ia'): string {
    const safeLpco = lpco.replace(/[^A-Za-z0-9_-]/g, '');
    const hash = randomBytes(6).toString('hex');
    return `${safeLpco}_${type}_${hash}.pdf`;
  }

  @Post('extract-pdf-data')
  @UseInterceptors(FileInterceptor('laudo', { dest: 'uploads/' }))
  async extractPdfData(
    @UploadedFile() laudoFile: Express.Multer.File,
    @Body('lpco') lpco: string,
    @Body('sub') sub: string
  ) {
    if (!laudoFile) {
      throw new BadRequestException("Arquivo 'laudo' não foi enviado.");
    }
    if (laudoFile.mimetype !== 'application/pdf') {
      await this.removeFile(laudoFile.path);
      throw new BadRequestException("O arquivo 'laudo' deve ser um PDF.");
    }
    if (!lpco || typeof lpco !== 'string') {
      await this.removeFile(laudoFile.path);
      throw new BadRequestException("O campo 'lpco' é obrigatório e deve ser uma string.");
    }

    const cpf = this.extractCpf(sub);

    const userRepo = getRepository<Usuario>(Usuario);
    const usuario = await userRepo.findOne({ where: { nrCpf: cpf } });
    if (!usuario) {
      await this.removeFile(laudoFile.path);
      throw new BadRequestException('Usuário não encontrado para o CPF informado.');
    }

    const laudoRepo = getRepository<LaudoOlivia>(LaudoOlivia);
    const laudo = await laudoRepo.findOne({ where: { nrLpco: lpco, usuario: { id: usuario.id } } });

    if (laudo?.jsDadoBruto) {
      await this.removeFile(laudoFile.path);
      return laudo.jsDadoBruto;
    }

    const usuarioFileName = this.generateFileName(lpco, 'usuario');

    const formData = new FormData();
    formData.append('laudo', fs.createReadStream(laudoFile.path), {
      filename: laudoFile.originalname,
      contentType: laudoFile.mimetype,
    });
    formData.append('lpco', lpco);

    try {
      await minioClient.fPutObject(MINIO_BUCKET, usuarioFileName, laudoFile.path);
      const apiResponse = await axios.post(`${process.env.IA_API_URL}/extract-pdf-data`, formData, {
        headers: formData.getHeaders(),
      });

      if (laudo) {
        laudo.jsDadoBruto = apiResponse.data;
        laudo.obLaudoUsuario = usuarioFileName;
        laudo.usuario = usuario;
        await laudoRepo.save(laudo);
      } else {
        const novoLaudo = laudoRepo.create({
          nrLpco: lpco,
          jsDadoBruto: apiResponse.data,
          dhCriacaoRegistro: new Date(),
          obLaudoUsuario: usuarioFileName,
          usuario,
        });
        await laudoRepo.save(novoLaudo);
      }
      return apiResponse.data;
    } catch (error: any) {
      console.error('Erro no processamento do laudo:', error);
      throw new BadRequestException(
        error.response?.data || error.message || 'Erro ao processar a requisição'
      );
    } finally {
      await this.removeFile(laudoFile.path);
    }
  }

  @Get('laudo/historico')
  async getHistorico() {
    const laudoRepo = getRepository<LaudoOlivia>(LaudoOlivia);

    const historico = await laudoRepo.find({
      select: ['id', 'nrLpco', 'dhCriacaoRegistro', 'obLaudoUsuario', 'obLaudoIa'],
      relations: ['usuario'],
      order: { dhCriacaoRegistro: 'DESC' },
    });

    return historico.map(i => ({
      id: i.id,
      lpco: i.nrLpco,
      criacao: i.dhCriacaoRegistro,
      laudoEnviado: i.obLaudoUsuario,
      laudoProcessado: i.obLaudoIa,
      clienteNome: i.usuario?.nmUsuario,
    }));
  }

  @Get('laudo/:filename')
  async getLaudoPdf(@Param('filename') filename: string, @Res() res: Response) {
    const sanitizedFilename = path.basename(filename);
    try {
      const fileStream = await minioClient.getObject(MINIO_BUCKET, sanitizedFilename);
      res.setHeader('Content-Type', 'application/pdf');
      fileStream.on('error', () => {
        res.status(404).json({ error: 'Arquivo não encontrado.' });
      });
      fileStream.pipe(res);
    } catch (e) {
      console.error('laudo/:filename - Erro ao obter arquivo do MinIO:', e);
      res.status(404).json({ error: 'Arquivo não encontrado.' });
    }
  }

  @Post('data-processing')
  async dataProcessing(
    @Body('lpco') lpco: string,
    @Body('chem_data') chemData: string,
    @Body('sub') sub?: string
  ) {
    if (!lpco || typeof lpco !== 'string' || lpco.trim() === '') {
      throw new BadRequestException("O campo 'lpco' é obrigatório e deve ser uma string válida.");
    }
    if (!chemData || typeof chemData !== 'string') {
      throw new BadRequestException("O campo 'chem_data' é obrigatório e deve ser uma string.");
    }
    let parsedChemData: any;
    try {
      parsedChemData = JSON.parse(chemData);
      if (
        typeof parsedChemData !== 'object' ||
        Array.isArray(parsedChemData) ||
        Object.keys(parsedChemData).length === 0
      ) {
        throw new Error('O campo "chem_data" deve conter um objeto JSON válido e não vazio.');
      }
    } catch (e: any) {
      throw new BadRequestException(`O campo 'chem_data' deve conter um JSON válido. ${e.message}`);
    }

    this.extractCpf(sub);

    const laudoRepo = getRepository<LaudoOlivia>(LaudoOlivia);
    const laudo = await laudoRepo.findOne({ where: { nrLpco: lpco } });

    if (!laudo) {
      throw new NotFoundException('Laudo não encontrado para o LPCO informado.');
    }

    const body = {
      lpco,
      chem_data: parsedChemData.quimico,
      sec_data: parsedChemData.cabecalho,
    };

    const aiFileName = this.generateFileName(lpco, 'ia');

    const tempDir = path.join(process.cwd(), 'temp');
    await fs.promises.mkdir(tempDir, { recursive: true });
    const filePath = path.join(tempDir, aiFileName);

    try {
      const apiResponse = await axios.post(`${process.env.IA_API_URL}/data-processing`, body, {
        responseType: 'stream',
      });

      const writer = fs.createWriteStream(filePath);
      apiResponse.data.pipe(writer);
      await new Promise<void>((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
      });

      try {
        await minioClient.fPutObject(MINIO_BUCKET, aiFileName, filePath);
      } catch (e) {
        console.error('Erro ao salvar no MinIO:', e);
        throw new BadRequestException('Erro ao salvar arquivo no MinIO.');
      }

      const xMensagem = apiResponse.headers['x-mensagem'];
      const xLpco = apiResponse.headers['x-lpco'];
      const xLinkSharepoint = apiResponse.headers['x-link-sharepoint'];

      laudo.obLaudoIa = aiFileName;
      laudo.jsDadoUsuario = parsedChemData;
      await laudoRepo.save(laudo);

      return {
        message: xMensagem || 'Arquivo recebido e salvo com sucesso!',
        lpco: xLpco,
        link_sharepoint: xLinkSharepoint,
        laudo: aiFileName,
      };
    } catch (error: any) {
      throw new BadRequestException(
        error.response?.data || error.message || 'Erro ao processar a requisição'
      );
    } finally {
      await this.removeFile(filePath);
    }
  }
}
