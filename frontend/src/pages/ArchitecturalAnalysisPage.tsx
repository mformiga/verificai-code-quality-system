import React, { useState } from 'react';
import { Upload, Settings, BarChart3, FileText, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import './ArchitecturalAnalysisPage.css';

interface ArchitecturalResult {
  id: string;
  title: string;
  status: 'compliant' | 'warning' | 'non-compliant';
  description: string;
  details: string;
  severity: 'low' | 'medium' | 'high';
}

const ArchitecturalAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'patterns' | 'violations'>('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<ArchitecturalResult[]>([]);

  const mockResults: ArchitecturalResult[] = [
    {
      id: '1',
      title: 'Separação de Camadas',
      status: 'compliant',
      description: 'A separação entre camadas de apresentação, negócio e dados está adequada',
      details: 'MVC: Controller → Service → Repository\nClean Architecture: Entity → Use Case → Controller',
      severity: 'low'
    },
    {
      id: '2',
      title: 'Injeção de Dependências',
      status: 'warning',
      description: 'Detectada dependência direta entre componentes que deveriam ser desacoplados',
      details: 'Arquivo: src/controllers/UserController.ts\nLinha 45: import { Database } from \'../database\'\nSugestão: Usar interface abstrata',
      severity: 'medium'
    },
    {
      id: '3',
      title: 'Padrões de Projeto',
      status: 'non-compliant',
      description: 'Identificada violação do padrão Singleton em classe de configuração',
      details: 'Arquivo: src/config/Database.ts\nLinha 12-25: Implementação direta sem gerenciamento adequado\nRecomendação: Usar factory pattern',
      severity: 'high'
    }
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Simular upload
      console.log('Files uploaded:', files);
    }
  };

  const startAnalysis = () => {
    setIsAnalyzing(true);
    // Simular análise
    setTimeout(() => {
      setResults(mockResults);
      setIsAnalyzing(false);
    }, 3000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle size={20} className="text-green-600" />;
      case 'warning':
        return <AlertTriangle size={20} className="text-yellow-600" />;
      case 'non-compliant':
        return <XCircle size={20} className="text-red-600" />;
      default:
        return <FileText size={20} className="text-gray-600" />;
    }
  };

  return (
    <div className="architectural-analysis-page">
      {/* Header */}
      <div className="architectural-analysis-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h1">Análise de Conformidade Arquitetural</h1>
            <p className="text-regular">
              Avalie a conformidade do seu código com os padrões arquiteturais definidos,
              identifique violações e receba recomendações para melhorar a estrutura do projeto
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Upload Section */}
        <div className="upload-section">
          <div className="br-card">
            <div className="card-content">
              <div className="upload-area">
                <Upload size={64} className="upload-icon" />
                <h3 className="upload-title">Upload dos Arquivos de Código</h3>
                <p className="upload-description">
                  Selecione os arquivos ou diretórios que deseja analisar quanto à conformidade arquitetural
                </p>
                <input
                  type="file"
                  multiple
                  accept=".ts,.js,.py,.java,.cpp,.cs"
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

        {/* Configuration Section */}
        <div className="config-section">
          <div className="br-card">
            <div className="card-content">
              <h3>
                <Settings size={20} style={{ marginRight: '8px' }} />
                Configurações da Análise
              </h3>

              <div className="config-item">
                <label className="config-label">Padrão Arquitetural</label>
                <select className="config-input">
                  <option>MVC (Model-View-Controller)</option>
                  <option>Clean Architecture</option>
                  <option>Hexagonal Architecture</option>
                  <option>Layered Architecture</option>
                  <option>Microservices</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Nível de Rigidez</label>
                <select className="config-input">
                  <option>Baixa (apenas violações críticas)</option>
                  <option>Média (violações importantes)</option>
                  <option>Alta (todas as violações)</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Regras Customizadas</label>
                <textarea
                  className="config-input config-textarea"
                  placeholder="Defina regras específicas para seu projeto..."
                />
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Summary */}
        <div className="analysis-section">
          <div className="br-card">
            <div className="card-content">
              <h3>
                <BarChart3 size={20} style={{ marginRight: '8px' }} />
                Resumo da Análise
              </h3>

              <div className="analysis-item">
                <div className="analysis-item-title">Padrões Identificados</div>
                <p className="analysis-item-description">
                  MVC, Singleton, Factory, Repository Pattern, Dependency Injection
                </p>
              </div>

              <div className="analysis-item">
                <div className="analysis-item-title">Componentes Analisados</div>
                <p className="analysis-item-description">
                  15 controllers, 23 services, 8 repositories, 12 models
                </p>
              </div>

              <div className="analysis-item">
                <div className="analysis-item-title">Métricas de Qualidade</div>
                <p className="analysis-item-description">
                  Acoplamento: Baixo | Coesão: Alta | Complexidade: Moderada
                </p>
              </div>

              <button
                className="action-button primary"
                onClick={startAnalysis}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? 'Analisando...' : 'Iniciar Análise'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {results.length > 0 && (
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
                  className={`results-tab ${activeTab === 'patterns' ? 'active' : ''}`}
                  onClick={() => setActiveTab('patterns')}
                >
                  Padrões
                </button>
                <button
                  className={`results-tab ${activeTab === 'violations' ? 'active' : ''}`}
                  onClick={() => setActiveTab('violations')}
                >
                  Violações
                </button>
              </div>

              <div className="results-content">
                {results.map((result) => (
                  <div key={result.id} className="result-item">
                    <div className="result-header">
                      <div className="result-title">
                        {getStatusIcon(result.status)}
                        <span style={{ marginLeft: '8px' }}>{result.title}</span>
                      </div>
                      <span className={`result-status ${result.status}`}>
                        {result.status === 'compliant' ? 'Conforme' :
                         result.status === 'warning' ? 'Atenção' : 'Não Conforme'}
                      </span>
                    </div>
                    <p className="result-description">{result.description}</p>
                    <div className="result-details">{result.details}</div>
                  </div>
                ))}
              </div>

              <div className="action-buttons">
                <button className="action-button primary">
                  Gerar Relatório
                </button>
                <button className="action-button secondary">
                  Exportar Resultados
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArchitecturalAnalysisPage;