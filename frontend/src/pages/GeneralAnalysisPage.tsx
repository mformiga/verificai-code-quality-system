import React, { useState, useEffect } from 'react';
import { Download, Upload, Settings, FileText } from 'lucide-react';
import CriteriaList from '@/components/features/Analysis/CriteriaList';
import ProgressTracker from '@/components/features/Analysis/ProgressTracker';
import ResultsTable from '@/components/features/Analysis/ResultsTable';
import ManualEditor from '@/components/features/Analysis/ManualEditor';
import { useUploadStore } from '@/stores/uploadStore';
import { criteriaService } from '@/services/criteriaService';
import './GeneralAnalysisPage.css';

interface CriteriaResult {
  criterion: string;
  assessment: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  confidence: number;
  evidence: Array<{
    code: string;
    language: string;
    filePath: string;
    lineNumbers?: [number, number];
  }>;
  recommendations: string[];
}

const GeneralAnalysisPage: React.FC = () => {
  const { uploadedFiles } = useUploadStore();
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [results, setResults] = useState<CriteriaResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingResult, setEditingResult] = useState<CriteriaResult | null>(null);
  const [activeTab, setActiveTab] = useState<'criteria' | 'results'>('criteria');

  // Carregar critérios cadastrados e mostrar como resultados
  useEffect(() => {
    const loadCriteriaAsResults = async () => {
      try {
        const criteria = await criteriaService.getCriteria();

        // Converter critérios para formato de resultados
        const criteriaAsResults: CriteriaResult[] = criteria.map((criterion, index) => ({
          criterion: criterion.text,
          assessment: `Análise do critério "${criterion.text}" - Aguardando análise completa.`,
          status: 'compliant' as const,
          confidence: 0.8,
          order: criterion.order || index + 1,
          evidence: [],
          recommendations: []
        }));

        setResults(criteriaAsResults);
      } catch (error) {
        console.error('Erro ao carregar critérios como resultados:', error);
      }
    };

    loadCriteriaAsResults();
  }, []);

  // Função para recarregar resultados quando critérios são modificados
  const refreshResults = async () => {
    try {
      const criteria = await criteriaService.getCriteria();

      // Preservar avaliações existentes quando possível
      const updatedResults = criteria.map((criterion, index) => {
        const existingResult = results.find(r => r.criterion === criterion.text);
        return {
          criterion: criterion.text,
          assessment: existingResult?.assessment || `Análise do critério "${criterion.text}" - Aguardando análise completa.`,
          status: existingResult?.status || 'compliant' as const,
          confidence: existingResult?.confidence || 0.8,
          order: criterion.order || index + 1,
          evidence: existingResult?.evidence || [],
          recommendations: existingResult?.recommendations || []
        };
      });

      setResults(updatedResults);
    } catch (error) {
      console.error('Erro ao recarregar resultados:', error);
    }
  };

  const handleStartAnalysis = async (specificCriteria?: string[]) => {
    if (uploadedFiles.length === 0) {
      alert('Por favor, faça upload dos arquivos para análise.');
      return;
    }

    setLoading(true);

    // Mock analysis progress
    const mockAnalysis = {
      id: Date.now().toString(),
      name: specificCriteria ? `Análise de ${specificCriteria.length} Critérios Selecionados` : 'Análise de Critérios Gerais',
      status: 'processing',
      progress: 0,
      startTime: new Date()
    };

    setCurrentAnalysis(mockAnalysis);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setCurrentAnalysis(prev => {
        if (prev && prev.progress < 100) {
          const newProgress = Math.min(prev.progress + 10, 100);
          return { ...prev, progress: newProgress };
        }
        return prev;
      });
    }, 500);

    // Mock criteria for analysis - use specific criteria if provided
    const mockCriteria = specificCriteria || [
      'O código deve seguir convenções de nomenclatura consistentes',
      'Funções e métodos devem ter documentação adequada',
      'O código deve ter tratamento adequado de erros',
      'Variáveis devem ter nomes descritivos e significativos'
    ];

    // Simulate analysis completion
    setTimeout(() => {
      clearInterval(progressInterval);

      const mockResults: CriteriaResult[] = mockCriteria.map((criterion, index) => ({
        criterion,
        assessment: `Análise do critério "${criterion}" revela que o código apresenta boa aderência aos padrões estabelecidos. Foram identificados pontos fortes na implementação e algumas oportunidades de melhoria que podem ser abordadas em futuras refatorações.`,
        status: index % 3 === 0 ? 'compliant' : index % 3 === 1 ? 'partially_compliant' : 'non_compliant',
        confidence: 0.7 + (Math.random() * 0.3),
        order: index + 1,
        evidence: [
          {
            code: '// Exemplo de código analisado\nfunction exampleFunction() {\n  // Implementação\n  return true;\n}',
            language: 'javascript',
            filePath: uploadedFiles[0]?.name || 'example.js',
            lineNumbers: [10, 15]
          }
        ],
        recommendations: [
          'Melhorar a documentação de funções complexas',
          'Adicionar tratamento de erros em pontos críticos',
          'Refatorar funções muito longas para melhor legibilidade'
        ]
      }));

      setResults(mockResults);
      setCurrentAnalysis({
        ...mockAnalysis,
        status: 'completed',
        progress: 100,
        endTime: new Date()
      });
      setLoading(false);
      setActiveTab('results');
    }, 5000);
  };

  const handleEditResult = (criterion: string, result: CriteriaResult) => {
    setEditingResult(result);
  };

  const handleSaveResult = (updatedResult: CriteriaResult) => {
    setResults(prev =>
      prev.map(result =>
        result.criterion === updatedResult.criterion ? updatedResult : result
      )
    );
    setEditingResult(null);
  };

  const handleCancelAnalysis = () => {
    setCurrentAnalysis(null);
    setResults([]);
    setLoading(false);
  };

  const handleReanalyze = (criterion: string) => {
    alert(`Re-analisando critério: ${criterion}`);
    // Implementar lógica de re-análise para o critério específico
  };

  const handleAnalyzeCriterion = (criterion: string) => {
    alert(`Analisando critério específico: ${criterion}`);
    // Implementar lógica de análise para o critério específico
  };

  const handleAnalyzeSelected = (selectedCriteria: string[]) => {
    if (uploadedFiles.length === 0) {
      alert('Por favor, faça upload dos arquivos para análise.');
      return;
    }

    alert(`Analisando ${selectedCriteria.length} critérios selecionados:\n${selectedCriteria.join('\n')}`);
    handleStartAnalysis(selectedCriteria);
  };

  const handleDownloadReport = () => {
    // Generate markdown report
    let report = '# Relatório de Análise de Critérios Gerais\n\n';
    report += `**Data:** ${new Date().toLocaleDateString('pt-BR')}\n`;
    report += `**Arquivos analisados:** ${uploadedFiles.length}\n`;
    report += `**Critérios avaliados:** ${results.length}\n\n`;

    results.forEach(result => {
      report += `## ${result.criterion}\n\n`;
      report += `**Status:** ${result.status}\n`;
      report += `**Confiança:** ${Math.round(result.confidence * 100)}%\n\n`;
      report += `### Avaliação\n${result.assessment}\n\n`;

      if (result.recommendations.length > 0) {
        report += '### Recomendações\n';
        result.recommendations.forEach(rec => {
          report += `- ${rec}\n`;
        });
        report += '\n';
      }
    });

    // Download as file
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analise-criterios-gerais-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="general-analysis-page">
      {/* Page Header */}
      <div className="general-analysis-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h1">Análise de Critérios Gerais</h1>
            <p className="text-regular">
              Configure seus critérios de avaliação, faça upload dos arquivos e execute análises de código baseadas em padrões de qualidade gerais
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="br-tabs" data-tabs="analysis-tabs">
        <nav className="tab-navigation" role="tablist">
          {[
            { id: 'criteria', name: 'Critérios', icon: Settings },
            { id: 'results', name: 'Resultados', icon: FileText }
          ].map((tab) => (
            <button
              key={tab.id}
              className={`tab-item ${activeTab === tab.id ? 'is-active' : ''}`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id as any)}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="br-container">
        {activeTab === 'criteria' && (
          <CriteriaList
            onCriteriaSelect={(selected) => console.log('Selected criteria:', selected)}
            onAnalyzeCriterion={handleAnalyzeCriterion}
            onAnalyzeSelected={handleAnalyzeSelected}
            onCriteriaChange={refreshResults}
          />
        )}

        {activeTab === 'results' && (
          <ResultsTable
            results={results}
            onEditResult={handleEditResult}
            onDownloadReport={handleDownloadReport}
            onReanalyze={handleReanalyze}
          />
        )}

        {/* Analysis Progress - shown in both tabs */}
        {currentAnalysis && (
          <div className="br-card mt-4">
            <div className="card-header">
              <h2 className="text-h2">Executar Análise</h2>
              <p className="text-regular text-muted">
                Inicie a análise de código com base nos critérios configurados
              </p>
            </div>
            <div className="card-content">
              <ProgressTracker
                progress={currentAnalysis.progress}
                status={currentAnalysis.status}
                message="Analisando código com base nos critérios configurados..."
                onCancel={handleCancelAnalysis}
              />
            </div>
          </div>
        )}
      </div>

      {/* Manual Editor Modal */}
      {editingResult && (
        <ManualEditor
          criterion={editingResult.criterion}
          initialResult={editingResult}
          onSave={handleSaveResult}
          onCancel={() => setEditingResult(null)}
        />
      )}
    </div>
  );
};

export default GeneralAnalysisPage;