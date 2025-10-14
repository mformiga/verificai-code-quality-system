import { getDataSource } from '@/infrastructure/databases/typeorm/postgres/database.providers';
import { Sessao } from '@/domains/domain/model-entities/sessao.entity';
import { Usuario } from '@/domains/domain/model-entities/usuario.entity';

export interface GovbrUserInfo {
  sub: string;
  name?: string | null;
  email?: string | null;
  email_verified?: boolean;
  picture?: string | null;
  profile?: string | null;
  social_name?: string | null;
}

export class AuthSessionStore {
  static async set(sessionId: string, userId: number, expiresAt?: number) {
    const dataSource = getDataSource() as any;
    const repo = dataSource.getRepository(Sessao);
    const session = repo.create({
      id: sessionId,
      usuario: { id: userId } as Usuario,
      dhExpiracaoSessao: expiresAt ? new Date(expiresAt) : null,
    });
    await repo.save(session);
  }

  static async get(sessionId: string): Promise<Sessao | null> {
    const dataSource = getDataSource() as any;
    return dataSource
      .getRepository(Sessao)
      .findOne({ where: { id: sessionId }, relations: ['usuario'] });
  }

  static async delete(sessionId: string) {
    const dataSource = getDataSource() as any;
    await dataSource.getRepository(Sessao).delete({ id: sessionId });
  }
}
