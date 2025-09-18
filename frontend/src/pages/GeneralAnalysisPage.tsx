import React, { useState, useEffect } from 'react';
import { Play, FileText, Settings, Download } from 'lucide-react';
import CriteriaList from '@/components/features/Analysis/CriteriaList';
import ProgressTracker from '@/components/features/Analysis/ProgressTracker';
import ResultsTable from '@/components/features/Analysis/ResultsTable';
import ManualEditor from '@/components/features/Analysis/ManualEditor';
import { useUploadStore } from '@/stores/uploadStore';

interface Criterion {
  id: string;
  text: string;
  active: boolean;
  createdAt: Date;
}

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
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [results, setResults] = useState<CriteriaResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingResult, setEditingResult] = useState<CriteriaResult | null>(null);
  const [activeTab, setActiveTab] = useState<'criteria' | 'analysis' | 'results'>('criteria');

  // Initialize with default criteria
  useEffect(() => {
    const defaultCriteria: Criterion[] = [
      {
        id: 'criteria_1',
        text: 'O código deve seguir convenções de nomenclatura consistentes',
        active: true,
        createdAt: new Date()
      },
      {
        id: 'criteria_2',
        text: 'Funções e métodos devem ter documentação adequada',
        active: true,
        createdAt: new Date()
      },
      {
        id: 'criteria_3',
        text: 'O código deve ter tratamento adequado de erros',
        active: true,
        createdAt: new Date()
      },
      {
        id: 'criteria_4',
        text: 'Variáveis devem ter nomes descritivos e significativos',
        active: true,
        createdAt: new Date()
      }
    ];
    setCriteria(defaultCriteria);
  }, []);

  const handleStartAnalysis = async () => {
    const activeCriteria = criteria.filter(c => c.active);
    if (activeCriteria.length === 0) {
      alert('Por favor, ative pelo menos um critério para análise.');
      return;
    }

    if (uploadedFiles.length === 0) {
      alert('Por favor, faça upload dos arquivos para análise.');
      return;
    }

    setLoading(true);
    setActiveTab('analysis');

    // Mock analysis progress
    const mockAnalysis = {
      id: Date.now().toString(),
      name: 'Análise de Critérios Gerais',
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

    // Simulate analysis completion
    setTimeout(() => {
      clearInterval(progressInterval);

      const mockResults: CriteriaResult[] = activeCriteria.map((criterion, index) => ({
        criterion: criterion.text,
        assessment: `Análise do critério "${criterion.text}" revela que o código apresenta boa aderência aos padrões estabelecidos. Foram identificados pontos fortes na implementação e algumas oportunidades de melhoria que podem ser abordadas em futuras refatorações.`,
        status: index % 3 === 0 ? 'compliant' : index % 3 === 1 ? 'partially_compliant' : 'non_compliant',
        confidence: 0.7 + (Math.random() * 0.3),
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
    setActiveTab('criteria');
  };

  const handleDownloadReport = () => {
    // Generate markdown report
    let report = '# Relatório de Análise de Critérios Gerais\n\n';
    report += `**Data:** ${new Date().toLocaleDateString('pt-BR')}\n`;
    report += `**Arquivos analisados:** ${uploadedFiles.length}\n`;
    report += `**Critérios avaliados:** ${criteria.filter(c => c.active).length}\n\n`;

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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Análise de Critérios Gerais</h1>
        <p className="text-gray-600">
          Configure seus critérios de avaliação e execute análises de código baseadas em padrões de qualidade gerais
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          {[
            { id: 'criteria', name: 'Critérios', icon: Settings },
            { id: 'analysis', name: 'Análise', icon: Play },
            { id: 'results', name: 'Resultados', icon: FileText }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'criteria' && (
          <CriteriaList
            criteria={criteria}
            onCriteriaChange={setCriteria}
            onCriteriaSelect={(selected) => console.log('Selected criteria:', selected)}
          />
        )}

        {activeTab === 'analysis' && (
          <>
            {currentAnalysis ? (
              <ProgressTracker
                progress={currentAnalysis.progress}
                status={currentAnalysis.status}
                message="Analisando código com base nos critérios configurados..."
                onCancel={handleCancelAnalysis}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <Play className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-800 mb-2">
                  Iniciar Análise
                </h3>
                <p className="text-gray-600 mb-6">
                  Configure seus critérios e arquivos, depois inicie a análise para avaliar o código.
                </p>
                <button
                  onClick={handleStartAnalysis}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  {loading ? 'Iniciando...' : 'Iniciar Análise'}
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === 'results' && (
          <ResultsTable
            results={results}
            onEditResult={handleEditResult}
            onDownloadReport={handleDownloadReport}
          />
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