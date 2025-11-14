import { HttpException, HttpStatus } from '@nestjs/common';

export class InvalidFormatationException extends HttpException {
  constructor(message: string) {
    super(
      {
        message: `Validation Error: ${message}`,
        error: 'Bad Request',
      },
      HttpStatus.BAD_REQUEST
    );
  }
}
