export interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  path: string;
  content?: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'failed' | 'completed';
  progress: number;
  error?: string;
  uploadedAt?: Date;
}

export interface FileUploadConfig {
  maxSize: number; // in bytes
  allowedTypes: string[];
  maxFiles: number;
}

export interface FileUploadProgress {
  id: string;
  progress: number;
  status: 'uploading' | 'completed' | 'failed';
  error?: string;
}