import apiClient from './apiClient';
import type { Analysis, AnalysisConfig, AnalysisResult, AnalysisSummary } from '@/types/analysis';

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
};