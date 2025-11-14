export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): string[] => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('A senha deve ter pelo menos 8 caracteres');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra maiúscula');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra minúscula');
  }

  if (!/\d/.test(password)) {
    errors.push('A senha deve conter pelo menos um número');
  }

  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('A senha deve conter pelo menos um caractere especial');
  }

  return errors;
};

export const validateRequired = (value: any, fieldName: string): string[] => {
  const errors: string[] = [];

  if (value === undefined || value === null || value === '') {
    errors.push(`${fieldName} é obrigatório`);
  }

  return errors;
};

export const validateFileUpload = (file: File): string[] => {
  const errors: string[] = [];
  const maxSize = 50 * 1024 * 1024; // 50MB
  const allowedTypes = [
    'application/javascript',
    'application/x-javascript',
    'text/javascript',
    'text/typescript',
    'application/x-typescript',
    'text/x-python',
    'text/x-java-source',
    'text/x-csrc',
    'text/x-c++src',
  ];

  if (file.size > maxSize) {
    errors.push('O arquivo deve ter no máximo 50MB');
  }

  if (!allowedTypes.includes(file.type)) {
    errors.push('Tipo de arquivo não suportado');
  }

  return errors;
};

export const validatePrompt = (prompt: { name: string; content: string }): string[] => {
  const errors: string[] = [];

  if (!prompt.name.trim()) {
    errors.push('O nome do prompt é obrigatório');
  }

  if (prompt.name.length > 100) {
    errors.push('O nome do prompt deve ter no máximo 100 caracteres');
  }

  if (!prompt.content.trim()) {
    errors.push('O conteúdo do prompt é obrigatório');
  }

  if (prompt.content.length > 5000) {
    errors.push('O conteúdo do prompt deve ter no máximo 5000 caracteres');
  }

  return errors;
};