import { Public } from '@/framework';
import { getDataSource } from '@/infrastructure/databases/typeorm/postgres/database.providers';
import { Controller, Get } from '@nestjs/common';
import { ApiResponse } from '@nestjs/swagger';
import { HealthCheck, HealthCheckService, TypeOrmHealthIndicator } from '@nestjs/terminus';

@Controller('health')
@Public()
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator
  ) {}

  @Get('ready')
  @HealthCheck()
  async readness() {
    if (process.env.NODE_ENV === 'development') {
      return { status: 'ok' };
    }
    try {
      const result = await this.health.check([
        async () =>
          await this.db.pingCheck('postgres', {
            connection: getDataSource(),
          }),
      ]);
      return result;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? `Error: ${error.message}` : 'Unknown error occurred';

      const errorDetails =
        error && typeof error === 'object' && 'details' in error
          ? (error as any).details
          : 'Database connection failed';

      return {
        status: 'down',
        error: {
          message: errorMessage,
          details: errorDetails,
        },
      };
    }
  }

  @Get('live')
  @ApiResponse({
    status: 200,
    description: 'Usuário editado com sucesso.',
    example: { status: 'ok' },
  })
  live() {
    return { status: 'ok' };
  }
}
