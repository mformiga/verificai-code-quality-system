import apiClient from './apiClient';
import type { UploadFile, FileUploadConfig } from '@/types/file';

export const fileService = {
  upload: async (file: globalThis.File, onProgress?: (progress: number) => void): Promise<UploadFile> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/files/upload', formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  getUploadConfig: async (): Promise<FileUploadConfig> => {
    const response = await apiClient.get('/files/config');
    return response.data;
  },

  validateFile: (file: globalThis.File): string[] => {
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
  },

  delete: async (fileId: string): Promise<void> => {
    await apiClient.delete(`/files/${fileId}`);
  },
};