import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { TestJobService } from './framework/jobs/test.job.service';

async function bootstrap() {
  const appContext = await NestFactory.createApplicationContext(AppModule);
  const integradorService = appContext.get(TestJobService);

  integradorService.execute();

  await appContext.close();
}

bootstrap();
