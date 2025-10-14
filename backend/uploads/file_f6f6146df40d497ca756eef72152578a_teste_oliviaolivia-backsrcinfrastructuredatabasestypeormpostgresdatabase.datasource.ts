import { DataSource } from 'typeorm';
import 'dotenv/config';
const port = process.env.POSTGRES_PORT ? parseInt(process.env.POSTGRES_PORT) : 5432;

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.POSTGRES_HOST,
  port: port,
  username: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB,
  schema: process.env.POSTGRES_SCHEMA,
  synchronize: true,
  logging: true,
  entities: ['{src,dist}/**/*.entidade{.ts,.js}'],
  migrations: ['./dist/**/migrations/*.js'],
  subscribers: [],
});
