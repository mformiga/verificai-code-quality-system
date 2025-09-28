import React, { useRef } from 'react';
import { DragDropZoneProps } from '../../../types/fileUpload';

export const DragDropZone: React.FC<DragDropZoneProps> = ({
  isDragActive,
  onDrag,
  onDrop,
  onFileSelect,
  acceptedTypes,
  multiple = true,
  disabled = false
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files);
    }
    // Reset the input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  const getAcceptedTypesString = () => {
    if (!acceptedTypes || acceptedTypes.length === 0) {
      return '';
    }
    return acceptedTypes.join(',');
  };

  const getAcceptedFileExtensions = () => {
    const extensions = [
      '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp', '.h', '.hpp',
      '.json', '.xml', '.html', '.css', '.md', '.yaml', '.yml', '.txt'
    ];
    return extensions.join(', ');
  };

  return (
    <div
      className={`
        relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
        ${isDragActive
          ? 'border-blue-500 bg-blue-50'
          : disabled
            ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100 cursor-pointer'
        }
      `}
      onDragEnter={onDrag}
      onDragOver={onDrag}
      onDragLeave={onDrag}
      onDrop={onDrop}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={disabled ? -1 : 0}
      role="button"
      aria-label={disabled ? 'Upload disabled' : 'File upload area'}
      aria-disabled={disabled}
    >
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={getAcceptedTypesString()}
        multiple={multiple}
        webkitdirectory={true}
        className="hidden"
        onChange={handleFileInputChange}
        disabled={disabled}
      />

      {/* Upload icon */}
      <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
        <svg
          className="w-full h-full"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 48 48"
          aria-hidden="true"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Main text */}
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-gray-900">
          {isDragActive ? 'Drop files here' : 'Upload your code files'}
        </h3>
        <p className="text-sm text-gray-600">
          {isDragActive
            ? 'Release to upload files'
            : multiple
              ? 'Drag and drop files or folders here, or click to browse'
              : 'Drag and drop file here, or click to browse'
          }
        </p>
      </div>

      {/* File type information */}
      <div className="mt-4 text-xs text-gray-500">
        <p>Supported file types: {getAcceptedFileExtensions()}</p>
        <p>Maximum file size: 50MB</p>
        <p>Folder upload supported</p>
      </div>

      {/* Drag active overlay */}
      {isDragActive && (
        <div className="absolute inset-0 bg-blue-500 bg-opacity-10 rounded-lg flex items-center justify-center">
          <div className="text-blue-600 font-medium">
            Drop files to upload
          </div>
        </div>
      )}

      {/* Disabled overlay */}
      {disabled && (
        <div className="absolute inset-0 bg-gray-200 bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="text-gray-500 font-medium">
            Upload disabled
          </div>
        </div>
      )}
    </div>
  );
};