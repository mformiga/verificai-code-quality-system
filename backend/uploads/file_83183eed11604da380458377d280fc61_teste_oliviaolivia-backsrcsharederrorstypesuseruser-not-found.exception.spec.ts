import { HttpStatus } from '@nestjs/common';
import { UserNotFoundException } from './user-not-found';

describe('UserNotFoundException', () => {
  it('should create an exception with the default message', () => {
    const exception = new UserNotFoundException();

    expect(exception.getStatus()).toBe(HttpStatus.NOT_FOUND);
    expect(exception.getResponse()).toEqual({
      message: 'Usuário não encontrado.',
      error: 'Bad Request',
    });
  });

  it('should create an exception with a custom message', () => {
    const customMessage = 'Custom user not found message.';
    const exception = new UserNotFoundException(customMessage);

    expect(exception.getStatus()).toBe(HttpStatus.NOT_FOUND);
    expect(exception.getResponse()).toEqual({
      message: customMessage,
      error: 'Bad Request',
    });
  });
});
