import React, { useState, useCallback, useRef } from 'react';

// Define types inline to avoid import issues
interface FileUploadProps {
  onUploadComplete: (files: any[]) => void;
  onError: (error: string) => void;
  maxFileSize?: number;
  acceptedTypes?: string[];
  multiple?: boolean;
  disabled?: boolean;
}

interface ProcessedFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  uploadDate: Date;
  status: 'completed' | 'error';
  error?: string;
}

const SUPPORTED_FILE_TYPES = [
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

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  onError,
  maxFileSize = 50 * 1024 * 1024, // 50MB
  acceptedTypes = SUPPORTED_FILE_TYPES,
  multiple = true,
  disabled = false
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<any[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const items = e.dataTransfer.items;
    await processFiles(Array.from(items) as any[]);
  }, []);

  const handleFileSelect = useCallback(async (files: FileList) => {
    await processFiles(Array.from(files));
  }, []);

  const processDirectory = async (entry: FileSystemEntry, path: string = ""): Promise<File[]> => {
    const files: File[] = [];

    if (entry.isFile) {
      const fileEntry = entry as FileSystemFileEntry;
      const file = await new Promise<File>((resolve, reject) => {
        fileEntry.file(resolve, reject);
      });
      files.push(file);
    } else if (entry.isDirectory) {
      const dirEntry = entry as FileSystemDirectoryEntry;
      const reader = dirEntry.createReader();

      const entries = await new Promise<FileSystemEntry[]>((resolve, reject) => {
        reader.readEntries(resolve, reject);
      });

      for (const entry of entries) {
        const newPath = path ? `${path}/${entry.name}` : entry.name;
        const subFiles = await processDirectory(entry, newPath);
        files.push(...subFiles);
      }
    }

    return files;
  };

  const processFiles = useCallback(async (files: File[]) => {
    setIsUploading(true);
    let fileArray: File[] = files;

    if (fileArray.length === 0) {
      setErrors(prev => [...prev, 'Nenhum arquivo encontrado']);
      setIsUploading(false);
      return;
    }

    // Filter supported file types
    const supportedExtensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.md', '.txt'];
    const validFiles = fileArray.filter(file => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      const isSupported = supportedExtensions.includes(extension);

      if (!isSupported) {
        setErrors(prev => [...prev, `${file.name}: Tipo de arquivo não suportado`]);
      }

      if (file.size > maxFileSize) {
        setErrors(prev => [...prev, `${file.name}: Arquivo muito grande (máx ${maxFileSize / (1024 * 1024)}MB)`]);
        return false;
      }

      return isSupported;
    });

    if (validFiles.length === 0) {
      setIsUploading(false);
      return;
    }

    // Create uploading files
    const newUploadingFiles = validFiles.map(file => ({
      id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      path: file.webkitRelativePath || file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0
    }));

    setUploadingFiles(prev => [...prev, ...newUploadingFiles]);

    // Send files to backend
    try {
      const formData = new FormData();
      validFiles.forEach(file => {
        formData.append('files', file);
      });

      // Get auth headers using utility function
      const { getAuthHeaders } = await import('@/utils/auth');
      const authHeaders = getAuthHeaders();

      console.log('Making upload request with headers:', authHeaders);

      const response = await fetch('/api/v1/upload/folder', {
        method: 'POST',
        body: formData,
        headers: authHeaders,
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Sessão expirada. Por favor, faça login novamente.');
        }
        throw new Error('Upload failed');
      }

      const result = await response.json();

      // Process uploaded files
      const completedFiles: ProcessedFile[] = result.uploaded_files || [];

      // Clear uploading files
      setUploadingFiles(prev => prev.filter(f => !newUploadingFiles.find(uf => uf.id === f.id)));

      // Call completion callback
      onUploadComplete(completedFiles);

    } catch (error) {
      console.error('Upload error:', error);
      onError('Erro no upload dos arquivos');

      // Mark files as error
      setUploadingFiles(prev =>
        prev.map(f =>
          newUploadingFiles.find(uf => uf.id === f.id)
            ? { ...f, status: 'error', error: 'Upload failed' }
            : f
        )
      );
    } finally {
      setIsUploading(false);
    }
  }, [maxFileSize, onUploadComplete, onError]);

  const removeFile = useCallback((fileId: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== fileId));
    setErrors(prev => prev.filter(e => !e.includes(fileId)));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files);
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${disabled || isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          id="file-input"
          type="file"
          multiple={multiple}
          webkitdirectory
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled || isUploading}
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <div>
            <p className="text-lg font-medium text-gray-900">
              Arraste arquivos ou pastas para cá
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Suporta múltiplos arquivos e pastas até {maxFileSize / (1024 * 1024)}MB por arquivo
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              type="button"
              disabled={disabled || isUploading}
              onClick={() => document.getElementById('file-input')?.click()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {isUploading ? 'Processando...' : 'Selecionar Pasta'}
            </button>

            <button
              type="button"
              disabled={disabled || isUploading}
              onClick={() => {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.multiple = true;
                fileInput.accept = acceptedTypes.join(',');
                fileInput.onchange = (e: Event) => {
                  const target = e.target as HTMLInputElement;
                  if (target && target.files) {
                    handleFileSelect(target.files);
                  }
                };
                fileInput.click();
              }}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Selecionar Arquivos
            </button>
          </div>
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-red-800">Erros</h3>
            <button
              onClick={clearErrors}
              className="text-red-600 hover:text-red-800 text-sm"
            >
              Limpar
            </button>
          </div>
          <ul className="text-sm text-red-700 space-y-1">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Uploading Files */}
      {uploadingFiles.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-3">Enviando arquivos...</h3>
          <div className="space-y-2">
            {uploadingFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between">
                <span className="text-sm text-blue-700">{file.name}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${file.progress || 0}%` }}
                    />
                  </div>
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-xs text-red-600 hover:text-red-800 ml-2"
                  >
                    Remover
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};