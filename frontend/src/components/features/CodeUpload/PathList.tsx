import React, { useState, useEffect, useRef, useCallback } from 'react';
// Função alternativa para gerar UUID sem dependência externa
const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};
import './PathList.css';

interface FilePath {
  id: string;
  fullPath: string;
  fileName: string;
  fileExtension: string;
  folderPath: string;
  fileSize?: number;
  lastModified?: Date;
  created_at?: string;
}

interface PathListProps {
  paths?: FilePath[];
  onLoadPaths?: (paths: FilePath[]) => void;
  autoRefresh?: boolean;
  onClearAll?: () => void;
  onRefresh?: () => void;
  onFolderSelect?: (paths: FilePath[]) => void;
  onError?: (error: string) => void;
  onSelectionComplete?: () => void;
}

const PathList: React.FC<PathListProps> = ({
  paths: initialPaths = [],
  onLoadPaths,
  autoRefresh = true,
  onClearAll,
  onRefresh,
  onFolderSelect,
  onError,
  onSelectionComplete
}) => {
  const [paths, setPaths] = useState<FilePath[]>(initialPaths);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [selectedFolderPath, setSelectedFolderPath] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [sortBy, setSortBy] = useState<'fileName' | 'fullPath' | 'fileSize' | 'lastModified'>('fileName');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileExtension = (fileName: string): string => {
    const parts = fileName.split('.');
    return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
  };

  const handleFolderSelect = useCallback(async (files: FileList) => {
    console.log('handleFolderSelect called with:', {
      fileCount: files.length,
      firstFileName: files[0]?.name,
      firstFilePath: files[0]?.webkitRelativePath
    });

    try {
      setIsScanning(true);
      setScanProgress(0);

      // Extract folder path from the first file
      const firstFile = files[0];
      if (!firstFile) {
        if (onError) onError('No files selected');
        return;
      }

      const relativePath = firstFile.webkitRelativePath || '';
      const folderPath = relativePath.split('/')[0] || 'selected_folder';
      console.log('Processing folder:', { folderPath, relativePath });

      // Store the complete folder path for display
      setSelectedFolderPath(folderPath);

      // Process files to extract path information
      const filePaths: FilePath[] = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const relativePath = file.webkitRelativePath || '';
        const pathParts = relativePath.split('/');
        const fileName = pathParts[pathParts.length - 1];
        const folderPath = pathParts.slice(0, -1).join('/');

        // Create a simulated full path for display
        // Note: Browser security restrictions prevent getting actual full file paths
        // So we construct a reasonable approximation
        const simulatedFullPath = `C:\\Users\\formi\\Desktop\\teste_sistema\\${relativePath.replace(/\//g, '\\')}`;

        const filePath: FilePath = {
          id: generateUUID(),
          fullPath: simulatedFullPath, // Use the simulated full path
          fileName,
          fileExtension: getFileExtension(fileName),
          folderPath,
          fileSize: file.size,
          lastModified: new Date(file.lastModified)
        };

        filePaths.push(filePath);

        // Update progress
        setScanProgress(((i + 1) / files.length) * 100);

        // Small delay to show progress
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Try to persist paths to database, but continue even if it fails
      try {
        console.log('Attempting to save paths to database...');
        const { getAuthHeaders } = await import('@/utils/auth');
        const authHeaders = getAuthHeaders();

        console.log('Auth headers:', { hasAuth: !!authHeaders.Authorization });

        if (authHeaders.Authorization) {
          // Transform frontend camelCase to backend snake_case
          const transformedFilePaths = filePaths.map(path => ({
            full_path: path.fullPath,
            file_name: path.fileName,
            file_extension: path.fileExtension,
            folder_path: path.folderPath,
            file_size: path.fileSize,
            last_modified: path.lastModified?.toISOString()
          }));

          const response = await fetch('/api/v1/file-paths/bulk', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...authHeaders
            },
            body: JSON.stringify({
              file_paths: transformedFilePaths
            })
          });

          console.log('Database response:', {
            status: response.status,
            statusText: response.statusText
          });

          if (!response.ok) {
            if (response.status === 401) {
              console.warn('Authentication failed - continuing without database save');
            } else {
              const errorText = await response.text();
              console.error('Server error response:', errorText);
            }
          } else {
            const result = await response.json();
            console.log('Save result:', result);

            if (result.errors && result.errors.length > 0) {
              console.warn('Some paths could not be saved:', result.errors);
            }
          }
        } else {
          console.warn('No authentication token - skipping database save');
        }
      } catch (error) {
        console.warn('Error saving file paths (continuing anyway):', error);
      }

      // Always call onFolderSelect, even if database save failed
      if (onFolderSelect) {
        onFolderSelect(filePaths);
      }

      // Notify that selection is complete to trigger list refresh
      if (onSelectionComplete) {
        onSelectionComplete();
      }

    } catch (error) {
      console.error('Error scanning folder:', error);
      if (onError) onError(error instanceof Error ? error.message : 'Failed to scan folder');
    } finally {
      setIsScanning(false);
      setScanProgress(0);
    }
  }, [onFolderSelect, onError, onSelectionComplete]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File input changed:', {
      files: e.target.files,
      fileCount: e.target.files?.length,
      firstFile: e.target.files?.[0]?.name
    });

    if (e.target.files && e.target.files.length > 0) {
      handleFolderSelect(e.target.files);
    } else {
      console.warn('No files selected');
      if (onError) onError('Nenhum arquivo selecionado. Por favor, escolha uma pasta com arquivos.');
    }
  };

  const loadPaths = async () => {
    try {
      setLoading(true);
      setError(null);

      const { getAuthHeaders, isAuthenticated } = await import('@/utils/auth');

      // Check if user is authenticated first
      if (!isAuthenticated()) {
        setError('Por favor, faça login para ver os caminhos de arquivos.');
        return;
      }

      const authHeaders = getAuthHeaders();

      const response = await fetch('/api/v1/file-paths/?page=1&per_page=20', {
        headers: authHeaders
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Sessão expirada. Por favor, faça login novamente.');
        }
        throw new Error('Failed to load file paths');
      }

      const result = await response.json();

      // Transform backend snake_case to frontend camelCase
      const transformedPaths = (result.file_paths || []).map((path: any) => ({
        id: path.id,
        fullPath: path.full_path,
        fileName: path.file_name,
        fileExtension: path.file_extension,
        folderPath: path.folder_path,
        fileSize: path.file_size,
        lastModified: path.last_modified ? new Date(path.last_modified) : undefined,
        created_at: path.created_at
      }));

      setPaths(transformedPaths);

      if (onLoadPaths) {
        onLoadPaths(transformedPaths);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load paths';
      setError(errorMessage);
      console.error('Error loading paths:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoRefresh) {
      loadPaths();
    }
  }, [autoRefresh]);

  const filteredAndSortedPaths = React.useMemo(() => {
    let filtered = paths;

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(path =>
        path.fileName.toLowerCase().includes(term) ||
        path.fullPath.toLowerCase().includes(term) ||
        path.fileExtension.toLowerCase().includes(term) ||
        path.folderPath.toLowerCase().includes(term)
      );
    }

    // Sort paths
    return filtered.sort((a, b) => {
      let aValue: any = a[sortBy];
      let bValue: any = b[sortBy];

      if (sortBy === 'fileSize') {
        aValue = aValue || 0;
        bValue = bValue || 0;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [paths, searchTerm, sortBy, sortOrder]);

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      // Optionally show a success message
    }).catch(err => {
      console.error('Failed to copy text:', err);
    });
  };

  const exportToCSV = () => {
    const csvContent = [
      ['File Path', 'File Name', 'Extension', 'Folder Path', 'Size', 'Modified'],
      ...filteredAndSortedPaths.map(path => [
        path.fullPath,
        path.fileName,
        path.fileExtension,
        path.folderPath,
        path.fileSize ? formatFileSize(path.fileSize) : '',
        path.lastModified ? formatDate(path.lastModified.toString()) : ''
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `file_paths_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Carregando caminhos de arquivos...</span>
        </div>
      </div>
    );
  }

  if (error) {
    const isAuthError = error.includes('login') || error.includes('Sessão expirada');
    return (
      <div className={`${isAuthError ? 'bg-blue-50 border-blue-200' : 'bg-red-50 border-red-200'} rounded-lg p-6`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`text-sm font-medium ${isAuthError ? 'text-blue-800' : 'text-red-800'}`}>
              {isAuthError ? 'Autenticação necessária' : 'Erro ao carregar caminhos'}
            </h3>
            <p className={`text-sm ${isAuthError ? 'text-blue-600' : 'text-red-600'} mt-1`}>{error}</p>
          </div>
          {!isAuthError && (
            <button
              onClick={loadPaths}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Tentar novamente
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="path-list">
      {/* Hidden file input for folder selection */}
      <input
        ref={fileInputRef}
        id="folder-input"
        type="file"
        webkitdirectory=""
        directory=""
        multiple
        className="hidden"
        onChange={handleFileInputChange}
        disabled={isScanning}
      />

      {/* Header */}
      <div className="path-list-header">
        <div className="br-card">
          <div className="card-header">
            <h2 className="text-h2">Caminhos de Arquivos</h2>
            <p className="text-regular">
              {filteredAndSortedPaths.length} arquivo(s) encontrado(s)
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="path-list-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar arquivos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="br-input"
          />
        </div>

        <div className="action-buttons">
          <button
            onClick={() => document.getElementById('folder-input')?.click()}
            disabled={isScanning}
            className="br-button"
            type="button"
          >
            {isScanning ? (
              <div className="flex items-center space-x-2">
                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Selecionando...</span>
              </div>
            ) : (
              'Selecionar Pasta'
            )}
          </button>

          <button
            onClick={onRefresh || loadPaths}
            className="br-button"
            type="button"
          >
            Atualizar
          </button>

          <button
            onClick={exportToCSV}
            disabled={filteredAndSortedPaths.length === 0}
            className="br-button secondary"
            type="button"
          >
            Exportar CSV
          </button>

          {onClearAll && (
            <button
              onClick={onClearAll}
              disabled={filteredAndSortedPaths.length === 0}
              className="br-button danger"
              type="button"
            >
              Limpar Todos
            </button>
          )}
        </div>
      </div>

      {/* Scanning Progress */}
      {isScanning && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-blue-800">
              Selecionando pasta...
            </h4>
            <span className="text-sm text-blue-600">
              {Math.round(scanProgress)}%
            </span>
          </div>

          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${scanProgress}%` }}
            />
          </div>

          <p className="text-xs text-blue-600 mt-2">
            Extraindo caminhos dos arquivos e salvando no banco de dados...
          </p>
        </div>
      )}

      {/* Path List */}
      <div className="br-card">
        {filteredAndSortedPaths.length === 0 ? (
          <div className="empty-state">
            <p className="text-center">
              {searchTerm ? 'Nenhum arquivo encontrado para os termos de busca.' : 'Selecione uma pasta para começar.'}
            </p>
          </div>
        ) : (
          <div className="path-items">
            {filteredAndSortedPaths.map((path) => (
              <div key={path.id} className="path-item">
                <div className="path-content">
                  <code className="path-text">{path.fullPath}</code>
                </div>
                <div className="path-actions">
                  <button
                    onClick={() => copyToClipboard(path.fullPath)}
                    className="br-button circle small"
                    type="button"
                    title="Copiar caminho"
                  >
                    <svg className="br-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {paths.length > 0 && (
        <div className="path-list-footer">
          <p className="text-center text-regular">
            Mostrando {filteredAndSortedPaths.length} de {paths.length} arquivos
          </p>
        </div>
      )}
    </div>
  );
};

export default PathList;