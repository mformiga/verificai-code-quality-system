import React, { useState } from 'react';
import { ChartBar, Download, AlertCircle, CheckCircle, AlertTriangle, Target, TrendingUp, FileText, MessageSquare } from 'lucide-react';
import MarkdownViewer from './MarkdownViewer';
import ReportGenerator from '@/utils/reportGenerator';
import { useBusinessAnalysisStore } from '@/stores/businessAnalysisStore';

interface BusinessDocumentResult {
  id: string;
  documentName: string;
  documentType: 'user-story' | 'epic' | 'business-rule' | 'requirement';
  alignmentScore: number;
  assessment: string;
  gaps: string[];
  recommendations: string[];
  businessImpact: 'high' | 'medium' | 'low';
}

interface BusinessAnalysisResultsProps {
  results: any; // BusinessAnalysisResult | null
  onDownloadReport: () => void;
}

const BusinessAnalysisResults: React.FC<BusinessAnalysisResultsProps> = ({
  results,
  onDownloadReport
}) => {
  const {
    currentAnalysis,
    businessDocuments,
    lastLLMResponse,
    updateResultManually,
    isAnalyzing
  } = useBusinessAnalysisStore();
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'markdown' | 'llm'>('overview');
  if (!results) {
    return (
      <div className="br-tab-panel">
        <div className="br-card">
          <div className="card-content text-center">
            <ChartBar className="w-16 h-16 text-muted mx-auto mb-4" />
            <h4>Nenhuma análise realizada ainda</h4>
            <p>Faça upload dos documentos e inicie a análise para ver os resultados</p>
          </div>
        </div>
      </div>
    );
  }

  // Mock business document results based on the story requirements
  const mockDocumentResults: BusinessDocumentResult[] = [
    {
      id: '1',
      documentName: 'US-001: Login do Usuário',
      documentType: 'user-story',
      alignmentScore: 85,
      assessment: 'O código implementa bem a funcionalidade de login com autenticação segura e validação adequada. Foram encontrados pontos fortes na implementação e pequenas oportunidades de melhoria.',
      gaps: [
        'Falta implementação de autenticação de dois fatores',
        'Não há taxa limite de tentativas de login',
        'Logs de segurança poderiam ser mais detalhados'
      ],
      recommendations: [
        'Implementar 2FA para maior segurança',
        'Adicionar rate limiting para prevenir brute force',
        'Melhorar logs de auditoria de segurança'
      ],
      businessImpact: 'high'
    },
    {
      id: '2',
      documentName: 'Épico-005: Gestão de Pagamentos',
      documentType: 'epic',
      alignmentScore: 92,
      assessment: 'Implementação robusta do sistema de pagamentos com boa cobertura dos casos de uso e tratamento adequado de erros. A arquitetura suporta bem os requisitos de negócio.',
      gaps: [
        'Falta tratamento para moedas internacionais',
        'Não implementado reconciliação automática',
        'Relatórios financeiros poderiam ser mais detalhados'
      ],
      recommendations: [
        'Expandir suporte para múltiplas moedas',
        'Implementar sistema de reconciliação automática',
        'Criar relatórios financeiros avançados'
      ],
      businessImpact: 'high'
    },
    {
      id: '3',
      documentName: 'BR-012: Regra de negócio - Validação de crédito',
      documentType: 'business-rule',
      alignmentScore: 78,
      assessment: 'A validação de crédito está implementada mas poderia ser mais robusta. Alguns edge cases não são tratados adequadamente e as regras de negócio poderiam estar mais centralizadas.',
      gaps: [
        'Não há validação para múltiplos cartões de crédito',
        'Regras de score não são atualizadas dinamicamente',
        'Falta integração com serviços de verificação externos'
      ],
      recommendations: [
        'Implementar validação para múltiplos métodos de pagamento',
        'Criar sistema de score dinâmico',
        'Integrar com bureaus de crédito'
      ],
      businessImpact: 'medium'
    }
  ];

  const getAlignmentScoreColor = (score: number): string => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'danger';
  };

  const getBusinessImpactIcon = (impact: string) => {
    switch (impact) {
      case 'high': return <AlertTriangle className="w-4 h-4 text-danger" />;
      case 'medium': return <AlertCircle className="w-4 h-4 text-warning" />;
      case 'low': return <CheckCircle className="w-4 h-4 text-success" />;
      default: return <Target className="w-4 h-4 text-muted" />;
    }
  };

  const getBusinessImpactLabel = (impact: string): string => {
    switch (impact) {
      case 'high': return 'Alto Impacto';
      case 'medium': return 'Médio Impacto';
      case 'low': return 'Baixo Impacto';
      default: return 'Não Avaliado';
    }
  };

  const getDocumentTypeLabel = (type: string): string => {
    switch (type) {
      case 'user-story': return 'User Story';
      case 'epic': return 'Épico';
      case 'business-rule': return 'Regra de Negócio';
      case 'requirement': return 'Requisito';
      default: return 'Documento';
    }
  };

  const calculateOverallAlignment = (): number => {
    if (mockDocumentResults.length === 0) return 0;
    const total = mockDocumentResults.reduce((sum, doc) => sum + doc.alignmentScore, 0);
    return Math.round(total / mockDocumentResults.length);
  };

  const overallAlignment = calculateOverallAlignment();

  // Enhanced download functions
  const handleDownloadMarkdown = () => {
    if (currentAnalysis && businessDocuments.length > 0) {
      ReportGenerator.downloadMarkdownReport(currentAnalysis, businessDocuments);
    }
  };

  const handleDownloadJSON = () => {
    if (currentAnalysis && businessDocuments.length > 0) {
      ReportGenerator.downloadJSONReport(currentAnalysis, businessDocuments);
    }
  };

  const handleEditAnalysis = (newContent: string) => {
    if (currentAnalysis) {
      updateResultManually({
        ...currentAnalysis,
        overallAssessment: newContent
      });
    }
  };

  // Generate markdown content for LLM response
  const getLLMMarkdownContent = (): string => {
    if (!lastLLMResponse && !currentAnalysis) return '';

    const response = lastLLMResponse || currentAnalysis?.overallAssessment || '';
    if (response) return response;

    // Generate markdown from current analysis if no direct response
    if (currentAnalysis) {
      let markdown = `# Análise de Negócio - Resultados\n\n`;
      markdown += `## Resumo\n\n${currentAnalysis.overallAssessment}\n\n`;
      markdown += `## Score de Alinhamento\n\n${Math.round(currentAnalysis.alignmentScore * 100)}%\n\n`;

      if (currentAnalysis.recommendations.length > 0) {
        markdown += `## Recomendações\n\n`;
        currentAnalysis.recommendations.forEach((rec, index) => {
          markdown += `${index + 1}. ${rec}\n`;
        });
        markdown += '\n';
      }

      if (currentAnalysis.gaps.length > 0) {
        markdown += `## Gaps Identificados\n\n`;
        currentAnalysis.gaps.forEach((gap, index) => {
          markdown += `### ${index + 1}. ${gap.description || gap}\n`;
          markdown += `**Severidade:** ${gap.severity || 'Não especificado'}\n\n`;
        });
      }

      return markdown;
    }

    return '';
  };

  return (
    <div className="br-tab-panel">
      <div className="br-card">
        {/* Tabs Navigation */}
        <div className="border-b">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Visão Geral
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Documentos
            </button>
            <button
              onClick={() => setActiveTab('markdown')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'markdown'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Download className="w-4 h-4 inline mr-2" />
              Relatório Markdown
            </button>
            <button
              onClick={() => setActiveTab('llm')}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'llm'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageSquare className="w-4 h-4 inline mr-2" />
              Resposta LLM
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div>
              <div className="card-header mb-6">
                <div className="header-content">
                  <h3 className="text-h3">Resultados da Análise de Negócio</h3>
                  <p className="text-regular text-muted">
                    Análise de alinhamento entre documentação de negócio e implementação do código
                  </p>
                </div>
                <div className="header-actions flex gap-2">
                  <button className="br-button secondary" onClick={handleDownloadMarkdown}>
                    <Download className="w-4 h-4 mr-2" />
                    Baixar Markdown
                  </button>
                  <button className="br-button secondary" onClick={handleDownloadJSON}>
                    <Download className="w-4 h-4 mr-2" />
                    Baixar JSON
                  </button>
                  {onDownloadReport && (
                    <button className="br-button secondary" onClick={onDownloadReport}>
                      <Download className="w-4 h-4 mr-2" />
                      Relatório Original
                    </button>
                  )}
                </div>
              </div>

        <div className="card-content">
          {/* Overall Summary */}
          <div className="overall-summary mb-4">
            <div className="summary-cards">
              <div className="summary-card">
                <div className="summary-icon">
                  <Target className="w-6 h-6" />
                </div>
                <div className="summary-content">
                  <div className="summary-label">Alinhamento Geral</div>
                  <div className={`summary-value ${getAlignmentScoreColor(overallAlignment)}`}>
                    {overallAlignment}%
                  </div>
                </div>
              </div>

              <div className="summary-card">
                <div className="summary-icon">
                  <ChartBar className="w-6 h-6" />
                </div>
                <div className="summary-content">
                  <div className="summary-label">Documentos Analisados</div>
                  <div className="summary-value">{mockDocumentResults.length}</div>
                </div>
              </div>

              <div className="summary-card">
                <div className="summary-icon">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <div className="summary-content">
                  <div className="summary-label">Gaps Identificados</div>
                  <div className="summary-value">
                    {mockDocumentResults.reduce((sum, doc) => sum + doc.gaps.length, 0)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Document Results */}
          <div className="document-results">
            <h4>Análise por Documento</h4>

            {mockDocumentResults.map((doc) => (
              <div key={doc.id} className="result-card mb-4">
                <div className="result-header">
                  <div className="document-info">
                    <h5 className="document-name">{doc.documentName}</h5>
                    <div className="document-meta">
                      <span className="document-type-badge">{getDocumentTypeLabel(doc.documentType)}</span>
                      <div className="alignment-score">
                        <span className="score-label">Alinhamento:</span>
                        <span className={`score-value ${getAlignmentScoreColor(doc.alignmentScore)}`}>
                          {doc.alignmentScore}%
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="impact-indicator">
                    {getBusinessImpactIcon(doc.businessImpact)}
                    <span className="impact-label">{getBusinessImpactLabel(doc.businessImpact)}</span>
                  </div>
                </div>

                <div className="result-content">
                  {/* Assessment */}
                  <div className="assessment-section">
                    <h6>Avaliação</h6>
                    <p className="assessment-text">{doc.assessment}</p>
                  </div>

                  {/* Gaps */}
                  {doc.gaps.length > 0 && (
                    <div className="gaps-section">
                      <h6>Gaps Identificados</h6>
                      <ul className="gaps-list">
                        {doc.gaps.map((gap, index) => (
                          <li key={index} className="gap-item">
                            <AlertCircle className="w-3 h-3 text-warning" />
                            {gap}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {doc.recommendations.length > 0 && (
                    <div className="recommendations-section">
                      <h6>Recomendações</h6>
                      <ul className="recommendations-list">
                        {doc.recommendations.map((rec, index) => (
                          <li key={index} className="recommendation-item">
                            <CheckCircle className="w-3 h-3 text-success" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

              {/* Original Overview Content */}
              <div className="card-content">
                {/* Overall Summary */}
                <div className="overall-summary mb-4">
                  <div className="summary-cards">
                    <div className="summary-card">
                      <div className="summary-icon">
                        <Target className="w-6 h-6" />
                      </div>
                      <div className="summary-content">
                        <div className="summary-label">Alinhamento Geral</div>
                        <div className={`summary-value ${getAlignmentScoreColor(overallAlignment)}`}>
                          {overallAlignment}%
                        </div>
                      </div>
                    </div>

                    <div className="summary-card">
                      <div className="summary-icon">
                        <ChartBar className="w-6 h-6" />
                      </div>
                      <div className="summary-content">
                        <div className="summary-label">Documentos Analisados</div>
                        <div className="summary-value">{mockDocumentResults.length}</div>
                      </div>
                    </div>

                    <div className="summary-card">
                      <div className="summary-icon">
                        <TrendingUp className="w-6 h-6" />
                      </div>
                      <div className="summary-content">
                        <div className="summary-label">Gaps Identificados</div>
                        <div className="summary-value">
                          {mockDocumentResults.reduce((sum, doc) => sum + doc.gaps.length, 0)}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Document Results Summary */}
                <div className="document-results">
                  <h4>Análise por Documento</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {mockDocumentResults.map((doc) => (
                      <div key={doc.id} className="result-card border rounded-lg p-4">
                        <div className="result-header">
                          <div className="document-info">
                            <h5 className="document-name font-semibold">{doc.documentName}</h5>
                            <div className="document-meta">
                              <span className="document-type-badge">{getDocumentTypeLabel(doc.documentType)}</span>
                              <div className="alignment-score">
                                <span className="score-label">Alinhamento:</span>
                                <span className={`score-value ${getAlignmentScoreColor(doc.alignmentScore)}`}>
                                  {doc.alignmentScore}%
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="impact-indicator">
                            {getBusinessImpactIcon(doc.businessImpact)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Análise Detalhada por Documento</h3>
              {mockDocumentResults.map((doc) => (
                <div key={doc.id} className="result-card mb-6 border rounded-lg p-6">
                  <div className="result-header mb-4">
                    <div className="document-info">
                      <h5 className="document-name">{doc.documentName}</h5>
                      <div className="document-meta">
                        <span className="document-type-badge">{getDocumentTypeLabel(doc.documentType)}</span>
                        <div className="alignment-score">
                          <span className="score-label">Alinhamento:</span>
                          <span className={`score-value ${getAlignmentScoreColor(doc.alignmentScore)}`}>
                            {doc.alignmentScore}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="impact-indicator">
                      {getBusinessImpactIcon(doc.businessImpact)}
                      <span className="impact-label">{getBusinessImpactLabel(doc.businessImpact)}</span>
                    </div>
                  </div>

                  <div className="result-content">
                    {/* Assessment */}
                    <div className="assessment-section mb-4">
                      <h6>Avaliação</h6>
                      <p className="assessment-text">{doc.assessment}</p>
                    </div>

                    {/* Gaps */}
                    {doc.gaps.length > 0 && (
                      <div className="gaps-section mb-4">
                        <h6>Gaps Identificados</h6>
                        <ul className="gaps-list">
                          {doc.gaps.map((gap, index) => (
                            <li key={index} className="gap-item">
                              <AlertCircle className="w-3 h-3 text-warning" />
                              {gap}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Recommendations */}
                    {doc.recommendations.length > 0 && (
                      <div className="recommendations-section">
                        <h6>Recomendações</h6>
                        <ul className="recommendations-list">
                          {doc.recommendations.map((rec, index) => (
                            <li key={index} className="recommendation-item">
                              <CheckCircle className="w-3 h-3 text-success" />
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'markdown' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Relatório em Markdown</h3>
              <p className="text-gray-600 mb-4">
                Visualização e edição do relatório completo em formato Markdown
              </p>
              {currentAnalysis ? (
                <MarkdownViewer
                  content={ReportGenerator.generateMarkdownReport(currentAnalysis, businessDocuments)}
                  title="Relatório de Análise de Negócio"
                  onEdit={handleEditAnalysis}
                  onDownload={(content) => {
                    const blob = new Blob([content], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `relatorio-editado-${new Date().toISOString().split('T')[0]}.md`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  }}
                />
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">Nenhuma análise disponível para gerar o relatório</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'llm' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Resposta da LLM</h3>
              <p className="text-gray-600 mb-4">
                Resposta completa da inteligência artificial com análise semântica
              </p>
              {isAnalyzing ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-500">Processando análise com a LLM...</p>
                </div>
              ) : getLLMMarkdownContent() ? (
                <MarkdownViewer
                  content={getLLMMarkdownContent()}
                  title="Resposta da Análise LLM"
                  showActions={true}
                  onEdit={(content) => {
                    if (currentAnalysis) {
                      updateResultManually({
                        ...currentAnalysis,
                        overallAssessment: content
                      });
                    }
                  }}
                  onDownload={(content) => {
                    const blob = new Blob([content], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `resposta-llm-${new Date().toISOString().split('T')[0]}.md`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  }}
                />
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">Nenhuma resposta da LLM disponível</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Export Actions - Only show on overview tab */}
        {activeTab === 'overview' && (
          <div className="border-t pt-4 mt-6">
            <div className="action-buttons flex gap-2 justify-center">
              <button className="br-button primary" onClick={handleDownloadMarkdown}>
                <Download className="w-4 h-4 mr-2" />
                Gerar Relatório Completo
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BusinessAnalysisResults;