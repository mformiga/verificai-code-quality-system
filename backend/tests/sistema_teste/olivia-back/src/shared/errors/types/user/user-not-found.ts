import { HttpException, HttpStatus } from '@nestjs/common';

export class UserNotFoundException extends HttpException {
  constructor(message?: string) {
    super(
      {
        message: message ? message : 'Usuário não encontrado.',
        error: 'Bad Request',
      },
      HttpStatus.NOT_FOUND
    );
  }
}
