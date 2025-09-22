import apiClient from './apiClient';
import type { Analysis, AnalysisConfig, AnalysisResult, AnalysisSummary } from '@/types/analysis';

export interface AnalysisRequest {
  criteria_ids: string[];
  file_paths: string[];
  analysis_name?: string;
  temperature?: number;
  max_tokens?: number;
  is_reanalysis?: boolean;
  result_id_to_update?: number;
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
      console.log('🔍 ENVIANDO REQUISIÇÃO PARA API:', {
        url: '/general-analysis/analyze-selected',
        data: request,
        baseURL: apiClient.defaults.baseURL
      });

      const response = await apiClient.post('/general-analysis/analyze-selected', request);
      console.log('🔍 RESPOSTA DA API:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error analyzing selected criteria:', error);
      console.error('🔍 DETALHES COMPLETOS DO ERRO:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data,
          headers: error.config?.headers
        }
      });
      throw error;
    }
  },

  getAnalysisResults: async () => {
    try {
      // Use the general-analysis public results endpoint
      const response = await apiClient.get('/general-analysis/results-public');
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
};