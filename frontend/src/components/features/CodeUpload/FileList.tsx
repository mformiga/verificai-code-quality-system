import React from 'react';
import { UploadedFile } from '../../../types/fileUpload';
import { ProgressIndicator } from './ProgressIndicator';

interface FileListProps {
  files: UploadedFile[];
  onRemoveFile?: (fileId: string) => void;
  onRetryUpload?: (fileId: string) => void;
  showProgress?: boolean;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileIcon = (fileName: string): string => {
  const extension = fileName.split('.').pop()?.toLowerCase() || '';

  const iconMap: Record<string, string> = {
    'js': '📜',
    'jsx': '📜',
    'ts': '📘',
    'tsx': '📘',
    'py': '🐍',
    'java': '☕',
    'c': '⚙️',
    'cpp': '⚙️',
    'h': '📋',
    'hpp': '📋',
    'json': '📄',
    'xml': '📄',
    'html': '🌐',
    'css': '🎨',
    'md': '📝',
    'yaml': '⚙️',
    'yml': '⚙️',
    'txt': '📄'
  };

  return iconMap[extension] || '📄';
};

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'uploading':
      return 'text-blue-600';
    case 'completed':
      return 'text-green-600';
    case 'error':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const FileList: React.FC<FileListProps> = ({
  files,
  onRemoveFile,
  onRetryUpload,
  showProgress = true
}) => {
  if (files.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No files uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">{files.length}</div>
            <div className="text-sm text-gray-600">Total Files</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {files.filter(f => f.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">
              {files.filter(f => f.status === 'uploading').length}
            </div>
            <div className="text-sm text-gray-600">Uploading</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">
              {files.filter(f => f.status === 'error').length}
            </div>
            <div className="text-sm text-gray-600">Failed</div>
          </div>
        </div>
      </div>

      {/* File list */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {files.map((file) => (
          <div
            key={file.id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              {/* File info */}
              <div className="flex items-start space-x-3 flex-1 min-w-0">
                <div className="text-2xl flex-shrink-0">
                  {getFileIcon(file.name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </h4>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                      {file.status}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-gray-500 space-y-1">
                    <p>Path: {file.path}</p>
                    <p>Size: {formatFileSize(file.size)}</p>
                    <p>Type: {file.type || 'Unknown'}</p>
                    <p>Uploaded: {new Date(file.uploadDate).toLocaleString()}</p>
                  </div>

                  {/* Progress indicator */}
                  {showProgress && file.status === 'uploading' && (
                    <div className="mt-3">
                      <ProgressIndicator
                        progress={file.progress || 0}
                        status={file.status}
                        fileName={file.name}
                        error={file.error}
                      />
                    </div>
                  )}

                  {/* Error message */}
                  {file.status === 'error' && file.error && (
                    <div className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
                      {file.error}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 ml-4 flex-shrink-0">
                {file.status === 'error' && onRetryUpload && (
                  <button
                    onClick={() => onRetryUpload(file.id)}
                    className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50 transition-colors"
                    title="Retry upload"
                    aria-label={`Retry upload for ${file.name}`}
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                )}

                {onRemoveFile && (
                  <button
                    onClick={() => onRemoveFile(file.id)}
                    className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50 transition-colors"
                    title="Remove file"
                    aria-label={`Remove ${file.name}`}
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};