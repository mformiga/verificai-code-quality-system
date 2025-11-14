import React, { useState, useEffect } from 'react';
import { RefreshCw, Download, FileText, AlertCircle, Clock } from 'lucide-react';
import { analysisService } from '@/services/analysisService';

interface LatestPromptData {
  success: boolean;
  message: string;
  prompt_content?: string;
  file_exists: boolean;
  file_size?: number;
  modified_time?: number;
  file_path?: string;
  token_usage?: {
    total_tokens?: number;
    prompt_tokens?: number;
    completion_tokens?: number;
  };
}

const LatestPromptViewer: React.FC = () => {
  const [promptData, setPromptData] = useState<LatestPromptData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLatestPrompt = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await analysisService.getLatestPrompt();
      setPromptData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar prompt');
      console.error('Error loading latest prompt:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLatestPrompt();
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('pt-BR');
  };

  const formatTokenCount = (tokens: number) => {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
    return tokens.toString();
  };

  const downloadPrompt = () => {
    if (!promptData?.prompt_content) return;

    const blob = new Blob([promptData.prompt_content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prompt_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="br-card">
        <div className="card-content">
          <div className="d-flex align-items-center justify-content-center" style={{ minHeight: '200px' }}>
            <RefreshCw className="animate-spin mr-2" />
            <span>Carregando prompt...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="br-card">
        <div className="card-content">
          <div className="d-flex align-items-center text-danger">
            <AlertCircle className="mr-2" />
            <span>Erro: {error}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!promptData || !promptData.file_exists) {
    return (
      <div className="br-card">
        <div className="card-content">
          <div className="text-center py-5">
            <FileText className="mb-3" style={{ width: '48px', height: '48px', opacity: 0.5 }} />
            <h3 className="text-h3 mb-2">Nenhum prompt encontrado</h3>
            <p className="text-regular text-muted mb-4">
              Execute uma análise primeiro para gerar um prompt.
            </p>
            <button
              className="br-button primary"
              onClick={loadLatestPrompt}
              type="button"
            >
              <RefreshCw className="mr-1" />
              Atualizar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="br-card">
      <div className="card-header">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h2 className="text-h2 mb-1">Último Prompt Enviado para LLM</h2>
            <div className="d-flex align-items-center text-muted text-small">
              <Clock className="mr-1" style={{ width: '14px', height: '14px' }} />
              <span>
                {promptData.modified_time ? formatDate(promptData.modified_time) : 'Data não disponível'}
              </span>
              {promptData.file_size && (
                <span className="ml-3">
                  Tamanho: {formatFileSize(promptData.file_size)}
                </span>
              )}
              {promptData.token_usage && promptData.token_usage.prompt_tokens && (
                <span className="ml-3">
                  Tokens enviados: {formatTokenCount(promptData.token_usage.prompt_tokens)}
                </span>
              )}
            </div>
          </div>
          <div className="d-flex gap-2">
            <button
              className="br-button circle"
              onClick={loadLatestPrompt}
              title="Atualizar"
              type="button"
            >
              <RefreshCw />
            </button>
            <button
              className="br-button circle"
              onClick={downloadPrompt}
              title="Baixar prompt"
              type="button"
            >
              <Download />
            </button>
          </div>
        </div>
      </div>

      <div className="card-content">
        <div className="br-scrollbar" style={{ maxHeight: '600px', overflow: 'auto' }}>
          <pre className="prompt-content" style={{
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            fontSize: '14px',
            lineHeight: '1.5',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            margin: 0,
            padding: '1rem',
            backgroundColor: '#f8f9fa',
            border: '1px solid #e9ecef',
            borderRadius: '4px'
          }}>
            {promptData.prompt_content}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default LatestPromptViewer;