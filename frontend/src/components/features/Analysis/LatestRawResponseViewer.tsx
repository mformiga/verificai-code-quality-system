import React, { useState, useEffect } from 'react';
import { RefreshCw, Download, FileText, AlertCircle, Clock, Code } from 'lucide-react';
import { analysisService } from '@/services/analysisService';

interface LatestRawResponseData {
  success: boolean;
  message: string;
  response_content?: string;
  file_exists: boolean;
  file_size?: number;
  modified_time?: number;
  file_path?: string;
  is_raw?: boolean;
}

const LatestRawResponseViewer: React.FC = () => {
  const [responseData, setResponseData] = useState<LatestRawResponseData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLatestRawResponse = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await analysisService.getLatestRawResponse();
      setResponseData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar resposta bruta da LLM');
      console.error('Error loading latest raw response:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLatestRawResponse();
  }, []);

  const handleDownload = () => {
    if (responseData?.response_content) {
      const blob = new Blob([responseData.response_content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `raw_llm_response_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  const formatDate = (timestamp?: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString('pt-BR');
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <RefreshCw className="animate-spin h-8 w-8 mb-2" />
        <p>Carregando resposta bruta da LLM...</p>
      </div>
    );
  }

  if (error || !responseData) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-500">
        <AlertCircle className="h-8 w-8 mb-2" />
        <p>Erro: {error || 'Falha ao carregar resposta da LLM'}</p>
        <button
          onClick={loadLatestRawResponse}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (!responseData.success || !responseData.response_content) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <FileText className="h-8 w-8 mb-2" />
        <p>{responseData.message || 'Nenhuma resposta bruta da LLM encontrada'}</p>
        <p className="text-sm text-gray-400 mt-2">
          Execute uma análise de código primeiro para gerar uma resposta.
        </p>
        <button
          onClick={loadLatestRawResponse}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Atualizar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <div className="flex items-center space-x-2">
          <Code className="h-5 w-5 text-green-600" />
          <h3 className="text-lg font-semibold">Resposta Bruta da LLM</h3>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
            Sem processamento
          </span>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={loadLatestRawResponse}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
            title="Atualizar resposta"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            onClick={handleDownload}
            className="p-2 text-green-600 hover:bg-green-50 rounded transition-colors"
            title="Baixar resposta"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-600 space-y-1">
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4" />
          <span>Última atualização: {formatDate(responseData.modified_time)}</span>
        </div>
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4" />
          <span>Tamanho: {formatFileSize(responseData.file_size)}</span>
          <span className="text-gray-400">({responseData.response_content.length} caracteres)</span>
        </div>
        {responseData.file_path && (
          <div className="text-xs text-gray-500">
            Arquivo: {responseData.file_path.split('/').pop()}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="border rounded-lg">
        <div className="bg-gray-100 px-4 py-2 border-b rounded-t-lg">
          <h4 className="font-medium text-gray-700">Conteúdo da Resposta Bruta:</h4>
          <p className="text-xs text-gray-500 mt-1">
            Esta é a resposta exata da LLM sem qualquer processamento ou extração de critérios.
          </p>
        </div>
        <div className="max-h-96 overflow-y-auto">
          <pre className="p-4 text-xs bg-gray-900 text-green-400 font-mono whitespace-pre-wrap break-words m-0 rounded-b-lg">
            {responseData.response_content}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default LatestRawResponseViewer;