export interface UploadedFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  uploadDate: Date;
  status: 'uploading' | 'completed' | 'error';
  progress?: number;
  error?: string;
}

export interface FileUploadProps {
  onUploadComplete: (files: UploadedFile[]) => void;
  onError: (error: string) => void;
  maxFileSize?: number; // Default: 50MB
  acceptedTypes?: string[];
  multiple?: boolean;
  disabled?: boolean;
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export interface UploadProgress {
  fileId: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface DragDropZoneProps {
  isDragActive: boolean;
  onDrag: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: (files: FileList) => void;
  acceptedTypes?: string[];
  multiple?: boolean;
  disabled?: boolean;
}

export interface FileListProps {
  files: UploadedFile[];
  onRemoveFile?: (fileId: string) => void;
  onRetryUpload?: (fileId: string) => void;
  showProgress?: boolean;
}

export interface ProgressIndicatorProps {
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  fileName?: string;
  error?: string;
}

export interface FileUploadHook {
  isDragActive: boolean;
  uploadProgress: number;
  uploadingFiles: UploadedFile[];
  handleDrag: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => void;
  handleFileSelect: (files: FileList) => void;
  removeFile: (fileId: string) => void;
  retryUpload: (fileId: string) => void;
}

export interface FileUploadService {
  uploadFile: (file: File, onProgress?: (progress: number) => void) => Promise<UploadedFile>;
  validateFile: (file: File) => ValidationResult;
  cancelUpload: (fileId: string) => void;
}

export interface UploadApiResponse {
  success: boolean;
  data?: UploadedFile;
  error?: string;
  message?: string;
}

// Supported file types and their MIME types
export const SUPPORTED_FILE_TYPES = [
  'application/javascript',
  'application/x-javascript',
  'text/javascript',
  'text/typescript',
  'application/typescript',
  'text/x-python',
  'text/x-java-source',
  'text/x-csrc',
  'text/x-c++src',
  'text/x-c',
  'text/x-c++',
  'text/plain',
  'application/json',
  'text/xml',
  'application/xml',
  'text/html',
  'text/css',
  'text/markdown',
  'text/x-yaml',
  'text/yaml',
  'application/x-yaml'
];

// File extensions mapping
export const FILE_EXTENSIONS = {
  '.js': 'application/javascript',
  '.jsx': 'application/javascript',
  '.ts': 'text/typescript',
  '.tsx': 'text/typescript',
  '.py': 'text/x-python',
  '.java': 'text/x-java-source',
  '.c': 'text/x-csrc',
  '.cpp': 'text/x-c++src',
  '.cxx': 'text/x-c++src',
  '.cc': 'text/x-c++src',
  '.h': 'text/x-csrc',
  '.hpp': 'text/x-c++src',
  '.json': 'application/json',
  '.xml': 'application/xml',
  '.html': 'text/html',
  '.htm': 'text/html',
  '.css': 'text/css',
  '.md': 'text/markdown',
  '.yaml': 'text/x-yaml',
  '.yml': 'text/x-yaml',
  '.txt': 'text/plain'
};

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const CHUNK_SIZE = 1024 * 1024; // 1MB chunks for large files