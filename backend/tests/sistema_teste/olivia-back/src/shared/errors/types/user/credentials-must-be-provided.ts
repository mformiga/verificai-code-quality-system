import { HttpException, HttpStatus } from '@nestjs/common';

export class CredentialsMustBeProvidedException extends HttpException {
  constructor(message?: string) {
    super(
      {
        message: message ? message : 'Crendenciais devem ser informadas.',
        error: 'Bad Request',
      },
      HttpStatus.BAD_REQUEST
    );
  }
}
