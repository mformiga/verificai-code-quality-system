import React, { useState, useEffect } from 'react';
import { Download, Upload, Settings, FileText, AlertCircle, Trash2 } from 'lucide-react';
import CriteriaList from '@/components/features/Analysis/CriteriaList';
import ProgressTracker from '@/components/features/Analysis/ProgressTracker';
import ResultsTable from '@/components/features/Analysis/ResultsTable';
import ManualEditor from '@/components/features/Analysis/ManualEditor';
import { useUploadStore } from '@/stores/uploadStore';
import { criteriaService } from '@/services/criteriaService';
import { analysisService, type AnalysisRequest, type AnalysisResponse } from '@/services/analysisService';
import './GeneralAnalysisPage.css';

interface CriteriaResult {
  id?: number;
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
  resultId?: number; // ID do resultado pai no banco de dados
  criterionKey?: string; // Chave do critério original
  criteriaId?: number; // ID numérico único do critério do banco de dados
}

const GeneralAnalysisPage: React.FC = () => {
  const { uploadedFiles } = useUploadStore();
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [results, setResults] = useState<CriteriaResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingResult, setEditingResult] = useState<CriteriaResult | null>(null);
  const [activeTab, setActiveTab] = useState<'criteria' | 'results'>('criteria');
  const [selectedCriteriaIds, setSelectedCriteriaIds] = useState<string[]>([]);
  const [showProgress, setShowProgress] = useState(false);
  const [progress, setProgress] = useState(0);

  // Carregar resultados salvos do banco de dados na inicialização
  useEffect(() => {
    const loadSavedResults = async () => {
      // Não carregar resultados se já houver resultados na tela
      if (results.length > 0) {
        console.log('Já existem resultados na tela, pulando carregamento do banco de dados');
        return;
      }

      try {
        console.log('Carregando resultados salvos do banco de dados...');
        const savedResults = await analysisService.getAnalysisResults();

        if (savedResults.success && savedResults.results && savedResults.results.length > 0) {
          // Carregar todos os critérios para obter o mapeamento de ID numérico
          const allCriteria = await criteriaService.getCriteria();

          // Criar mapeamento de texto do critério para ID numérico
          const criteriaTextToIdMap = new Map<string, number>();
          console.log('🔍 Carregando critérios para mapeamento:', allCriteria.length);
          allCriteria.forEach(criterion => {
            criteriaTextToIdMap.set(criterion.text, criterion.id);
            // Também mapear versões curtas do texto
            const shortText = criterion.text.split(':')[0].trim();
            if (shortText !== criterion.text) {
              criteriaTextToIdMap.set(shortText, criterion.id);
            }
          });

          // Converter resultados salvos para o formato esperado pelo componente
          const formattedResults: CriteriaResult[] = savedResults.results.map((result: any) => {
            // Converter criteria_results do formato salvo para o formato esperado
            const criteriaResultsList: CriteriaResult[] = [];

            if (result.criteria_results && typeof result.criteria_results === 'object') {
              Object.entries(result.criteria_results).forEach(([key, criterionData]: [string, any]) => {
                if (criterionData && criterionData.content) {
                  // Extrair confiança do conteúdo
                  let confidence = 0.8;
                  const confidenceMatch = criterionData.content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
                  if (confidenceMatch) {
                    const confidenceValue = parseFloat(confidenceMatch[2]);
                    confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
                  }

                  // Extrair status do conteúdo
                  let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
                  const content = criterionData.content.toLowerCase();
                  if (content.includes('não atende') || content.includes('não cumpre') || content.includes('viol') || content.includes('defeito')) {
                    status = 'non_compliant';
                  } else if (content.includes('parcialmente') || content.includes('atende parcialmente') || content.includes('precisa melhorar')) {
                    status = 'partially_compliant';
                  }

                  // Tentar encontrar o ID numérico do critério
                  const criterionName = criterionData.name || `Critério ${key}`;
                  const criteriaId = criteriaTextToIdMap.get(criterionName) ||
                                   criteriaTextToIdMap.get(criterionName.split(':')[0].trim());

                  if (!criteriaId) {
                    console.log(`⚠️ Critério não encontrado no mapa: "${criterionName}"`);
                  }

                  criteriaResultsList.push({
                    id: criteriaId || (result.id * 1000 + parseInt(key.replace(/\D/g, ''))), // Usar criteriaId como ID principal
                    criterion: criterionData.name || `Critério ${key}`,
                    assessment: criterionData.content,
                    status: status,
                    confidence: confidence,
                    evidence: [],
                    recommendations: [],
                    resultId: result.id, // Adicionar referência ao ID do resultado pai no banco
                    criterionKey: key, // Adicionar a chave do critério original
                    criteriaId: criteriaId // Adicionar o ID numérico único do critério
                  });
                }
              });
            }

            return criteriaResultsList;
          }).flat();

          console.log(`Carregados ${formattedResults.length} resultados salvos`);
          console.log('Resultados formatados:', formattedResults);
          setResults(formattedResults);
        } else {
          console.log('Nenhum resultado salvo encontrado');
          setResults([]);
        }
      } catch (error) {
        console.error('Erro ao carregar resultados salvos:', error);
        setResults([]);
      }
    };

    loadSavedResults();
  }, []);

  // Função para limpar resultados (mantida para compatibilidade, mas não faz nada)
  const refreshResults = async () => {
    // Não faz mais nada para manter a tela limpa até análise explícita
    console.log('Função refreshResults desativada - mantendo tela limpa');
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
      setCurrentAnalysis((prev: any) => {
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
        id: Date.now() + index, // Gerar ID único
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

  const handleEditResult = (criterion: string, result: Partial<CriteriaResult>) => {
    setEditingResult(result as CriteriaResult);
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

  const handleClearResults = () => {
    if (results.length === 0) return;

    const confirmClear = confirm('Tem certeza que deseja limpar todos os resultados? Esta ação não pode ser desfeita.');
    if (confirmClear) {
      setResults([]);
      console.log('Resultados limpos pelo usuário');
    }
  };

  const handleReanalyze = (criterion: string) => {
    alert(`Re-analisando critério: ${criterion}`);
    // Implementar lógica de re-análise para o critério específico
  };

  const handleDeleteResults = async (selectedIds: number[]) => {
    if (selectedIds.length === 0) return;

    // Mapear os IDs de seleção para os resultados correspondentes
    const selectedResults = results.filter(result => result.id !== undefined && selectedIds.includes(result.id));

    // Separar resultados que estão no banco (têm resultId) dos que são novos (só na tela)
    const databaseResults = selectedResults.filter(result => result.resultId);
    const newResults = selectedResults.filter(result => !result.resultId);

    // Extrair os IDs únicos dos resultados do banco de dados
    const uniqueDatabaseResultIds = [...new Set(databaseResults.map(result => result.resultId).filter(Boolean))];

    if (uniqueDatabaseResultIds.length === 0 && newResults.length === 0) {
      alert('Não foi possível identificar os resultados para exclusão.');
      return;
    }

    let message = `Tem certeza que deseja excluir `;
    if (uniqueDatabaseResultIds.length > 0) {
      message += `${uniqueDatabaseResultIds.length} conjunto(s) de análise do banco de dados`;
    }
    if (newResults.length > 0) {
      if (uniqueDatabaseResultIds.length > 0) message += ' e ';
      message += `${newResults.length} resultado(s) novos`;
    }
    message += '? Esta ação não pode ser desfeita.';

    const confirmDelete = confirm(message);

    if (!confirmDelete) return;

    try {
      // Excluir resultados do banco de dados
      if (uniqueDatabaseResultIds.length > 0) {
        if (uniqueDatabaseResultIds.length === 1) {
          await analysisService.deleteAnalysisResult(uniqueDatabaseResultIds[0]);
        } else {
          await analysisService.deleteMultipleAnalysisResults(uniqueDatabaseResultIds);
        }
      }

      // Remover todos os resultados selecionados da lista local
      setResults(prev => prev.filter(result => result.id === undefined || !selectedIds.includes(result.id)));

      let successMessage = '';
      if (uniqueDatabaseResultIds.length > 0) {
        successMessage += `${uniqueDatabaseResultIds.length} conjunto(s) de análise do banco excluído(s)`;
      }
      if (newResults.length > 0) {
        if (uniqueDatabaseResultIds.length > 0) successMessage += ' e ';
        successMessage += `${newResults.length} resultado(s) novos removido(s)`;
      }
      successMessage += ' com sucesso!';

      alert(successMessage);
    } catch (error) {
      console.error('Erro ao excluir resultados:', error);
      alert(`Erro ao excluir resultados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  };

  const handleAnalyzeCriterion = (criterion: string) => {
    alert(`Analisando critério específico: ${criterion}`);
    // Implementar lógica de análise para o critério específico
  };

  const handleAnalyzeSelected = async (selectedCriteriaIds: string[]) => {
    // Removido check de uploadedFiles - não será usado por enquanto

    if (selectedCriteriaIds.length === 0) {
      alert('Por favor, selecione pelo menos um critério para análise.');
      return;
    }

    try {
      setLoading(true);
      setSelectedCriteriaIds(selectedCriteriaIds);

      // Show simple progress bar at top of page
      setShowProgress(true);
      setProgress(0);
      setActiveTab('results');

      // Simple progress animation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev < 90) {
            return Math.min(prev + Math.random() * 15, 90);
          }
          return prev;
        });
      }, 300);

      // Create analysis request com arquivo de exemplo
      const request: AnalysisRequest = {
        criteria_ids: selectedCriteriaIds,
        file_paths: ['C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\codigo_analise.ts'], // Arquivo correto para análise
        analysis_name: 'Análise de Critérios Selecionados',
        temperature: 0.7,
        max_tokens: 4000
      };

      // Call the new API endpoint
      const response: AnalysisResponse = await analysisService.analyzeSelectedCriteria(request);

      // Clear progress interval
      clearInterval(progressInterval);
      setProgress(100);

      // Criar mapeamento direto dos critérios selecionados para seus IDs numéricos
      const selectedCriteriaMap = new Map<string, number>();
      selectedCriteriaIds.forEach(criteriaId => {
        // Converter "criteria_64" para o ID numérico 64
        const numericId = parseInt(criteriaId.replace('criteria_', ''));
        selectedCriteriaMap.set(criteriaId, numericId);
      });

      // Extract confidence from LLM response content
      const newResults: CriteriaResult[] = Object.entries(response.criteria_results).map(([key, result]) => {
        const content = result.content;

        // Extract confidence from content (look for confidence value)
        let confidence = 0.8;
        const confidenceMatch = content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
        if (confidenceMatch) {
          const confidenceValue = parseFloat(confidenceMatch[2]);
          // If confidence is already in 0.0-1.0 range, use it as is
          // If confidence is in percentage (0-100), divide by 100
          confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
        }

        // Extract status from content based on keywords
        let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
        if (content.toLowerCase().includes('não atende') ||
            content.toLowerCase().includes('não cumpre') ||
            content.toLowerCase().includes('viol') ||
            content.toLowerCase().includes('defeito') ||
            content.toLowerCase().includes('problema')) {
          status = 'non_compliant';
        } else if (content.toLowerCase().includes('parcialmente') ||
                   content.toLowerCase().includes('atende parcialmente') ||
                   content.toLowerCase().includes('precisa melhorar') ||
                   content.toLowerCase().includes('recomenda')) {
          status = 'partially_compliant';
        }

        // Mapear a chave do resultado de volta para o critério original selecionado
        // A chave key aqui corresponde à posição no array de critérios selecionados
        const keyIndex = parseInt(key.replace('criteria_', '')) - 1;
        const originalCriteriaId = selectedCriteriaIds[keyIndex] || selectedCriteriaIds[0];
        const criteriaId = selectedCriteriaMap.get(originalCriteriaId);

        console.log(`🔍 MAPEAMENTO: key=${key}, keyIndex=${keyIndex}, originalCriteriaId=${originalCriteriaId}, criteriaId=${criteriaId}`);
        console.log(`🔍 TODOS OS SELECTED:`, selectedCriteriaIds);
        console.log(`🔍 MAPA COMPLETO:`, Array.from(selectedCriteriaMap.entries()));

        return {
          id: criteriaId || Date.now() + parseInt(key.replace(/\D/g, '')), // Usar o ID numérico do critério se disponível
          criterion: result.name,
          assessment: content,
          status: status,
          confidence: Math.max(0, Math.min(1, confidence)),
          evidence: [],
          recommendations: [],
          resultId: undefined, // Novos resultados não têm ID no banco ainda
          criterionKey: originalCriteriaId, // Usar o ID original do critério selecionado
          criteriaId: criteriaId // Adicionar o ID numérico único do critério
        };
      });

      // Hide progress immediately after successful completion
      setShowProgress(false);
      setProgress(0);

      // Update results: replace only the criteria that were analyzed, keep existing ones
      setResults(prevResults => {
        console.log(`📊 Processando ${prevResults.length} resultados existentes e ${newResults.length} novos resultados`);

        // Log detalhado para depuração
        console.log('🔍 EXISTENTES DETALHADOS:');
        prevResults.forEach((r, i) => console.log(`  ${i}: criteriaId=${r.criteriaId}, criterion="${r.criterion.substring(0, 40)}..."`));

        console.log('🔍 NOVOS DETALHADOS:');
        newResults.forEach((r, i) => console.log(`  ${i}: criteriaId=${r.criteriaId}, criterion="${r.criterion.substring(0, 40)}..."`));

        // Merge results: keep existing results for non-analyzed criteria, update analyzed ones
        const mergedResults = prevResults.map(existingResult => {
          // Check if this criterion was analyzed in the current run using numeric ID
          const analyzedResult = newResults.find(newResult =>
            newResult.criteriaId && existingResult.criteriaId &&
            newResult.criteriaId === existingResult.criteriaId
          );

          if (analyzedResult) {
            console.log(`🔄 ENCONTROU MATCH por ID - Atualizando resultado existente para critério ID ${existingResult.criteriaId}`);
            console.log(`   Existente: "${existingResult.criterion.substring(0, 30)}..."`);
            console.log(`   Novo:      "${analyzedResult.criterion.substring(0, 30)}..."`);
            // Update with new analysis result
            return {
              ...existingResult,
              assessment: analyzedResult.assessment,
              status: analyzedResult.status,
              confidence: analyzedResult.confidence,
              evidence: analyzedResult.evidence,
              recommendations: analyzedResult.recommendations,
              criterionKey: analyzedResult.criterionKey // Update the key as well
            };
          }

          // Se não encontrou por ID, tentar correspondência por texto do critério (fallback)
          if (!existingResult.criteriaId) {
            const textMatch = newResults.find(newResult => {
              const existingText = existingResult.criterion.toLowerCase().trim();
              const newText = newResult.criterion.toLowerCase().trim();

              // Tentar correspondência exata primeiro
              if (existingText === newText) return true;

              // Tentar correspondência por substring (se um contém o outro)
              if (existingText.includes(newText) || newText.includes(existingText)) return true;

              // Tentar correspondência por palavras-chave (remover sufixos como ":", "Princípios", etc.)
              const existingKey = existingText.split(':')[0].replace(/princípios?/i, '').trim();
              const newKey = newText.split(':')[0].replace(/princípios?/i, '').trim();

              return existingKey === newKey || existingKey.includes(newKey) || newKey.includes(existingKey);
            });

            if (textMatch) {
              console.log(`🔄 ENCONTROU MATCH por texto - Atualizando resultado sem ID`);
              console.log(`   Existente: "${existingResult.criterion.substring(0, 30)}..."`);
              console.log(`   Novo:      "${textMatch.criterion.substring(0, 30)}..."`);
              return {
                ...existingResult,
                assessment: textMatch.assessment,
                status: textMatch.status,
                confidence: textMatch.confidence,
                evidence: textMatch.evidence,
                recommendations: textMatch.recommendations,
                criterionKey: textMatch.criterionKey
              };
            }
          }

          // Keep existing result if not analyzed in this run
          return existingResult;
        });

        // Add any new criteria that weren't in the previous results
        // Usar correspondência mais inteligente para evitar duplicações
        const newCriteriaResults = newResults.filter(newResult => {
          // Se tem criteriaId, verificar se já existe nos resultados mesclados
          if (newResult.criteriaId) {
            const alreadyExists = mergedResults.some(existing =>
              existing.criteriaId && existing.criteriaId === newResult.criteriaId
            );
            if (alreadyExists) {
              console.log(`🚫 Ignorando novo resultado com criteriaId ${newResult.criteriaId} - já existe nos mesclados`);
              return false;
            }
          }

          // Verificação adicional por texto para resultados sem criteriaId
          const alreadyExistsByText = mergedResults.some(existing => {
            if (existing.criteriaId === newResult.criteriaId) return true;

            // Comparação flexível de texto
            const existingText = existing.criterion.toLowerCase().trim();
            const newText = newResult.criterion.toLowerCase().trim();

            return existingText === newText ||
                   existingText.includes(newText) ||
                   newText.includes(existingText);
          });

          if (alreadyExistsByText) {
            console.log(`🚫 Ignorando novo resultado por correspondência de texto - "${newResult.criterion.substring(0, 30)}..."`);
            return false;
          }

          return true; // Pode adicionar este resultado
        });

        const existingCriteriaIds = new Set(prevResults.map(r => r.criteriaId).filter(Boolean));
        console.log(`🔍 CRITÉRIOS EXISTENTES: ${Array.from(existingCriteriaIds)}`);
        console.log(`🔍 NOVOS CRITÉRIOS SEM MATCH: ${newCriteriaResults.map(r => ({id: r.criteriaId, name: r.criterion.substring(0, 30)}))}`);
        console.log(`✅ Análise concluída: ${mergedResults.length} atualizados, ${newCriteriaResults.length} novos critérios`);

        return [...mergedResults, ...newCriteriaResults];
      });

      // Show success message
      setTimeout(() => {
        alert(`Análise concluída com sucesso!\n\nModelo: ${response.model_used}\nCritérios analisados: ${response.criteria_count}\nTokens usados: ${response.usage.total_tokens || 'N/A'}`);
      }, 500);

    } catch (error) {
      console.error('Erro na análise:', error);
      alert(`Erro ao realizar análise: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);

      // Keep progress showing on error to indicate failure
      setTimeout(() => {
        setShowProgress(false);
        setProgress(0);
      }, 3000);
    } finally {
      setLoading(false);
    }
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
      {/* Enhanced Progress Bar */}
      {showProgress && (
        <div className="progress-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          zIndex: 9998,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div className="progress-card" style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '24px',
            minWidth: '400px',
            maxWidth: '500px',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)',
            zIndex: 9999
          }}>
            <div className="progress-header" style={{
              textAlign: 'center',
              marginBottom: '20px'
            }}>
              <h3 className="text-h3" style={{
                margin: '0 0 8px 0',
                color: '#1351b4'
              }}>
                Analisando Critérios
              </h3>
              <p className="text-regular text-muted" style={{
                margin: 0,
                fontSize: '14px'
              }}>
                Processando análise com inteligência artificial...
              </p>
            </div>

            <div className="progress-bar-container" style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#e9ecef',
              borderRadius: '4px',
              overflow: 'hidden',
              marginBottom: '16px'
            }}>
              <div
                className="progress-bar-fill"
                style={{
                  height: '100%',
                  backgroundColor: '#1351b4',
                  width: `${progress}%`,
                  transition: 'width 0.3s ease',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div className="progress-text" style={{
              textAlign: 'center',
              fontSize: '14px',
              color: '#6c757d',
              fontWeight: 500
            }}>
              {Math.round(progress)}% concluído
            </div>
          </div>
        </div>
      )}

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
            onAnalyzeSelected={(selected) => handleAnalyzeSelected(selected)}
            onCriteriaChange={refreshResults}
          />
        )}

        {activeTab === 'results' && (
          <div>
            {results.length > 0 && (
              <div className="br-card mb-3">
                <div className="card-content">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <span className="text-regular">
                        Mostrando {results.length} resultado(s) de análise
                      </span>
                    </div>
                    <div className="d-flex gap-2">
                      <button
                        onClick={handleClearResults}
                        className="br-button secondary"
                        title="Limpar todos os resultados"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Limpar Resultados
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <ResultsTable
              results={results}
              onEditResult={handleEditResult}
              onDownloadReport={handleDownloadReport}
              onReanalyze={handleReanalyze}
              onDeleteResults={handleDeleteResults}
            />
          </div>
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