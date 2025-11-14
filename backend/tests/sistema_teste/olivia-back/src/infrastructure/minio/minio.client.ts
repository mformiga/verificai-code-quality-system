import 'dotenv/config';
import { Client } from 'minio';

const minioClient = new Client({
  endPoint: process.env.MINIO_ENDPOINT || 'localhost',
  port: Number(process.env.MINIO_PORT) || 9000,
  useSSL: (process.env.MINIO_SSL || 'false').toLowerCase() === 'true',
  accessKey: process.env.MINIO_ACCESS_KEY || 'admin',
  secretKey: process.env.MINIO_SECRET_KEY || 'adminadmin',
  region: process.env.MINIO_REGION || 'br-mapa-1',
});

export const MINIO_BUCKET = process.env.MINIO_BUCKET || 'olivia';

export default minioClient;
