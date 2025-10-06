import { randomBytes, createHash } from 'crypto';

export function base64url(input: Buffer | string): string {
  const buff = Buffer.isBuffer(input) ? input : Buffer.from(input);
  return buff.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

export function generateCodeVerifier(length = 64): string {
  return base64url(randomBytes(length));
}

export function deriveCodeChallengeS256(codeVerifier: string): string {
  const hash = createHash('sha256').update(codeVerifier).digest();
  return base64url(hash);
}
