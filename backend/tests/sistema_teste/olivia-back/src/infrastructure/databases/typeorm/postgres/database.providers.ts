import { DataSource } from 'typeorm';
import { MAPA_POSTGRES_DATA_SOURCE } from '@/shared/constants';
import entidades from '@/domains/domain/model-entities';
import { EnvironmentModule, EnvironmentService } from '@/shared/environments';
import { AppLogger } from '@/framework';

class InMemoryRepository<T extends { id?: any }> {
  private items: T[] = [];

  create(entity: Partial<T>): T {
    return entity as T;
  }

  async save(entity: T): Promise<T> {
    if (entity.id === undefined || entity.id === null) {
      (entity as any).id = this.items.length + 1;
    }
    const index = this.items.findIndex(item => item.id === (entity as any).id);
    if (index >= 0) {
      this.items[index] = entity;
    } else {
      this.items.push(entity);
    }
    return entity;
  }

  async findOne(options: { where: any }): Promise<T | null> {
    const conditions = Array.isArray(options.where) ? options.where : [options.where];
    const match = (item: any, cond: any): boolean => {
      return Object.entries(cond).every(([k, v]) => {
        const left = item[k];
        if (v && typeof v === 'object') {
          if ('id' in v && left && typeof left === 'object' && 'id' in left) {
            return left.id === (v as any).id;
          }
          return left === v;
        }
        return left === v;
      });
    };
    return this.items.find(item => conditions.some(cond => match(item, cond))) || null;
  }

  async find(_options?: any): Promise<T[]> {
    void _options;
    return this.items;
  }
}

class InMemoryDataSource {
  private repositories = new Map<any, InMemoryRepository<any>>();

  getRepository<T extends { id?: any }>(target: any): InMemoryRepository<T> {
    if (!this.repositories.has(target)) {
      this.repositories.set(target, new InMemoryRepository<T>());
    }
    return this.repositories.get(target) as InMemoryRepository<T>;
  }
}

export type DataSourceLike = DataSource | InMemoryDataSource;

let dataSourceInstance: DataSourceLike | null = null;

export const databaseProviders = [
  {
    provide: MAPA_POSTGRES_DATA_SOURCE,
    imports: [EnvironmentModule],
    inject: [EnvironmentService, AppLogger],
    useFactory: async (
      configService: EnvironmentService,
      logger: AppLogger
    ): Promise<DataSourceLike> => {
      if (dataSourceInstance) {
        logger.log('Retornando DataSource já inicializado.', 'databaseProviders');
        return dataSourceInstance;
      }

      if (configService.get('NODE_ENV') === 'development') {
        logger.log('NODE_ENV=development - usando InMemoryDataSource.', 'databaseProviders');
        const dataSource = new InMemoryDataSource();
        dataSourceInstance = dataSource;
        return dataSource;
      }

      logger.log('Inicializando DataSource.', 'databaseProviders');
      const dataSource = new DataSource({
        type: configService.get('MAPA_TYPEORM_POSTGRES_TYPE'),
        host: configService.get('POSTGRES_HOST'),
        schema: configService.get('POSTGRES_SCHEMA'),
        port: configService.get('POSTGRES_PORT'),
        username: configService.get('POSTGRES_USER'),
        password: configService.get('POSTGRES_PASSWORD'),
        database: configService.get('POSTGRES_DB'),
        entities: [...entidades],
        synchronize: false,
        logging: configService.get('POSTGRES_LOGAR'),
      });

      try {
        await dataSource.initialize();
        logger.log('Retornando DataSource já inicializado.', 'databaseProviders');
        dataSourceInstance = dataSource;
        return dataSource;
      } catch (error) {
        if (error instanceof Error) {
          logger.error(
            `Erro ao inicializar DataSource: ${error.message}`,
            error.stack,
            'databaseProviders'
          );
        } else {
          logger.error('Erro desconhecido ao inicializar DataSource', '', 'databaseProviders');
        }
        throw error;
      }
    },
  },
];

export const getDataSource = (): DataSourceLike => {
  if (!dataSourceInstance) {
    throw new Error('O DataSource ainda não foi inicializado!');
  }
  return dataSourceInstance;
};

// Tipagem mínima comum entre TypeORM Repository e InMemoryRepository
export type RepositoryLike<T extends { id?: any }> = {
  create(entity: Partial<T>): T;
  save(entity: T): Promise<T>;
  findOne(options: { where: any }): Promise<T | null>;
  find(options?: any): Promise<T[]>;
};

// Helper para unificar o acesso ao repositório sem erro de união de tipos
export const getRepository = <T extends { id?: any }>(target: any): RepositoryLike<T> => {
  // O retorno é compatível estruturalmente com RepositoryLike
  return (getDataSource() as any).getRepository(target) as RepositoryLike<T>;
};
