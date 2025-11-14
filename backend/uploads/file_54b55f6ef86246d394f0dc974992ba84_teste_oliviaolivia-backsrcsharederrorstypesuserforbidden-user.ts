import { HttpException, HttpStatus } from '@nestjs/common';

export class UserForbiddenException extends HttpException {
  constructor(message?: string) {
    super(
      {
        message: message ? message : 'Usuário não autorizado.',
        error: 'Forbidden',
      },
      HttpStatus.FORBIDDEN
    );
  }
}
