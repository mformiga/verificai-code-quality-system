import apiClient from './apiClient';
import type { Analysis, AnalysisConfig, AnalysisResult, AnalysisSummary } from '@/types/analysis';

export interface AnalysisRequest {
  criteria_ids: string[];
  file_paths?: string[];  // Tornado opcional para compatibilidade
  use_code_entry?: boolean;  // Novo parâmetro
  code_entry_id?: string;  // ID específico do code_entry (opcional)
  analysis_name?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface AnalysisResponse {
  success: boolean;
  analysis_name: string;
  criteria_count: number;
  timestamp: string;
  model_used: string;
  usage: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
  };
  criteria_results: Record<string, {
    name: string;
    content: string;
  }>;
  raw_response: string;
  modified_prompt: string;
  file_paths: string[];
  db_result_id?: number; // Database ID of the saved analysis result
}

export const analysisService = {
  create: async (config: AnalysisConfig): Promise<Analysis> => {
    const response = await apiClient.post('/analysis', config);
    return response.data;
  },

  getById: async (id: string): Promise<Analysis> => {
    const response = await apiClient.get(`/analysis/${id}`);
    return response.data;
  },

  getResults: async (id: string): Promise<AnalysisResult[]> => {
    const response = await apiClient.get(`/analysis/${id}/results`);
    return response.data;
  },

  getSummary: async (id: string): Promise<AnalysisSummary> => {
    const response = await apiClient.get(`/analysis/${id}/summary`);
    return response.data;
  },

  cancel: async (id: string): Promise<void> => {
    await apiClient.post(`/analysis/${id}/cancel`);
  },

  retry: async (id: string): Promise<Analysis> => {
    const response = await apiClient.post(`/analysis/${id}/retry`);
    return response.data;
  },

  exportResults: async (id: string, format: 'pdf' | 'excel' | 'json'): Promise<Blob> => {
    const response = await apiClient.get(`/analysis/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  analyzeSelectedCriteria: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    try {
      console.log('🔍 DEBUG: analyzeSelectedCriteria chamado com request:', request);

      // Se usar código da code_entries, buscar o conteúdo e enviar no formato compatível
      if (request.use_code_entry) {
        console.log('🔍 DEBUG: Usando código da code_entries, buscando conteúdo...');

        const codeEntryResult = await analysisService.getLatestCodeEntry();
        console.log('🔍 DEBUG: Resultado getLatestCodeEntry:', codeEntryResult);

        if (codeEntryResult.success && codeEntryResult.code_content) {
          console.log('🔍 DEBUG: Código encontrado, criando request compatível...');

          // Criar um arquivo temporário com o conteúdo para manter compatibilidade
          const tempFilePath = 'temp_code_from_database.js';

          // Modificar request para usar formato compatível com o backend schema
          const compatibleRequest = {
            criteria_ids: request.criteria_ids,
            file_paths: [tempFilePath], // Mock file path para compatibilidade
            analysis_name: request.analysis_name || 'Análise de Critérios Selecionados',
            temperature: request.temperature || 0.7,
            max_tokens: request.max_tokens || 4000,
            use_code_entry: true, // Flag para o backend buscar da database
            code_entry_id: codeEntryResult.entry_id // ID do code_entry encontrado
          };

          console.log('🔍 DEBUG: Enviando request compatível:', compatibleRequest);
          console.log('🔍 DEBUG: Fazendo POST para /general-analysis/analyze-selected...');

          const response = await apiClient.post('/general-analysis/analyze-selected', compatibleRequest);
          console.log('🔍 DEBUG: Resposta recebida:', response);
          console.log('🔍 DEBUG: Response data:', response.data);
          return response.data;
        } else {
          console.error('🔍 DEBUG: Não foi possível obter código:', codeEntryResult);
          throw new Error(codeEntryResult.message || 'Não foi possível obter o código da base de dados');
        }
      } else {
        // Fluxo normal (sem usar code_entries)
        console.log('🔍 DEBUG: Fluxo normal, enviando request original');
        const response = await apiClient.post('/general-analysis/analyze-selected', request);
        return response.data;
      }
    } catch (error) {
      console.error('🔍 DEBUG: Error analyzing selected criteria:', error);
      console.error('🔍 DEBUG: Error response:', error.response?.data);
      console.error('🔍 DEBUG: Error status:', error.response?.status);
      console.error('🔍 DEBUG: Error message:', error.message);
      throw error;
    }
  },

  getAnalysisResults: async () => {
    try {
      // Use the authenticated endpoint to get current user's results
      const response = await apiClient.get('/general-analysis/results');
      return response.data;
    } catch (error) {
      console.error('Error fetching analysis results:', error);
      // Return empty results to avoid breaking the UI
      return { success: true, results: [], total: 0 };
    }
  },

  deleteAnalysisResult: async (resultId: number) => {
    try {
      const response = await apiClient.delete(`/general-analysis/results/${resultId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting analysis result:', error);
      throw error;
    }
  },

  deleteMultipleAnalysisResults: async (resultIds: number[]) => {
    try {
      const response = await apiClient.delete('/general-analysis/results', {
        data: { result_ids: resultIds }
      });
      return response.data;
    } catch (error) {
      console.error('Error deleting multiple analysis results:', error);
      throw error;
    }
  },

  deleteAllAnalysisResults: async () => {
    try {
      console.log('🗑️ DEBUG: Tentando excluir todos os resultados via /general-analysis/results/all...');
      const response = await apiClient.delete('/general-analysis/results/all');
      console.log('✅ DEBUG: Exclusão bem-sucedida:', response.data);
      return response.data;
    } catch (error) {
      console.warn('⚠️ DEBUG: Erro ao excluir todos os resultados (não crítico):', error.response?.status || error.message);

      // A exclusão não deve bloquear a análise - sempre retorna sucesso
      console.log('✅ DEBUG: Prosseguindo com análise mesmo sem exclusão');
      return {
        message: 'Análise pode prosseguir independentemente da exclusão de resultados anteriores',
        success: true,
        skipped: true
      };
    }
  },

  getLatestPrompt: async () => {
    try {
      const response = await apiClient.get('/general-analysis/latest-prompt');
      return response.data;
    } catch (error) {
      console.error('Error getting latest prompt:', error);
      throw error;
    }
  },

  getLatestResponse: async () => {
    try {
      const response = await apiClient.get('/general-analysis/latest-response');
      return response.data;
    } catch (error) {
      console.error('Error getting latest response:', error);
      throw error;
    }
  },

  getLatestRawResponse: async () => {
    try {
      const response = await apiClient.get('/general-analysis/latest-raw-response');
      return response.data;
    } catch (error) {
      console.error('Error getting latest raw response:', error);
      throw error;
    }
  },

  getLatestCodeEntry: async () => {
    try {
      console.log('🔍 DEBUG: Tentando buscar código via endpoint /code-entries...');

      // 1. Primeiro busca a lista de entries
      const listResponse = await apiClient.get('/code-entries');
      const entries = listResponse.data;
      console.log('🔍 DEBUG: Entries recebidos:', entries?.length || 0, 'items');

      if (!entries || entries.length === 0) {
        console.log('🔍 DEBUG: Nenhum entry encontrado no banco de dados');
        return {
          success: false,
          message: "Nenhum código encontrado. Por favor, cole um código na página de colagem primeiro.",
          code_content: null,
          title: null,
          language: null,
          lines_count: 0,
          characters_count: 0
        };
      }

      // 2. Pega o mais recente (primeiro da lista)
      const latestEntry = entries[0];
      console.log('🔍 DEBUG: Último entry encontrado:', latestEntry.title, 'ID:', latestEntry.id);

      // 3. Busca o conteúdo completo usando o endpoint individual
      console.log('🔍 DEBUG: Buscando conteúdo completo do entry:', latestEntry.id);
      try {
        const detailResponse = await apiClient.get(`/code-entries/${latestEntry.id}`);
        const fullEntry = detailResponse.data;
        console.log('🔍 DEBUG: Entry completo recebido:', fullEntry);

        // Verifica se o conteúdo do código existe
        if (!fullEntry.code_content || fullEntry.code_content.trim() === '') {
          console.log('🔍 DEBUG: O código está vazio mesmo no endpoint individual!');
          return {
            success: false,
            message: "Código encontrado mas está vazio. Por favor, cole um código na página de colagem.",
            code_content: null,
            title: null,
            language: null,
            lines_count: 0,
            characters_count: 0
          };
        }

        console.log('✅ DEBUG: Código encontrado com sucesso! Tamanho:', fullEntry.code_content.length, 'caracteres');
        return {
          success: true,
          message: "Código recuperado com sucesso",
          code_content: fullEntry.code_content,
          title: fullEntry.title || latestEntry.title,
          description: fullEntry.description || latestEntry.description,
          language: fullEntry.language || latestEntry.language,
          lines_count: fullEntry.lines_count || latestEntry.lines_count,
          characters_count: fullEntry.characters_count || latestEntry.characters_count,
          created_at: fullEntry.created_at || latestEntry.created_at,
          entry_id: fullEntry.id || latestEntry.id
        };

      } catch (detailError) {
        console.log('❌ DEBUG: Erro ao buscar detalhes do entry:', detailError);
        console.log('🔍 DEBUG: Tentando usar informações da lista como fallback...');

        // Fallback: se o endpoint individual falhar, tenta usar o que vier da lista
        if (latestEntry.code_content && latestEntry.code_content.trim() !== '') {
          return {
            success: true,
            message: "Código recuperado com sucesso (fallback)",
            code_content: latestEntry.code_content,
            title: latestEntry.title,
            description: latestEntry.description,
            language: latestEntry.language,
            lines_count: latestEntry.lines_count,
            characters_count: latestEntry.characters_count,
            created_at: latestEntry.created_at,
            entry_id: latestEntry.id
          };
        } else {
          return {
            success: false,
            message: "Não foi possível obter o conteúdo completo do código. Tente colar o código novamente.",
            code_content: null,
            title: null,
            language: null,
            lines_count: 0,
            characters_count: 0
          };
        }
      }

    } catch (error) {
      console.error('🔍 DEBUG: Erro geral ao buscar código:', error);
      throw error;
    }
  },
};