import { HttpStatus } from '@nestjs/common';
import { UserForbiddenException } from './forbidden-user';

describe('UserForbiddenException', () => {
  it('should create an exception with the default message', () => {
    const exception = new UserForbiddenException();

    expect(exception.getStatus()).toBe(HttpStatus.FORBIDDEN);
    expect(exception.getResponse()).toEqual({
      message: 'Usuário não autorizado.',
      error: 'Forbidden',
    });
  });

  it('should create an exception with a custom message', () => {
    const customMessage = 'Custom forbidden message.';
    const exception = new UserForbiddenException(customMessage);

    expect(exception.getStatus()).toBe(HttpStatus.FORBIDDEN);
    expect(exception.getResponse()).toEqual({
      message: customMessage,
      error: 'Forbidden',
    });
  });
});
