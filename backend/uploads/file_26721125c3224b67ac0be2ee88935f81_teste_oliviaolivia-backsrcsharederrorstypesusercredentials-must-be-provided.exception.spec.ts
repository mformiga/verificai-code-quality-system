import { HttpStatus } from '@nestjs/common';
import { CredentialsMustBeProvidedException } from './credentials-must-be-provided';

describe('CredentialsMustBeProvidedException', () => {
  it('should create an exception with the default message', () => {
    const exception = new CredentialsMustBeProvidedException();

    expect(exception.getStatus()).toBe(HttpStatus.BAD_REQUEST);
    expect(exception.getResponse()).toEqual({
      message: 'Crendenciais devem ser informadas.',
      error: 'Bad Request',
    });
  });

  it('should create an exception with a custom message', () => {
    const customMessage = 'Custom error message.';
    const exception = new CredentialsMustBeProvidedException(customMessage);

    expect(exception.getStatus()).toBe(HttpStatus.BAD_REQUEST);
    expect(exception.getResponse()).toEqual({
      message: customMessage,
      error: 'Bad Request',
    });
  });
});
