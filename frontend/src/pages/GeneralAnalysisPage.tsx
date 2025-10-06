import React, { useState, useEffect, useCallback } from 'react';
import { Download, Upload, Settings, FileText, AlertCircle, Trash2, RefreshCw, Eye } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import apiClient from '@/services/apiClient';
import CriteriaList from '@/components/features/Analysis/CriteriaList';
import ProgressTracker from '@/components/features/Analysis/ProgressTracker';
import ResultsTable from '@/components/features/Analysis/ResultsTable';
import LatestPromptViewer from '@/components/features/Analysis/LatestPromptViewer';
import LatestResponseViewer from '@/components/features/Analysis/LatestResponseViewer';
import { useUploadStore } from '@/stores/uploadStore';
import { criteriaService } from '@/services/criteriaService';
import { analysisService, type AnalysisRequest, type AnalysisResponse } from '@/services/analysisService';
import Modal from '@/components/common/Modal';
import Alert from '@/components/common/Alert';
import Button from '@/components/common/Button';
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

interface Criterion {
  id: number;
  text: string;
  active: boolean;
  order: number;
}

const GeneralAnalysisPage: React.FC = () => {
  const uploadStore = useUploadStore();

  // Clear upload store on component mount to ensure sync with database
  React.useEffect(() => {
    if (uploadStore.files.length > 0) {
      console.log('🔍 GeneralAnalysisPage montado - limpando upload store para sincronizar com banco de dados');
      uploadStore.clearFiles();
    }

    // Forçar recarga dos paths do banco para garantir sincronização
    reloadDbPaths();
  }, [uploadStore]);

  const uploadedFiles = uploadStore?.files || [];
  const [dbFilePaths, setDbFilePaths] = useState<string[]>([]);

  // Debug: Log onde os arquivos estão vindo
  console.log('🔍 DEBUG - Fontes de arquivos:');
  console.log('  - uploadedFiles (uploadStore):', uploadedFiles);
  console.log('  - uploadedFiles.length:', uploadedFiles.length);
  console.log('  - dbFilePaths:', dbFilePaths);
  console.log('  - dbFilePaths.length:', dbFilePaths.length);

  // Função para recarregar paths do banco de dados
  const reloadDbPaths = async () => {
    try {
      console.log('🔄 Recarregando paths do banco de dados...');

      // Tentar diferentes endpoints
      const endpoints = [
        '/api/v1/file-paths/dev-paths',
        '/public/file-paths',
        '/api/v1/file-paths/test'
      ];

      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint, {
            headers: {
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            console.log(`🔍 Resposta do endpoint ${endpoint}:`, data);

            let paths = [];
            if (data.file_paths && Array.isArray(data.file_paths)) {
              // Verificar se é array de strings ou objetos
              if (typeof data.file_paths[0] === 'string') {
                paths = data.file_paths;
              } else {
                paths = data.file_paths.map((fp: any) => fp.full_path);
              }
            } else if (data.items && Array.isArray(data.items)) {
              paths = data.items.map((fp: any) => fp.full_path);
            }

            setDbFilePaths(paths);
            console.log('✅ Paths recarregados do banco de dados:', paths);
            return paths;
          }
        } catch (endpointError) {
          console.warn(`❌ Erro ao tentar endpoint ${endpoint}:`, endpointError);
        }
      }

      console.warn('❌ Todos os endpoints falharam');
      return [];
    } catch (error) {
      console.error('❌ Erro ao recarregar paths do banco:', error);
      return [];
    }
  };

  // Carregar paths do banco de dados na inicialização
  useEffect(() => {
    reloadDbPaths();
  }, []);

  // Função para obter os file paths para análise de critérios gerais (apenas banco de dados)
  const getAnalysisFilePaths = useCallback(async () => {
    console.log('🔍 getAnalysisFilePaths chamado para análise geral:', {
      uploadedFiles: uploadedFiles.length,
      dbFilePaths: dbFilePaths.length,
      uploadedFilesContent: uploadedFiles,
      dbFilePathsContent: dbFilePaths
    });

    // Para análise de critérios gerais, usar APENAS arquivos do banco de dados
    // Ignorar arquivos do upload store (que são para testes/temporários)
    console.log('🗄️ Análise geral: usando apenas arquivos do banco de dados');

    if (dbFilePaths.length === 0) {
      console.log('🔄 Nenhum path em cache, recarregando do banco...');
      const freshPaths = await reloadDbPaths();
      if (freshPaths.length > 0) {
        console.log('🗄️ Usando paths recarregados do banco:', freshPaths);
        return freshPaths;
      }
    } else {
      console.log('🗄️ Usando paths do banco de dados em cache:', dbFilePaths);
      return dbFilePaths;
    }

    console.log('⚠️ Nenhum path encontrado no banco de dados!');
    return [];
  }, [dbFilePaths]);
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [results, setResults] = useState<CriteriaResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [resultsManuallyCleared, setResultsManuallyCleared] = useState(false);
    const [activeTab, setActiveTab] = useState<'criteria' | 'results' | 'prompt' | 'response'>('criteria');
  const [selectedCriteriaIds, setSelectedCriteriaIds] = useState<string[]>([]);
  const [showProgress, setShowProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [pendingAnalysis, setPendingAnalysis] = useState<string[] | null>(null);
  const [latestTokenInfo, setLatestTokenInfo] = useState<any>(null);

  // Carregar resultados salvos do banco de dados na inicialização
  useEffect(() => {
    const loadSavedResults = async () => {
      // Não carregar resultados se já houver resultados na tela
      if (results.length > 0) {
        console.log('Já existem resultados na tela, pulando carregamento do banco de dados');
        return;
      }

      // Não carregar resultados se o usuário já os excluiu manualmente nesta sessão
      if (resultsManuallyCleared) {
        console.log('Resultados foram excluídos manualmente pelo usuário, pulando carregamento automático');
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

          // Pegar apenas a análise mais recente
          const mostRecentResult = savedResults.results[0]; // Já vem ordenado por timestamp decrescente
          console.log('📊 Usando apenas a análise mais recente:', mostRecentResult.analysis_name);

          // Converter resultado salvo para o formato esperado pelo componente
          const formattedResults: CriteriaResult[] = [];

          if (mostRecentResult.criteria_results && typeof mostRecentResult.criteria_results === 'object') {
            Object.entries(mostRecentResult.criteria_results).forEach(([key, criterionData]: [string, any]) => {
                if (criterionData && criterionData.content) {
                  // Extrair confiança do conteúdo
                  let confidence = 0.8;
                  const confidenceMatch = criterionData.content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
                  if (confidenceMatch) {
                    const confidenceValue = parseFloat(confidenceMatch[2]);
                    confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
                  }

                  // Extrair status do conteúdo usando formato estruturado
                  let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
                  const statusMatch = criterionData.content.match(/\*\*Status:\*\*\s*([^*\n]+)/i);
                  if (statusMatch) {
                    const statusText = statusMatch[1].trim().toLowerCase();
                    console.log(`[DEBUG] Status extracted: "${statusText}" from criterion: ${criterionData.name}`);

                    // Check for "não conforme" first (most specific)
                    if (statusText === 'não conforme' || statusText === 'nao conforme' || statusText.startsWith('não conforme') || statusText.startsWith('nao conforme')) {
                      status = 'non_compliant';
                    } else if (statusText === 'parcialmente conforme' || statusText.startsWith('parcialmente conforme')) {
                      status = 'partially_compliant';
                    } else if (statusText === 'conforme' || statusText.startsWith('conforme')) {
                      status = 'compliant';
                    } else {
                      // Fallback: check for contains (less precise)
                      if (statusText.includes('não conforme') || statusText.includes('nao conforme')) {
                        status = 'non_compliant';
                      } else if (statusText.includes('parcialmente conforme')) {
                        status = 'partially_compliant';
                      } else if (statusText.includes('conforme') && !statusText.includes('não') && !statusText.includes('nao')) {
                        status = 'compliant';
                      }
                    }
                    console.log(`[DEBUG] Status mapped to: ${status} for criterion: ${criterionData.name}`);
                  } else {
                    // Fallback para busca por palavra-chave se formato estruturado não for encontrado
                    const content = criterionData.content.toLowerCase();
                    console.log(`[DEBUG] No structured status found, using content search for criterion: ${criterionData.name}`);

                    if (content.includes('não atende') || content.includes('não cumpre') || content.includes('viol') || content.includes('defeito')) {
                      status = 'non_compliant';
                    } else if (content.includes('parcialmente') || content.includes('atende parcialmente') || content.includes('precisa melhorar')) {
                      status = 'partially_compliant';
                    }
                    console.log(`[DEBUG] Fallback status mapped to: ${status} for criterion: ${criterionData.name}`);
                  }

                  // Tentar encontrar o ID numérico do critério
                  const criterionNameFromDB = criterionData.name || `Critério ${key}`;
                  const criteriaId = criteriaTextToIdMap.get(criterionNameFromDB) ||
                                   criteriaTextToIdMap.get(criterionNameFromDB.split(':')[0].trim());

                  // Encontrar o critério correspondente para obter o texto original
                  const matchingCriterion = allCriteria.find(c => c.id === criteriaId);

                  // SEMPRE usar o texto original do critério se encontrado, senão usar o do banco
                  const finalCriterionText = matchingCriterion ? matchingCriterion.text : criterionNameFromDB;

                  if (!criteriaId) {
                    console.log(`⚠️ Critério não encontrado no mapa: "${criterionNameFromDB}"`);
                  }

                  if (matchingCriterion) {
                    console.log(`✅ Critério encontrado no mapa: "${criterionNameFromDB}" -> "${matchingCriterion.text}"`);
                  }

                  formattedResults.push({
                    id: criteriaId || (mostRecentResult.id * 1000 + parseInt(key.replace(/\D/g, ''))), // Usar criteriaId como ID principal
                    criterion: finalCriterionText, // Usar texto original do critério quando disponível
                    assessment: criterionData.content,
                    status: status,
                    confidence: confidence,
                    evidence: [],
                    recommendations: [],
                    resultId: mostRecentResult.id, // Adicionar referência ao ID do resultado pai no banco
                    criterionKey: key, // Adicionar a chave do critério original
                    criteriaId: criteriaId // Adicionar o ID numérico único do critério
                  });
                }
            });
          }

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

  // Função para carregar informações de tokens mais recentes
  const loadLatestTokenInfo = async () => {
    try {
      // Tenta carregar tanto informações do prompt quanto da resposta
      const [promptData, responseData] = await Promise.all([
        analysisService.getLatestPrompt().catch(() => null),
        analysisService.getLatestResponse().catch(() => null)
      ]);

      const tokenInfo: any = {};

      if (promptData?.token_usage) {
        tokenInfo.prompt = promptData.token_usage;
      }

      if (responseData?.token_usage) {
        tokenInfo.response = responseData.token_usage;
      }

      if (Object.keys(tokenInfo).length > 0) {
        setLatestTokenInfo(tokenInfo);
      }
    } catch (error) {
      console.error('Erro ao carregar informações de tokens:', error);
    }
  };

  // Carregar informações de tokens quando mudar para abas de prompt/response
  useEffect(() => {
    if (activeTab === 'prompt' || activeTab === 'response') {
      loadLatestTokenInfo();
    }
  }, [activeTab]);

  // Função para formatar contagem de tokens
  const formatTokenCount = (tokens: number) => {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
    return tokens.toString();
  };

  const handleStartAnalysis = async (specificCriteria?: string[]) => {
    const filePaths = await getAnalysisFilePaths();
    if (filePaths.length === 0) {
      alert('Nenhum arquivo encontrado para análise. Por favor, faça upload dos arquivos primeiro.');
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
            filePath: filePaths[0] || uploadedFiles[0]?.name || 'example.js',
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

  const handleReanalyze = async (criterion: string) => {
    try {
      // Encontrar o critério nos resultados existentes para obter o ID
      const existingResult = results.find(r => r.criterion === criterion || r.criterion.includes(criterion) || criterion.includes(r.criterion));

      if (!existingResult) {
        alert('Critério não encontrado nos resultados.');
        return;
      }

      // Obter o ID do critério para reanálise
      const criteriaId = existingResult.criteriaId || existingResult.id;
      const criteriaKey = existingResult.criterionKey || `criteria_${criteriaId}`;

      if (!criteriaId) {
        alert('Não foi possível identificar o ID do critério para reanálise.');
        return;
      }

      setLoading(true);

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

      // Obter file paths para análise
      const filePaths = await getAnalysisFilePaths();

      if (filePaths.length === 0) {
        // Limpar estado de progresso antes de retornar
        clearInterval(progressInterval);
        setShowProgress(false);
        setProgress(0);
        setActiveTab('criteria');
        setLoading(false);
        alert('Nenhum arquivo encontrado para análise. Por favor, faça upload dos arquivos primeiro.');
        return;
      }

      // Create analysis request para reanálise do critério específico
      const request: AnalysisRequest = {
        criteria_ids: [criteriaKey],
        file_paths: filePaths,
        analysis_name: `Reanálise do Critério: ${criterion}`,
        temperature: 0.7,
        max_tokens: 4000
      };

      // Call the API endpoint
      const response: AnalysisResponse = await analysisService.analyzeSelectedCriteria(request);

      // Clear progress interval
      clearInterval(progressInterval);
      setProgress(100);

      // Process the single result
      const newResultEntry = Object.entries(response.criteria_results)[0];
      if (!newResultEntry) {
        throw new Error('Nenhum resultado retornado da reanálise');
      }

      const [key, result] = newResultEntry;
      const content = result.content;

      // Extract confidence from content
      let confidence = 0.8;
      const confidenceMatch = content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
      if (confidenceMatch) {
        const confidenceValue = parseFloat(confidenceMatch[2]);
        confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
      }

      // Extract status from content using formato estruturado primeiro
      let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
      const statusMatch = content.match(/\*\*Status:\*\*\s*([^*\n]+)/i);
      if (statusMatch) {
        const statusText = statusMatch[1].trim().toLowerCase();
        console.log(`[DEBUG] Status extracted from structured format: "${statusText}"`);

        // Check for "não conforme" first (most specific)
        if (statusText === 'não conforme' || statusText === 'nao conforme' || statusText.startsWith('não conforme') || statusText.startsWith('nao conforme')) {
          status = 'non_compliant';
        } else if (statusText === 'parcialmente conforme' || statusText.startsWith('parcialmente conforme')) {
          status = 'partially_compliant';
        } else if (statusText === 'conforme' || statusText.startsWith('conforme')) {
          status = 'compliant';
        } else {
          // Fallback: check for contains (less precise)
          if (statusText.includes('não conforme') || statusText.includes('nao conforme')) {
            status = 'non_compliant';
          } else if (statusText.includes('parcialmente conforme')) {
            status = 'partially_compliant';
          } else if (statusText.includes('conforme') && !statusText.includes('não') && !statusText.includes('nao')) {
            status = 'compliant';
          }
        }
        console.log(`[DEBUG] Status mapped to: ${status}`);
      } else {
        // Fallback para busca por palavra-chave se formato estruturado não for encontrado
        console.log(`[DEBUG] No structured status found, using content search`);
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
        console.log(`[DEBUG] Fallback status mapped to: ${status}`);
      }

      // Create the new result object
      const updatedResult: CriteriaResult = {
        id: criteriaId,
        criterion: criterion, // Usar o título original do critério em vez do LLM response.name
        assessment: content,
        status: status,
        confidence: Math.max(0, Math.min(1, confidence)),
        evidence: [],
        recommendations: [],
        resultId: existingResult.resultId, // Manter o mesmo ID do banco de dados
        criterionKey: criteriaKey,
        criteriaId: criteriaId
      };

      // Hide progress immediately after successful completion
      setShowProgress(false);
      setProgress(0);

      // Update results: replace only the reanalyzed criterion
      setResults(prevResults => {
        return prevResults.map(existingResult => {
          // Match by criteriaId or by criterion name
          if ((existingResult.criteriaId && existingResult.criteriaId === criteriaId) ||
              (existingResult.criterion === criterion) ||
              (existingResult.criterion.includes(criterion)) ||
              (criterion.includes(existingResult.criterion))) {

            console.log(`🔄 REANÁLISE - Atualizando resultado para critério: ${criterion}`);
            console.log(`   Antigo: "${existingResult.assessment.substring(0, 50)}..."`);
            console.log(`   Novo:  "${content.substring(0, 50)}..."`);

            // Return updated result
            return {
              ...existingResult,
              assessment: content,
              status: status,
              confidence: Math.max(0, Math.min(1, confidence)),
              criterionKey: criteriaKey
            };
          }

          // Keep other results unchanged
          return existingResult;
        });
      });

      console.log(`✅ Reanálise concluída com sucesso para: ${criterion}`);

    } catch (error) {
      console.error('Erro na reanálise do critério:', error);
      alert('Erro ao reanalisar o critério. Por favor, tente novamente.');
      setShowProgress(false);
      setProgress(0);
    } finally {
      setLoading(false);
    }
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

      // Marcar que os resultados foram limpos manualmente para evitar recarregamento automático
      setResultsManuallyCleared(true);

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

  const handleAnalyzeCriterion = async (criterionObj: Criterion) => {
    try {
      console.log('🔍 DEBUG handleAnalyzeCriterion:');
      console.log('  - criterionObj recebido:', criterionObj);

      const criteriaKey = `criteria_${criterionObj.id}`;
      console.log('  - criteriaKey gerado:', criteriaKey);

      setLoading(true);

      // Excluir todos os resultados anteriores antes de iniciar nova análise
      try {
        console.log('🗑️ Excluindo todos os resultados anteriores antes da nova análise...');
        await analysisService.deleteAllAnalysisResults();
        console.log('✅ Todos os resultados anteriores excluídos com sucesso');
      } catch (deleteError) {
        console.warn('⚠️ Erro ao excluir resultados anteriores, continuando com análise:', deleteError);
      }

      // Limpar resultados anteriores para evitar misturar com nova análise
      setResults([]);
      // Resetar a flag de exclusão manual pois estamos iniciando uma nova análise
      setResultsManuallyCleared(false);

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

      // Obter file paths para análise
      const filePaths = await getAnalysisFilePaths();

      if (filePaths.length === 0) {
        // Limpar estado de progresso antes de retornar
        clearInterval(progressInterval);
        setShowProgress(false);
        setProgress(0);
        setActiveTab('criteria');
        setLoading(false);
        alert('Nenhum arquivo encontrado para análise. Por favor, faça upload dos arquivos primeiro.');
        return;
      }

      // Create analysis request para análise do critério específico
      const request: AnalysisRequest = {
        criteria_ids: [criteriaKey],
        file_paths: filePaths,
        analysis_name: `Análise do Critério: ${criterionObj.text}`,
        temperature: 0.7,
        max_tokens: 4000
      };

      // Call the API endpoint
      const response: AnalysisResponse = await analysisService.analyzeSelectedCriteria(request);

      // Clear progress interval
      clearInterval(progressInterval);
      setProgress(100);

      // Process the single result
      const newResultEntry = Object.entries(response.criteria_results)[0];
      if (!newResultEntry) {
        throw new Error('Nenhum resultado retornado da análise');
      }

      const [key, result] = newResultEntry;
      const content = result.content;

      // Extract confidence from content
      let confidence = 0.8;
      const confidenceMatch = content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
      if (confidenceMatch) {
        const confidenceValue = parseFloat(confidenceMatch[2]);
        confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
      }

      // Extract status from content using formato estruturado primeiro
      let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
      const statusMatch = content.match(/\*\*Status:\*\*\s*([^*\n]+)/i);
      if (statusMatch) {
        const statusText = statusMatch[1].trim().toLowerCase();
        console.log(`[DEBUG] Status extracted from structured format: "${statusText}"`);

        // Check for "não conforme" first (most specific)
        if (statusText === 'não conforme' || statusText === 'nao conforme' || statusText.startsWith('não conforme') || statusText.startsWith('nao conforme')) {
          status = 'non_compliant';
        } else if (statusText === 'parcialmente conforme' || statusText.startsWith('parcialmente conforme')) {
          status = 'partially_compliant';
        } else if (statusText === 'conforme' || statusText.startsWith('conforme')) {
          status = 'compliant';
        } else {
          // Fallback: check for contains (less precise)
          if (statusText.includes('não conforme') || statusText.includes('nao conforme')) {
            status = 'non_compliant';
          } else if (statusText.includes('parcialmente conforme')) {
            status = 'partially_compliant';
          } else if (statusText.includes('conforme') && !statusText.includes('não') && !statusText.includes('nao')) {
            status = 'compliant';
          }
        }
        console.log(`[DEBUG] Status mapped to: ${status}`);
      } else {
        // Fallback para busca por palavra-chave se formato estruturado não for encontrado
        console.log(`[DEBUG] No structured status found, using content search`);
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
        console.log(`[DEBUG] Fallback status mapped to: ${status}`);
      }

      // Create the new result object - sempre usar o texto original do critério
      const newResult: CriteriaResult = {
        id: criterionObj.id,
        criterion: criterionObj.text, // Usar SEMPRE o texto original do critério
        assessment: content,
        status: status,
        confidence: Math.max(0, Math.min(1, confidence)),
        evidence: [],
        recommendations: [],
        resultId: response.db_result_id, // Usar o ID do resultado salvo no banco
        criterionKey: criteriaKey,
        criteriaId: criterionObj.id
      };

      console.log('🔍 DEBUG handleAnalyzeCriterion - criação do resultado:');
      console.log('  - criterionObj.text (original):', criterionObj.text);
      console.log('  - result.name (LLM):', result.name);
      console.log('  - newResult.criterion (usado):', newResult.criterion);
      console.log('  - result.name do backend:', result.name);

      // IMPORTANTE: Usar o nome enviado pelo backend se estiver disponível e for diferente do ID
      if (result.name && result.name !== key) {
        newResult.criterion = result.name;
        console.log('  - Usando nome do backend:', newResult.criterion);
      }

      // Hide progress immediately after successful completion
      setShowProgress(false);
      setProgress(0);

      // Update results: check if criterion already exists and update, or add new
      setResults(prevResults => {
        const existingIndex = prevResults.findIndex(r =>
          (r.criteriaId && r.criteriaId === criterionObj.id) ||
          (r.criterion === criterionObj.text) ||
          (r.criterion.includes(criterionObj.text)) ||
          (criterionObj.text.includes(r.criterion))
        );

        if (existingIndex >= 0) {
          console.log(`🔄 ANÁLISE INDIVIDUAL - Atualizando resultado existente para: ${criterionObj.text}`);
          const updatedResults = [...prevResults];
          updatedResults[existingIndex] = {
            ...prevResults[existingIndex],
            assessment: content,
            status: status,
            confidence: Math.max(0, Math.min(1, confidence)),
            criterionKey: criteriaKey
          };
          return updatedResults;
        } else {
          console.log(`➕ ANÁLISE INDIVIDUAL - Adicionando novo resultado para: ${criterionObj.text}`);
          return [...prevResults, newResult];
        }
      });

      console.log(`✅ Análise individual concluída com sucesso para: ${criterionObj.text}`);

    } catch (error) {
      console.error('Erro na análise do critério:', error);
      alert('Erro ao analisar o critério. Por favor, tente novamente.');
      setShowProgress(false);
      setProgress(0);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeSelected = async (selectedCriteriaIds: string[]) => {
    // Removido check de uploadedFiles - não será usado por enquanto

    if (selectedCriteriaIds.length === 0) {
      alert('Por favor, selecione pelo menos um critério para análise.');
      return;
    }

    // Verificar se há resultados anteriores e mostrar confirmação
    if (results.length > 0) {
      setPendingAnalysis(selectedCriteriaIds);
      setConfirmModalOpen(true);
      return;
    }

    // Se não há resultados anteriores, prosseguir diretamente
    executeAnalysis(selectedCriteriaIds);
  };

  const executeAnalysis = async (selectedCriteriaIds: string[]) => {
    try {
      setLoading(true);
      setSelectedCriteriaIds(selectedCriteriaIds);

      // Excluir todos os resultados anteriores antes de iniciar nova análise
      try {
        console.log('🗑️ Excluindo todos os resultados anteriores antes da nova análise...');
        await analysisService.deleteAllAnalysisResults();
        console.log('✅ Todos os resultados anteriores excluídos com sucesso');
      } catch (deleteError) {
        console.warn('⚠️ Erro ao excluir resultados anteriores, continuando com análise:', deleteError);
      }

      // Limpar resultados anteriores para evitar misturar com nova análise
      setResults([]);
      // Resetar a flag de exclusão manual pois estamos iniciando uma nova análise
      setResultsManuallyCleared(false);

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

      // Obter file paths para análise
      const filePaths = await getAnalysisFilePaths();

      if (filePaths.length === 0) {
        // Limpar estado de progresso antes de retornar
        clearInterval(progressInterval);
        setShowProgress(false);
        setProgress(0);
        setActiveTab('criteria');
        setLoading(false);
        alert('Nenhum arquivo encontrado para análise. Por favor, faça upload dos arquivos primeiro.');
        return;
      }

      // Create analysis request com os arquivos uploaded
      const request: AnalysisRequest = {
        criteria_ids: selectedCriteriaIds,
        file_paths: filePaths,
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

      // Carregar todos os critérios para obter os textos originais
      const allCriteriaData = await criteriaService.getCriteria();

      // Extract confidence from LLM response content
      const newResults: CriteriaResult[] = Object.entries(response.criteria_results).map(([key, result]) => {
        const content = result.content;

        console.log('🔍 FRONTEND: Processando resultado:', { key, result, name: result.name });

        // Extract confidence from content (look for confidence value)
        let confidence = 0.8;
        const confidenceMatch = content.match(/(confiança|confidence)[^\d]*(\d+(?:\.\d+)?)/i);
        if (confidenceMatch) {
          const confidenceValue = parseFloat(confidenceMatch[2]);
          // If confidence is already in 0.0-1.0 range, use it as is
          // If confidence is in percentage (0-100), divide by 100
          confidence = confidenceValue > 1.0 ? Math.min(confidenceValue / 100, 1.0) : Math.min(confidenceValue, 1.0);
        }

        // Extract status from content using formato estruturado primeiro
        let status: 'compliant' | 'partially_compliant' | 'non_compliant' = 'compliant';
        const statusMatch = content.match(/\*\*Status:\*\*\s*([^*\n]+)/i);
        if (statusMatch) {
          const statusText = statusMatch[1].trim().toLowerCase();
          console.log(`[DEBUG] Status extracted from structured format: "${statusText}"`);

          // Check for "não conforme" first (most specific)
          if (statusText === 'não conforme' || statusText === 'nao conforme' || statusText.startsWith('não conforme') || statusText.startsWith('nao conforme')) {
            status = 'non_compliant';
          } else if (statusText === 'parcialmente conforme' || statusText.startsWith('parcialmente conforme')) {
            status = 'partially_compliant';
          } else if (statusText === 'conforme' || statusText.startsWith('conforme')) {
            status = 'compliant';
          } else {
            // Fallback: check for contains (less precise)
            if (statusText.includes('não conforme') || statusText.includes('nao conforme')) {
              status = 'non_compliant';
            } else if (statusText.includes('parcialmente conforme')) {
              status = 'partially_compliant';
            } else if (statusText.includes('conforme') && !statusText.includes('não') && !statusText.includes('nao')) {
              status = 'compliant';
            }
          }
          console.log(`[DEBUG] Status mapped to: ${status}`);
        } else {
          // Fallback para busca por palavra-chave se formato estruturado não for encontrado
          console.log(`[DEBUG] No structured status found, using content search`);
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
          console.log(`[DEBUG] Fallback status mapped to: ${status}`);
        }

        // Mapear a chave do resultado de volta para o critério original selecionado
        // A chave key aqui corresponde à posição no array de critérios selecionados
        const keyIndex = parseInt(key.replace('criteria_', '')) - 1;
        const originalCriteriaId = selectedCriteriaIds[keyIndex] || selectedCriteriaIds[0];
        const criteriaId = selectedCriteriaMap.get(originalCriteriaId);

        console.log(`🔍 MAPEAMENTO: key=${key}, keyIndex=${keyIndex}, originalCriteriaId=${originalCriteriaId}, criteriaId=${criteriaId}`);
        console.log(`🔍 TODOS OS SELECTED:`, selectedCriteriaIds);
        console.log(`🔍 MAPA COMPLETO:`, Array.from(selectedCriteriaMap.entries()));

        // Encontrar o critério correspondente para obter o texto original
        let matchingCriterion = allCriteriaData.find(c => c.id === criteriaId);

        // Se não encontrou por ID, tentar encontrar pelo criteriaKey
        if (!matchingCriterion && originalCriteriaId) {
          const numericId = parseInt(originalCriteriaId.replace('criteria_', ''));
          matchingCriterion = allCriteriaData.find(c => c.id === numericId);
        }

        // SEMPRE usar o texto original do critério do banco de dados
        let criterionText = matchingCriterion ? matchingCriterion.text : `Critério ${criteriaId || key}`;
        if (!matchingCriterion && criteriaId) {
          // Se temos o ID mas não encontramos o critério, usar um nome mais descritivo
          criterionText = `Critério ID ${criteriaId}`;
        }

        console.log(`🔍 Mapeamento de critério: key=${key}, criteriaId=${criteriaId}, matchingCriterion=${matchingCriterion ? 'SIM' : 'NÃO'}, textoFinal="${criterionText}"`);
        console.log(`🔍 result.name do backend: "${result.name}"`);

        // IMPORTANTE: Usar o nome enviado pelo backend se estiver disponível, pois já foi corrigido lá
        const finalCriterionText = result.name && result.name !== key ? result.name : criterionText;

        console.log(`🔍 Texto final usado: "${finalCriterionText}"`);

        return {
          id: criteriaId || Date.now() + parseInt(key.replace(/\D/g, '')), // Usar o ID numérico do critério se disponível
          criterion: finalCriterionText, // Usar nome corrigido do backend ou fazer fallback para mapeamento
          assessment: content,
          status: status,
          confidence: Math.max(0, Math.min(1, confidence)),
          evidence: [],
          recommendations: [],
          resultId: response.db_result_id, // Usar o ID do resultado salvo no banco
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

  const handleConfirmAnalysis = () => {
    setConfirmModalOpen(false);
    if (pendingAnalysis) {
      executeAnalysis(pendingAnalysis);
      setPendingAnalysis(null);
    }
  };

  const handleCancelModalAnalysis = () => {
    setConfirmModalOpen(false);
    setPendingAnalysis(null);
  };

  const [allCriteria, setAllCriteria] = useState<any[]>([]);
  const [fullCriteriaText, setFullCriteriaText] = useState<Record<string, string>>({});

  const getFullCriterionText = (criterionName: string) => {
    // Tentar encontrar correspondência exata primeiro
    if (fullCriteriaText[criterionName]) {
      return fullCriteriaText[criterionName];
    }

    // Tentar encontrar por substring
    const matchingCriterion = allCriteria.find(criterion =>
      criterion.text.includes(criterionName) || criterionName.includes(criterion.text.split(':')[0])
    );

    return matchingCriterion ? matchingCriterion.text : criterionName;
  };

  const loadAllCriteria = async () => {
    try {
      const criteria = await criteriaService.getCriteria();
      setAllCriteria(criteria);

      // Criar mapeamento de texto completo
      const textMapping: Record<string, string> = {};
      criteria.forEach(criterion => {
        textMapping[criterion.text] = criterion.text;
      });
      setFullCriteriaText(textMapping);
    } catch (error) {
      console.error('Erro ao carregar critérios:', error);
    }
  };

  
  useEffect(() => {
    loadAllCriteria();
  }, []);

  const generateReportContent = () => {
    const currentDate = new Date().toLocaleDateString('pt-BR');
    const currentTime = new Date().toLocaleTimeString('pt-BR');

    let content = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office'
            xmlns:w='urn:schemas-microsoft-com:office:word'
            xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <meta charset='utf-8'>
        <title>Relatório de Análise de Código</title>
        <style>
          @page Section1 {
            size: 21.0cm 29.7cm;
            margin: 1.2cm 1.5cm 1.2cm 1.5cm;
            mso-header-margin: 1cm;
            mso-footer-margin: 1cm;
            mso-paper-source: 0;
          }
          div.Section1 { page: Section1; }
          body {
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            margin: 0;
            padding: 0;
          }
          h1 {
            font-size: 16pt;
            color: #2C5282;
            text-align: center;
            border-bottom: 2pt solid #2C5282;
            padding-bottom: 8pt;
            margin: 0 0 15pt 0;
          }
          h2 {
            font-size: 14pt;
            color: #2C5282;
            margin: 15pt 0 8pt 0;
          }
          h3 {
            font-size: 12pt;
            color: #2C5282;
            border-left: 3pt solid #2C5282;
            padding-left: 6pt;
            margin: 12pt 0 6pt 0;
          }
          h4 {
            font-size: 11pt;
            color: #2C5282;
            margin: 8pt 0 4pt 0;
          }
          .header {
            text-align: center;
            margin-bottom: 20pt;
          }
          .summary {
            background-color: #F7FAFC;
            padding: 10pt;
            border: 1pt solid #E2E8F0;
            margin-bottom: 15pt;
          }
          .result-item {
            margin-bottom: 15pt;
            page-break-inside: avoid;
          }
          .status-conforme { color: #38A169; font-weight: bold; }
          .status-parcial { color: #D69E2E; font-weight: bold; }
          .status-nao-conforme { color: #E53E3E; font-weight: bold; }
          .confidence { font-style: italic; color: #718096; }
          .recommendations { margin-top: 8pt; }
          .recommendations ul { margin: 4pt 0; padding-left: 18pt; }
          .evidence {
            background-color: #F7FAFC;
            padding: 8pt;
            border: 1pt solid #E2E8F0;
            margin: 8pt 0;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
          }
          .footer {
            text-align: center;
            margin-top: 20pt;
            font-size: 10pt;
            color: #718096;
            border-top: 1pt solid #E2E8F0;
            padding-top: 8pt;
          }
          p { margin: 4pt 0; }
          div { margin: 0; }
        </style>
      </head>
      <body>
        <div class="Section1">
          <div class="header">
            <h1>Relatório de Análise de Código</h1>
            <h2>VerificAI Code Quality System</h2>
            <p>Gerado em: ${currentDate} às ${currentTime}</p>
          </div>

          <div class="summary">
            <h3>Resumo da Análise</h3>
            <p><strong>Total de critérios analisados:</strong> ${results.length}</p>
            <p><strong>Critérios conformes:</strong> ${results.filter(r => r.status === 'compliant').length}</p>
            <p><strong>Critérios parcialmente conformes:</strong> ${results.filter(r => r.status === 'partially_compliant').length}</p>
            <p><strong>Critérios não conformes:</strong> ${results.filter(r => r.status === 'non_compliant').length}</p>
            <p><strong>Confiança média:</strong> ${Math.round(results.reduce((acc, r) => acc + r.confidence, 0) / results.length * 100)}%</p>
          </div>`;

    // Add results
    results.forEach((result, index) => {
      const statusClass = result.status === 'compliant' ? 'status-conforme' :
                         result.status === 'partially_compliant' ? 'status-parcial' : 'status-nao-conforme';
      const statusText = result.status === 'compliant' ? 'Conforme' :
                        result.status === 'partially_compliant' ? 'Parcialmente Conforme' : 'Não Conforme';

      content += `
        <div class="result-item">
          <h3>${index + 1}. ${result.criterion}</h3>
          <p><strong>Status:</strong> <span class="${statusClass}">${statusText}</span></p>
          <p><strong>Confiança:</strong> <span class="confidence">${Math.round(result.confidence * 100)}%</span></p>

          <div>
            <h4>Avaliação</h4>
            <div style="margin: 0;">${(() => {
              let processedText = result.assessment;
              // Handle code blocks
              processedText = processedText.replace(/`([^`]+)`/g, '<code style="background-color: #e9ecef; padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>');
              // Handle bold text
              processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
              // Convert line breaks to <br> tags
              processedText = processedText.replace(/\n/g, '<br>');
              return processedText;
            })()}</div>
          </div>`;

      if (result.recommendations && result.recommendations.length > 0) {
        content += `
          <div class="recommendations">
            <h4>Recomendações</h4>
            <ul>
              ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
          </div>`;
      }

      if (result.evidence && result.evidence.length > 0) {
        content += `
          <div>
            <h4>Evidências de Código</h4>
            ${result.evidence.map(ev => `
              <div class="evidence">
                <p><strong>Arquivo:</strong> ${ev.filePath}</p>
                <p><strong>Linguagem:</strong> ${ev.language}</p>
                <pre>${ev.code}</pre>
              </div>
            `).join('')}
          </div>`;
      }

      content += '</div>';
    });

    content += `
          <div class="footer">
            <p>Relatório gerado automaticamente pelo VerificAI Code Quality System</p>
            <p>Este relatório é confidencial e deve ser tratado de acordo com as políticas da organização.</p>
          </div>
        </div>
      </body>
      </html>`;

    return content;
  };

  const handleDownloadDocx = () => {
    if (results.length === 0) {
      alert('Nenhum resultado para gerar relatório.');
      return;
    }

    try {
      const content = generateReportContent();
      const blob = new Blob(['\ufeff', content], {
        type: 'application/msword'
      });

      const currentDate = new Date().toLocaleDateString('pt-BR').replace(/\//g, '-');
      const fileName = `relatorio-analise-codigo-${currentDate}.doc`;

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = fileName;
      link.click();

      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Erro ao gerar DOCX:', error);
      alert('Erro ao gerar o relatório DOCX. Por favor, tente novamente.');
    }
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
          <div className="card-header">
            <div className="row align-items-center">
              <div className="br-col">
                <h1 className="text-h1">Análise de Critérios Gerais</h1>
                <p className="text-regular">
                  Configure seus critérios de avaliação, faça upload dos arquivos e execute análises de código baseadas em padrões de qualidade gerais
                </p>
              </div>
              </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="br-tabs" data-tabs="analysis-tabs">
        <nav className="tab-navigation" role="tablist">
          {[
            { id: 'criteria', name: 'Critérios', icon: Settings },
            { id: 'results', name: 'Resultados', icon: FileText },
            { id: 'prompt', name: 'Último Prompt Enviado', icon: Eye },
            { id: 'response', name: 'Última Resposta da LLM', icon: FileText }
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
          <ResultsTable
            results={results}
            onDownloadDocx={handleDownloadDocx}
            onDeleteResults={handleDeleteResults}
          />
        )}

        {activeTab === 'prompt' && (
          <LatestPromptViewer />
        )}

        {activeTab === 'response' && (
          <LatestResponseViewer />
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

      {/* Modal de Confirmação de Nova Análise */}
      <Modal
        isOpen={confirmModalOpen}
        onClose={handleCancelModalAnalysis}
        title="⚠️ Confirmar Nova Análise"
        size="md"
      >
        <div className="space-y-4">
          <Alert variant="warning" title="Atenção!">
            Você está prestes a iniciar uma nova análise, e todos os resultados das análises anteriores serão <strong>permanentemente perdidos</strong>.
          </Alert>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">📋 Recomendação:</h4>
            <p className="text-sm text-blue-700">
              Antes de prosseguir, considere gerar um relatório da análise atual para salvar seus resultados.
              Você pode exportar os resultados usando os botões de download disponíveis na aba de resultados.
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <p className="text-sm text-gray-600">
              <strong>Deseja prosseguir com a nova análise?</strong>
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              variant="outline"
              onClick={handleCancelModalAnalysis}
              className="px-4 py-2"
            >
              ❌ Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmAnalysis}
              className="px-4 py-2"
            >
              ⚠️ Prosseguir e Perder Dados
            </Button>
          </div>
        </div>
      </Modal>

      </div>
  );
};

export default GeneralAnalysisPage;