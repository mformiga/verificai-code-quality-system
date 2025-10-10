import React from 'react';
import { ChartBar, Download, AlertCircle, CheckCircle, AlertTriangle, Target, TrendingUp } from 'lucide-react';

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

  return (
    <div className="br-tab-panel">
      <div className="br-card">
        <div className="card-header">
          <div className="header-content">
            <h3 className="text-h3">Resultados da Análise de Negócio</h3>
            <p className="text-regular text-muted">
              Análise de alinhamento entre documentação de negócio e implementação do código
            </p>
          </div>
          <div className="header-actions">
            <button className="br-button secondary" onClick={onDownloadReport}>
              <Download className="w-4 h-4 mr-2" />
              Baixar Relatório
            </button>
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

          {/* Export Actions */}
          <div className="export-actions mt-4">
            <div className="action-buttons">
              <button className="br-button primary" onClick={onDownloadReport}>
                <Download className="w-4 h-4 mr-2" />
                Gerar Relatório Completo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessAnalysisResults;