import { z } from 'zod';

export const environmentSchema = z
  .object({
    NODE_ENV: z.string().optional().default('development'),
    PORT: z.coerce.number().optional().default(8080),
    MAPA_TYPEORM_POSTGRES_TYPE: z.enum(['postgres']).default('postgres'),
    POSTGRES_HOST: z.string().optional(),
    POSTGRES_PORT: z.coerce.number().optional().default(5432),
    POSTGRES_SCHEMA: z.string().optional(),
    POSTGRES_PASSWORD: z.string().optional(),
    POSTGRES_USER: z.string().optional(),
    POSTGRES_DB: z.string().optional(),
    POSTGRES_LOGAR: z.coerce.boolean().default(false),
    IA_API_URL: z.string().optional().default('http://localhost'),
    GOVBR_CLIENT_ID: z.string(),
    GOVBR_CLIENT_SECRET: z.string(),
    GOVBR_REDIRECT_URL: z.string(),
    GOVBR_URL: z.string(),
    MINIO_ACCESS_KEY: z.string(),
    MINIO_SECRET_KEY: z.string(),
    MINIO_ENDPOINT: z.string(),
    MINIO_PORT: z.coerce.number().default(443),
    MINIO_SSL: z.coerce.boolean().default(true),
    MINIO_BUCKET: z.string(),
    MINIO_REGION: z.string(),
  })
  .refine(
    env => {
      if (env.NODE_ENV !== 'development') {
        return (
          !!env.POSTGRES_HOST &&
          !!env.POSTGRES_SCHEMA &&
          !!env.POSTGRES_PASSWORD &&
          !!env.POSTGRES_USER &&
          !!env.POSTGRES_DB
        );
      }
      return true;
    },
    {
      message: 'Database environment variables are required unless NODE_ENV=development',
      path: ['POSTGRES_HOST'],
    }
  );

export type Environment = z.infer<typeof environmentSchema>;
