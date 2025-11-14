import { Controller, Get, Query, Headers, Res, BadRequestException } from '@nestjs/common';
import { GovBrService } from '@/framework/authentication/govbr.service';
import { Response } from 'express';

@Controller('auth/govbr')
export class GovBrAuthController {
  constructor(private readonly govBrService: GovBrService) {}

  @Get('login')
  login(@Res() res: Response) {
    const url = this.govBrService.getAuthorizationUrl();
    return res.redirect(url);
  }

  @Get('callback')
  async callback(@Query('code') code: string, @Query('state') state: string) {
    if (!code || !state) {
      throw new BadRequestException('Parâmetros code/state ausentes');
    }
    return this.govBrService.exchangeCode(code, state);
  }

  @Get('userinfo')
  async getUserInfo(@Headers('authorization') authorization?: string) {
    const accessToken = authorization?.startsWith('Bearer ') ? authorization.slice(7) : undefined;

    if (!accessToken) {
      throw new BadRequestException('Informe o access_token (Authorization: Bearer ...)');
    }

    return this.govBrService.getUserInfo(accessToken);
  }

  @Get('logout')
  async logout(@Query('session_id') sessionId?: string) {
    if (sessionId) {
      await this.govBrService.logout(sessionId);
    }
    return { ok: true };
  }
}
