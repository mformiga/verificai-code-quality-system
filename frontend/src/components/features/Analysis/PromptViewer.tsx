import React from 'react';
import { Send, Copy, Eye, AlertCircle } from 'lucide-react';
import { useBusinessAnalysisStore } from '@/stores/businessAnalysisStore';

const PromptViewer: React.FC = () => {
  const { lastPromptSent, isAnalyzing } = useBusinessAnalysisStore();

  const handleCopyToClipboard = () => {
    if (lastPromptSent) {
      navigator.clipboard.writeText(lastPromptSent).then(() => {
        // Could add a toast notification here
        alert('Prompt copiado para a área de transferência!');
      }).catch(err => {
        console.error('Failed to copy prompt:', err);
        alert('Erro ao copiar prompt');
      });
    }
  };

  const formatTimestamp = (date: Date): string => {
    return new Date(date).toLocaleString('pt-BR');
  };

  const countTokens = (text: string): number => {
    // Simple token estimation (rough approximation)
    return Math.ceil(text.length / 4);
  };

  if (!lastPromptSent && !isAnalyzing) {
    return (
      <div className="br-tab-panel">
        <div className="br-card">
          <div className="card-content text-center">
            <Send className="w-16 h-16 text-muted mx-auto mb-4" />
            <h4>Nenhum prompt enviado ainda</h4>
            <p>O prompt enviado para a LLM aparecerá aqui após a análise</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="br-tab-panel">
      <div className="br-card">
        <div className="card-header">
          <div className="header-content">
            <h3 className="text-h3">Último Prompt Enviado</h3>
            <p className="text-regular text-muted">
              Prompt enviado para a LLM durante a análise de documentação de negócio
            </p>
          </div>
          <div className="header-actions">
            <button
              className="br-button secondary"
              onClick={handleCopyToClipboard}
              disabled={!lastPromptSent}
            >
              <Copy className="w-4 h-4 mr-2" />
              Copiar
            </button>
          </div>
        </div>

        <div className="card-content">
          {isAnalyzing ? (
            <div className="loading-state">
              <div className="loading-content">
                <div className="br-loading"></div>
                <h4>Enviando prompt para a LLM...</h4>
                <p className="text-muted">Processando solicitação de análise de negócio</p>
              </div>
            </div>
          ) : (
            <>
              {lastPromptSent ? (
                <>
                  {/* Prompt Metadata */}
                  <div className="prompt-metadata mb-4">
                    <div className="metadata-grid">
                      <div className="metadata-item">
                        <span className="metadata-label">Enviado em:</span>
                        <span className="metadata-value">{formatTimestamp(new Date())}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-label">Tokens:</span>
                        <span className="metadata-value">{countTokens(lastPromptSent)}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-label">Caracteres:</span>
                        <span className="metadata-value">{lastPromptSent.length.toLocaleString('pt-BR')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Prompt Content */}
                  <div className="prompt-content">
                    <div className="content-header">
                      <div className="content-title">
                        <Eye className="w-4 h-4 mr-2" />
                        Conteúdo do Prompt
                      </div>
                    </div>

                    <div className="prompt-text-container">
                      <textarea
                        value={lastPromptSent}
                        readOnly
                        className="br-textarea prompt-textarea"
                        rows={20}
                      />
                    </div>
                  </div>

                  {/* Prompt Analysis Info */}
                  <div className="prompt-analysis-info mt-4">
                    <div className="br-message info">
                      <AlertCircle className="w-4 h-4" />
                      <div>
                        <h5>Informações do Prompt</h5>
                        <p className="text-small">
                          Este prompt foi gerado automaticamente com base nos documentos de negócio selecionados
                          e enviado para a LLM para análise semântica e verificação de alinhamento.
                        </p>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <Send className="w-12 h-12 text-muted mx-auto mb-3" />
                  <h5>Nenhum prompt disponível</h5>
                  <p className="text-muted">
                    Inicie uma análise para ver o prompt enviado para a LLM
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PromptViewer;