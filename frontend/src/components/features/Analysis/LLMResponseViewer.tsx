import React, { useState } from 'react';
import { MessageSquare, Copy, Edit, Save, X, AlertCircle, CheckCircle } from 'lucide-react';
import { useBusinessAnalysisStore } from '@/stores/businessAnalysisStore';

const LLMResponseViewer: React.FC = () => {
  const { lastLLMResponse, isAnalyzing, updateResultManually } = useBusinessAnalysisStore();
  const [isEditing, setIsEditing] = useState(false);
  const [editedResponse, setEditedResponse] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  const handleCopyToClipboard = () => {
    const responseToCopy = isEditing ? editedResponse : (lastLLMResponse || '');
    if (responseToCopy) {
      navigator.clipboard.writeText(responseToCopy).then(() => {
        // Could add a toast notification here
        alert('Resposta copiada para a área de transferência!');
      }).catch(err => {
        console.error('Failed to copy response:', err);
        alert('Erro ao copiar resposta');
      });
    }
  };

  const handleStartEditing = () => {
    setEditedResponse(lastLLMResponse || '');
    setIsEditing(true);
    setHasChanges(false);
  };

  const handleCancelEditing = () => {
    if (hasChanges) {
      const confirmCancel = confirm('Você tem alterações não salvas. Deseja cancelar a edição?');
      if (!confirmCancel) return;
    }
    setIsEditing(false);
    setEditedResponse('');
    setHasChanges(false);
  };

  const handleSaveEditing = () => {
    if (hasChanges && editedResponse.trim()) {
      // Update the response in the store
      updateResultManually({ overallAssessment: editedResponse });
      setIsEditing(false);
      setHasChanges(false);
      alert('Resposta atualizada com sucesso!');
    }
  };

  const handleResponseChange = (value: string) => {
    setEditedResponse(value);
    setHasChanges(value !== (lastLLMResponse || ''));
  };

  const formatTimestamp = (date: Date): string => {
    return new Date(date).toLocaleString('pt-BR');
  };

  const countTokens = (text: string): number => {
    // Simple token estimation (rough approximation)
    return Math.ceil(text.length / 4);
  };

  // Mock response for demonstration when no response is available
  const mockResponse = `# Análise de Documentação de Negócio

## Resumo da Análise

Foram analisados 3 documentos de negócio para verificar o alinhamento com a implementação atual do código-fonte. A análise revelou uma boa aderência geral aos requisitos, com alguns pontos de atenção identificados.

## Resultados por Documento

### US-001: Login do Usuário
- **Alinhamento:** 85%
- **Status:** Parcialmente Conforme
- **Observações:** Implementação robusta mas falta autenticação de dois fatores

### Épico-005: Gestão de Pagamentos
- **Alinhamento:** 92%
- **Status:** Conforme
- **Observações:** Implementação completa e bem estruturada

### BR-012: Validação de Crédito
- **Alinhamento:** 78%
- **Status:** Parcialmente Conforme
- **Observações:** Funcionalidade básica implementada mas precisa melhorias

## Recomendações Principais

1. Implementar autenticação de dois fatores para maior segurança
2. Adicionar suporte para moedas internacionais no sistema de pagamentos
3. Melhorar validação de crédito com integração a bureaus externos
4. Implementar rate limiting para prevenir ataques de brute force

## Conclusão

O sistema está bem alinhado com os requisitos de negócio, com um score geral de 85%. As oportunidades de melhoria identificadas são principalmente relacionadas a segurança e expansão de funcionalidades.`;

  const responseContent = isEditing ? editedResponse : (lastLLMResponse || mockResponse);

  if (!lastLLMResponse && !isAnalyzing) {
    return (
      <div className="br-tab-panel">
        <div className="br-card">
          <div className="card-content text-center">
            <MessageSquare className="w-16 h-16 text-muted mx-auto mb-4" />
            <h4>Nenhuma resposta recebida ainda</h4>
            <p>A resposta da LLM aparecerá aqui após a análise</p>
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
            <h3 className="text-h3">Última Resposta da LLM</h3>
            <p className="text-regular text-muted">
              Resposta completa da inteligência artificial para a análise de negócio
            </p>
          </div>
          <div className="header-actions">
            {!isEditing && (
              <>
                <button
                  className="br-button secondary"
                  onClick={handleCopyToClipboard}
                  disabled={!responseContent}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copiar
                </button>
                {lastLLMResponse && (
                  <button
                    className="br-button secondary"
                    onClick={handleStartEditing}
                    disabled={isAnalyzing}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar Manualmente
                  </button>
                )}
              </>
            )}

            {isEditing && (
              <>
                <button
                  className="br-button primary"
                  onClick={handleSaveEditing}
                  disabled={!hasChanges || !editedResponse.trim()}
                >
                  <Save className="w-4 h-4 mr-2" />
                  Salvar
                </button>
                <button
                  className="br-button secondary"
                  onClick={handleCancelEditing}
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancelar
                </button>
              </>
            )}
          </div>
        </div>

        <div className="card-content">
          {isAnalyzing ? (
            <div className="loading-state">
              <div className="loading-content">
                <div className="br-loading"></div>
                <h4>Aguardando resposta da LLM...</h4>
                <p className="text-muted">Processando análise de documentação de negócio</p>
              </div>
            </div>
          ) : (
            <>
              {responseContent ? (
                <>
                  {/* Response Metadata */}
                  <div className="response-metadata mb-4">
                    <div className="metadata-grid">
                      <div className="metadata-item">
                        <span className="metadata-label">Recebido em:</span>
                        <span className="metadata-value">{formatTimestamp(new Date())}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-label">Tokens:</span>
                        <span className="metadata-value">{countTokens(responseContent)}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-label">Caracteres:</span>
                        <span className="metadata-value">{responseContent.length.toLocaleString('pt-BR')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Edit Mode Indicator */}
                  {isEditing && (
                    <div className="br-message warning mb-4">
                      <Edit className="w-4 h-4" />
                      <div>
                        <h5>Modo de Edição</h5>
                        <p className="text-small">
                          Você está editando manualmente a resposta da LLM. As alterações serão salvas e substituirão a resposta original.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Response Content */}
                  <div className="response-content">
                    <div className="content-header">
                      <div className="content-title">
                        <MessageSquare className="w-4 h-4 mr-2" />
                        {isEditing ? 'Editando Resposta' : 'Conteúdo da Resposta'}
                      </div>
                      {isEditing && hasChanges && (
                        <div className="changes-indicator">
                          <span className="text-small text-warning">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Alterações não salvas
                          </span>
                        </div>
                      )}
                    </div>

                    {isEditing ? (
                      <div className="response-editor">
                        <textarea
                          value={editedResponse}
                          onChange={(e) => handleResponseChange(e.target.value)}
                          className="br-textarea response-textarea"
                          rows={25}
                          placeholder="Edite a resposta da LLM aqui..."
                        />
                        <div className="editor-footer">
                          <span className="text-small text-muted">
                            {editedResponse.length} caracteres
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="response-viewer">
                        <div className="br-markdown">
                          <pre className="response-text">{responseContent}</pre>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Response Analysis Info */}
                  <div className="response-analysis-info mt-4">
                    <div className="br-message info">
                      <MessageSquare className="w-4 h-4" />
                      <div>
                        <h5>Informações da Resposta</h5>
                        <p className="text-small">
                          Esta resposta foi gerada pela LLM com base na análise semântica dos documentos de negócio.
                          {lastLLMResponse ? ' Você pode editar manualmente esta resposta se necessário.' : ' Esta é uma resposta de demonstração.'}
                        </p>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <MessageSquare className="w-12 h-12 text-muted mx-auto mb-3" />
                  <h5>Nenhuma resposta disponível</h5>
                  <p className="text-muted">
                    Inicie uma análise para ver a resposta completa da LLM
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

export default LLMResponseViewer;