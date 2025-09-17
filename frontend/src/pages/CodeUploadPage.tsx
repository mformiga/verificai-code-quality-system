import React, { useState, useEffect } from 'react';
import { FileUpload } from '@/components/features/CodeUpload/FileUpload';
import AuthDebug from '@/components/debug/AuthDebug';
import toast from 'react-hot-toast';

interface UploadedFile {
  id: string;
  original_name: string;
  file_path: string;
  relative_path: string;
  file_size: number;
  mime_type: string;
  status: string;
  upload_date: string;
}

const CodeUploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);

  // Load files from database on component mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      // Get auth headers using utility function
      const { getAuthHeaders, getAuthData } = await import('@/utils/auth');
      const authHeaders = getAuthHeaders();
      const authData = getAuthData();

      console.log('Loading files with auth:', {
        isAuthenticated: authData?.isAuthenticated,
        hasToken: !!authData?.token,
        headers: authHeaders
      });

      const response = await fetch('/api/v1/upload/', {
        headers: authHeaders,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadedFiles(data.files || []);
      } else if (response.status === 401) {
        toast.error('Sessão expirada. Por favor, faça login novamente.');
      } else {
        toast.error('Erro ao carregar arquivos');
      }
    } catch (error) {
      console.error('Error loading files:', error);
      toast.error('Erro ao carregar arquivos');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (files: any[]) => {
    // Reload files list after upload
    loadFiles();
    toast.success(`${files.length} arquivo(s) enviado(s) com sucesso!`);
  };

  const handleUploadError = (error: string) => {
    toast.error(`Erro no upload: ${error}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload de Código</h1>
          <p className="text-gray-600">
            Envie seus arquivos de código para análise de qualidade. Suporta arrastar e soltar, upload de pastas e múltiplos arquivos.
          </p>
        </div>

        {/* File Upload Component */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <FileUpload
            onUploadComplete={handleUploadComplete}
            onError={handleUploadError}
            maxFileSize={50 * 1024 * 1024} // 50MB
            multiple={true}
          />
        </div>

        {/* Previously Uploaded Files */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Carregando arquivos...</span>
            </div>
          </div>
        ) : uploadedFiles.length > 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Arquivos Enviados</h2>
              <span className="text-sm text-gray-500">
                Total: {uploadedFiles.length} arquivo(s)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uploadedFiles.map((file, index) => (
                <div key={file.id || index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900 truncate" title={file.original_name}>
                      {file.original_name}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      file.status === 'completed' ? 'bg-green-100 text-green-800' :
                      file.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {file.status}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 space-y-1">
                    <p><strong>Nome:</strong> {file.original_name}</p>
                    <p><strong>Caminho:</strong> {file.relative_path || file.file_path}</p>
                    <p><strong>Tamanho:</strong> {(file.file_size / 1024 / 1024).toFixed(2)} MB</p>
                    <p><strong>Tipo:</strong> {file.mime_type || 'Desconhecido'}</p>
                    <p><strong>Enviado:</strong> {new Date(file.upload_date).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum arquivo enviado</h3>
              <p className="mt-1 text-sm text-gray-500">
                Envie seus arquivos de código para começar a análise de qualidade.
              </p>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Instruções de Uso</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Formatos Suportados</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• JavaScript (.js, .jsx)</li>
                <li>• TypeScript (.ts, .tsx)</li>
                <li>• Python (.py)</li>
                <li>• Java (.java)</li>
                <li>• C/C++ (.c, .cpp, .h, .hpp)</li>
                <li>• e muitos outros...</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Recursos</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Arrastar e soltar arquivos</li>
                <li>• Upload de pastas inteiras</li>
                <li>• Seleção múltipla de arquivos</li>
                <li>• Progresso em tempo real</li>
                <li>• Validação de formatos</li>
                <li>• Limite de 50MB por arquivo</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Debug Component */}
        <AuthDebug />
      </div>
    </div>
  );
};

export default CodeUploadPage;