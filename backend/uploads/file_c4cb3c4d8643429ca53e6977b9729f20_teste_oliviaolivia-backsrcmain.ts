import 'reflect-metadata';
import 'module-alias/register';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { EnvironmentService } from './shared/environments/environment.service';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AllExceptionsFilter } from './framework/filters/errors/exception-filter';
import { ErrorsInterceptor } from './framework/interceptors/errors/error-interceptor';
import { AppLogger } from './framework';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors();

  const logger = app.get(AppLogger);
  app.useLogger(logger);

  app.useGlobalFilters(new AllExceptionsFilter());
  app.useGlobalInterceptors(new ErrorsInterceptor(logger));

  const configService = app.get(EnvironmentService);
  const port = configService.get('PORT');

  const config = new DocumentBuilder()
    .setTitle('Skeleton Api')
    .setDescription('Esse é o esqueleto base das aplicações node do MAPA')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api-docs', app, document);

  await app.listen(port);
  logger.log(`Servidor rodando na porta ${port}`, 'Bootstrap');
}
bootstrap();
