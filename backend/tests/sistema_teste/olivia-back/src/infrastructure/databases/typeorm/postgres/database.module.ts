import { Global, Module } from '@nestjs/common';
import { databaseProviders } from './database.providers';
import { EnvironmentModule } from '@/shared/environments';

@Global()
@Module({
  imports: [EnvironmentModule],
  providers: [...databaseProviders],
  exports: [...databaseProviders],
})
export class DatabaseModule {}
