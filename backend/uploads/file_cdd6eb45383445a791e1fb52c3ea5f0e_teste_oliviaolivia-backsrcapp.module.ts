import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { EnvironmentModule } from '@/shared/environments/environment.module';
// import { AuthModule } from '@/framework/authentication/auth.module';
import { environmentSchema } from './shared/environments/environment';
import { HttpModule } from './gateways/http/http.module';
import { DatabaseModule } from './infrastructure/databases/typeorm/postgres/database.module';
import { TestJobModule } from './framework/jobs/test.module';
import { LoggerModule } from './framework';

@Module({
  imports: [
    ConfigModule.forRoot({
      validate: env => environmentSchema.parse(env),
      isGlobal: true,
    }),
    LoggerModule,
    DatabaseModule,
    //AuthModule,
    HttpModule,
    EnvironmentModule,
    TestJobModule,
  ],
})
export class AppModule {}
