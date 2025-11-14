import { Module } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import {

  LaudoController,
  GovBrAuthController,
} from './controllers';

import { EnvironmentModule, EnvironmentService } from '@/shared/environments';
import { HealthController } from './controllers/core/health.controller';
import { HealthIndicatorService, TerminusModule, TypeOrmHealthIndicator } from '@nestjs/terminus';

@Module({
  imports: [TerminusModule, EnvironmentModule],
  controllers: [
    HealthController,
    LaudoController,
    GovBrAuthController,
  ],
  providers: [
    EnvironmentService,
    HealthIndicatorService,
    Reflector,
    TypeOrmHealthIndicator,
  ],
  exports: [HealthIndicatorService, TypeOrmHealthIndicator],
})
export class HttpModule {}
