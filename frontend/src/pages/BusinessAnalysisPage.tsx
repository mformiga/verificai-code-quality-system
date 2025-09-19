import React, { useState } from 'react';
import { Upload, TrendingUp, Building2, DollarSign, Users, AlertTriangle, CheckCircle, FileText, Target } from 'lucide-react';
import './BusinessAnalysisPage.css';

interface BusinessRule {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
}

interface BusinessImpact {
  id: string;
  title: string;
  impact: 'high' | 'medium' | 'low';
  description: string;
  details: string[];
  recommendations: string[];
  roi?: string;
  cost?: string;
}

const BusinessAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'compliance' | 'impact'>('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<BusinessImpact[]>([]);

  const businessRules: BusinessRule[] = [
    {
      id: '1',
      title: 'Validação de Dados Sensíveis',
      description: 'Todos os dados pessoais devem ser criptografados e seguir LGPD',
      priority: 'high',
      category: 'Segurança'
    },
    {
      id: '2',
      title: 'Auditoria Financeira',
      description: 'Transações financeiras devem ter rastreabilidade completa',
      priority: 'high',
      category: 'Financeiro'
    },
    {
      id: '3',
      title: 'Performance de Sistema',
      description: 'Tempo de resposta não pode exceder 2 segundos para operações críticas',
      priority: 'medium',
      category: 'Performance'
    },
    {
      id: '4',
      title: 'Backup de Dados',
      description: 'Backup diário automático com retenção de 30 dias',
      priority: 'medium',
      category: 'Operações'
    }
  ];

  const mockResults: BusinessImpact[] = [
    {
      id: '1',
      title: 'Conformidade com LGPD',
      impact: 'high',
      description: 'Identificamos vulnerabilidade crítica no tratamento de dados pessoais que pode resultar em multas de até R$ 50 milhões.',
      details: [
        'Dados pessoais armazenados sem criptografia',
        'Ausência de consentimento explícito dos usuários',
        'Falta de mecanismos de anonimização',
        'Não há política de retenção e exclusão de dados'
      ],
      recommendations: [
        'Implementar criptografia AES-256 para dados sensíveis',
        'Criar mecanismo de consentimento do usuário',
        'Desenvolver política de data retention',
        'Implementar logging de acesso a dados'
      ],
      roi: 'Evita multas de R$ 50M',
      cost: 'R$ 120K estimados'
    },
    {
      id: '2',
      title: 'Otimização de Performance',
      impact: 'medium',
      description: 'Sistema apresenta lentidão em operações críticas, impactando a experiência do usuário e produtividade.',
      details: [
        'Consultas ao banco demoram 3.2 segundos em média',
        'Cache não implementado para operações frequentes',
        'Algoritmos de processamento ineficientes',
        'Falta de monitoramento de performance'
      ],
      recommendations: [
        'Implementar Redis para cache',
        'Otimizar queries e adicionar índices',
        'Refatorar algoritmos críticos',
        'Implementar APM monitoring'
      ],
      roi: 'Aumento de 40% na produtividade',
      cost: 'R$ 85K estimados'
    },
    {
      id: '3',
      title: 'Escalabilidade da Arquitetura',
      impact: 'medium',
      description: 'Arquitetura atual limita o crescimento do negócio e suporte a novos clientes.',
      details: [
        'Monolito difícil de escalar',
        'Bottleneck no processamento de pedidos',
        'Limitações na base de dados',
        'Infraestrutura não preparada para peak loads'
      ],
      recommendations: [
        'Migrar para microservices',
        'Implementar load balancing',
        'Adotar database sharding',
        'Configurar auto-scaling'
      ],
      roi: 'Suporte a 10x mais usuários',
      cost: 'R$ 250K estimados'
    }
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      console.log('Files uploaded:', files);
    }
  };

  const startAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setResults(mockResults);
      setIsAnalyzing(false);
    }, 3000);
  };

  const getPriorityClass = (priority: string) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-medium';
    }
  };

  const getImpactClass = (impact: string) => {
    switch (impact) {
      case 'high': return 'impact-high';
      case 'medium': return 'impact-medium';
      case 'low': return 'impact-low';
      default: return 'impact-medium';
    }
  };

  return (
    <div className="business-analysis-page">
      {/* Header */}
      <div className="business-analysis-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h1">Análise de Impacto de Negócio</h1>
            <p className="text-regular">
              Avalie o impacto do seu código nos objetivos de negócio, identifique oportunidades de melhoria,
              calcule ROI e tome decisões estratégicas baseadas em dados técnicos
            </p>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="br-card">
          <div className="card-content">
            <div className="upload-area">
              <Upload size={64} className="upload-icon" />
              <h3 className="upload-title">Upload dos Arquivos de Projeto</h3>
              <p className="upload-description">
                Selecione os arquivos de código, documentação e requisitos para análise de impacto de negócio
              </p>
              <input
                type="file"
                multiple
                accept=".ts,.js,.py,.md,.txt,.json,.yaml"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload" className="upload-button">
                Selecionar Arquivos
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Business Rules Section */}
        <div className="business-rules-section">
          <div className="br-card">
            <div className="card-content">
              <h3>
                <Building2 size={20} style={{ marginRight: '8px' }} />
                Regras de Negócio
              </h3>

              {businessRules.map((rule) => (
                <div key={rule.id} className="business-rule-item">
                  <div className="business-rule-title">
                    <Target size={16} />
                    {rule.title}
                  </div>
                  <p className="business-rule-description">{rule.description}</p>
                  <span className={`business-rule-priority ${getPriorityClass(rule.priority)}`}>
                    {rule.priority === 'high' ? 'Alta Prioridade' :
                     rule.priority === 'medium' ? 'Média Prioridade' : 'Baixa Prioridade'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Impact Analysis Section */}
        <div className="impact-analysis-section">
          <div className="br-card">
            <div className="card-content">
              <h3>
                <TrendingUp size={20} style={{ marginRight: '8px' }} />
                Métricas de Impacto
              </h3>

              <div className="impact-metric">
                <span className="impact-metric-label">ROI Potencial</span>
                <span className="impact-metric-value">R$ 2.3M</span>
              </div>
              <div className="impact-meter">
                <div className="impact-meter-fill" style={{ width: '85%' }}></div>
              </div>

              <div className="impact-metric">
                <span className="impact-metric-label">Risco de Compliance</span>
                <span className="impact-metric-value">Alto</span>
              </div>
              <div className="impact-meter">
                <div className="impact-meter-fill" style={{ width: '75%', background: '#dc3545' }}></div>
              </div>

              <div className="impact-metric">
                <span className="impact-metric-label">Custo Estimado</span>
                <span className="impact-metric-value">R$ 455K</span>
              </div>
              <div className="impact-meter">
                <div className="impact-meter-fill" style={{ width: '45%', background: '#28a745' }}></div>
              </div>

              <div className="impact-metric">
                <span className="impact-metric-label">Oportunidades</span>
                <span className="impact-metric-value">12 identificadas</span>
              </div>
              <div className="impact-meter">
                <div className="impact-meter-fill" style={{ width: '90%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Project Context Section */}
        <div className="project-context-section">
          <div className="br-card">
            <div className="card-content">
              <h3>
                <Users size={20} style={{ marginRight: '8px' }} />
                Contexto do Projeto
              </h3>

              <div className="context-grid">
                <div className="context-item">
                  <div className="context-item-label">Tamanho do Time</div>
                  <div className="context-item-value">15 desenvolvedores</div>
                </div>
                <div className="context-item">
                  <div className="context-item-label">Usuários Ativos</div>
                  <div className="context-item-value">50,000+</div>
                </div>
                <div className="context-item">
                  <div className="context-item-label">Receita Mensal</div>
                  <div className="context-item-value">R$ 2.5M</div>
                </div>
                <div className="context-item">
                  <div className="context-item-label">Setor</div>
                  <div className="context-item-value">FinTech</div>
                </div>
                <div className="context-item">
                  <div className="context-item-label">Complexidade</div>
                  <div className="context-item-value">Alta</div>
                </div>
                <div className="context-item">
                  <div className="context-item-label">Código Fonte</div>
                  <div className="context-item-value">250k linhas</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="results-section">
          <div className="br-card">
            <div className="card-content">
              <div className="results-tabs">
                <button
                  className={`results-tab ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  Visão Geral
                </button>
                <button
                  className={`results-tab ${activeTab === 'compliance' ? 'active' : ''}`}
                  onClick={() => setActiveTab('compliance')}
                >
                  Conformidade
                </button>
                <button
                  className={`results-tab ${activeTab === 'impact' ? 'active' : ''}`}
                  onClick={() => setActiveTab('impact')}
                >
                  Impacto
                </button>
              </div>

              <div className="action-buttons" style={{ marginBottom: '24px' }}>
                <button
                  className="action-button primary"
                  onClick={startAnalysis}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? 'Analisando...' : 'Iniciar Análise de Negócio'}
                </button>
              </div>

              {results.length > 0 && (
                <div className="analysis-results">
                  {results.map((result) => (
                    <div key={result.id} className="analysis-result-card">
                      <div className="result-header">
                        <h3 className="result-title">{result.title}</h3>
                        <div className="result-impact">
                          <AlertTriangle size={16} />
                          {result.impact === 'high' ? 'Alto Impacto' :
                           result.impact === 'medium' ? 'Médio Impacto' : 'Baixo Impacto'}
                        </div>
                      </div>

                      <p className="result-description">{result.description}</p>

                      <div className="result-details">
                        <h4>Detalhes Técnicos:</h4>
                        <ul>
                          {result.details.map((detail, index) => (
                            <li key={index}>{detail}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="result-recommendations">
                        <h4>Recomendações:</h4>
                        <ul>
                          {result.recommendations.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>

                      <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
                        {result.roi && (
                          <div style={{ flex: 1 }}>
                            <div className="context-item-label">ROI Estimado</div>
                            <div className="context-item-value">{result.roi}</div>
                          </div>
                        )}
                        {result.cost && (
                          <div style={{ flex: 1 }}>
                            <div className="context-item-label">Custo Estimado</div>
                            <div className="context-item-value">{result.cost}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {results.length > 0 && (
                <div className="action-buttons">
                  <button className="action-button primary">
                    <FileText size={16} style={{ marginRight: '8px' }} />
                    Gerar Relatório Executivo
                  </button>
                  <button className="action-button secondary">
                    <DollarSign size={16} style={{ marginRight: '8px' }} />
                    Exportar Análise de ROI
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessAnalysisPage;