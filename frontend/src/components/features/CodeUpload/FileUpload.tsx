import React, { useState, useCallback } from 'react';

// Define types inline to avoid import issues
interface FileUploadProps {
  onUploadComplete: (files: any[]) => void;
  onError: (error: string) => void;
  maxFileSize?: number;
  acceptedTypes?: string[];
  multiple?: boolean;
  disabled?: boolean;
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

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    processFiles(files);
  }, []);

  const handleFileSelect = useCallback((files: FileList) => {
    processFiles(files);
  }, []);

  const processFiles = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);

    if (fileArray.length === 0) {
      setErrors(prev => [...prev, 'No files selected']);
      return;
    }

    // Simple validation
    const validFiles = fileArray.filter(file => {
      if (file.size > maxFileSize) {
        setErrors(prev => [...prev, `${file.name}: File too large`]);
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) {
      return;
    }

    // Create uploading files
    const newUploadingFiles = validFiles.map(file => ({
      id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0
    }));

    setUploadingFiles(prev => [...prev, ...newUploadingFiles]);

    // Simulate upload process
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const uploadingFile = newUploadingFiles[i];

      try {
        // Simulate progress
        for (let progress = 0; progress <= 100; progress += 20) {
          setUploadingFiles(prev =>
            prev.map(f =>
              f.id === uploadingFile.id
                ? { ...f, progress }
                : f
            )
          );
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Complete upload
        setUploadingFiles(prev => prev.filter(f => f.id !== uploadingFile.id));

        const completedFile = {
          id: uploadingFile.id,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadDate: new Date(),
          status: 'completed'
        };

        onUploadComplete([completedFile]);

      } catch (error) {
        setUploadingFiles(prev =>
          prev.map(f =>
            f.id === uploadingFile.id
              ? { ...f, status: 'error', error: 'Upload failed' }
              : f
          )
        );
        onError(`${file.name}: Upload failed`);
      }
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
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          multiple={multiple}
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <div>
            <p className="text-lg font-medium text-gray-900">
              Arraste arquivos para cá ou clique para selecionar
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Suporta múltiplos arquivos até {maxFileSize / (1024 * 1024)}MB
            </p>
          </div>

          <button
            type="button"
            disabled={disabled}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Selecionar Arquivos
          </button>
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
                  <span className="text-xs text-blue-600">{file.progress || 0}%</span>
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-red-600 hover:text-red-800 text-xs"
                  >
                    Cancelar
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