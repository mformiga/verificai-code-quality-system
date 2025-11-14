import apiClient from './apiClient';
import { PromptConfig, PromptVersion, Prompt } from '@/types/prompt';

export const promptService = {
  getPrompts: async (): Promise<PromptConfig> => {
    const response = await apiClient.get<PromptConfig>('/prompts/config');
    return response.data;
  },

  savePrompts: async (prompts: PromptConfig): Promise<PromptConfig> => {
    await promptService.createVersionBackup(prompts);
    // Use the backup endpoint for saving since it works
    const response = await apiClient.post<PromptConfig>('/prompts/backup', prompts);
    return response.data;
  },

  createVersionBackup: async (prompts: PromptConfig): Promise<void> => {
    try {
      await apiClient.post('/prompts/backup', prompts);
    } catch (error) {
      // Silently fail for backup - it's not critical for the main functionality
      console.warn('Failed to create version backup:', error);
    }
  },

  getVersionHistory: async (promptId: string): Promise<PromptVersion[]> => {
    try {
      const response = await apiClient.get<PromptVersion[]>(`/prompts/${promptId}/versions`);
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch version history:', error);
      return [];
    }
  },

  restoreVersion: async (promptId: string, version: number): Promise<Prompt> => {
    const response = await apiClient.post<Prompt>(`/prompts/${promptId}/restore`, { version });
    return response.data;
  },

  restoreDefaults: async (): Promise<PromptConfig> => {
    const response = await apiClient.post<PromptConfig>('/prompts/restore-defaults');
    return response.data;
  },

  validatePrompt: async (content: string): Promise<{ isValid: boolean; errors: string[] }> => {
    const response = await apiClient.post<{ isValid: boolean; errors: string[] }>('/prompts/validate', { content });
    return response.data;
  },

  exportPrompts: async (): Promise<string> => {
    const response = await apiClient.get<string>('/prompts/export');
    return response.data;
  },

  importPrompts: async (promptsData: string): Promise<PromptConfig> => {
    const response = await apiClient.post<PromptConfig>('/prompts/import', { data: promptsData });
    return response.data;
  },
};