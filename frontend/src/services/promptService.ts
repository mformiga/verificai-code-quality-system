import { useApi } from '@/hooks/useApi';
import { PromptConfig, PromptVersion, Prompt } from '@/types/prompt';

export const promptService = {
  getPrompts: async (): Promise<PromptConfig> => {
    const { get } = useApi();
    const response = await get<PromptConfig>('/api/prompts');
    return response.data;
  },

  savePrompts: async (prompts: PromptConfig): Promise<PromptConfig> => {
    const { post } = useApi();

    await promptService.createVersionBackup(prompts);

    const response = await post<PromptConfig>('/api/prompts', prompts);
    return response.data;
  },

  createVersionBackup: async (prompts: PromptConfig): Promise<void> => {
    const { post } = useApi();
    await post('/api/prompts/backup', prompts);
  },

  getVersionHistory: async (promptId: string): Promise<PromptVersion[]> => {
    const { get } = useApi();
    const response = await get<PromptVersion[]>(`/api/prompts/${promptId}/versions`);
    return response.data;
  },

  restoreVersion: async (promptId: string, version: number): Promise<Prompt> => {
    const { post } = useApi();
    const response = await post<Prompt>(`/api/prompts/${promptId}/restore`, { version });
    return response.data;
  },

  restoreDefaults: async (): Promise<PromptConfig> => {
    const { post } = useApi();
    const response = await post<PromptConfig>('/api/prompts/restore-defaults');
    return response.data;
  },

  validatePrompt: async (content: string): Promise<{ isValid: boolean; errors: string[] }> => {
    const { post } = useApi();
    const response = await post<{ isValid: boolean; errors: string[] }>('/api/prompts/validate', { content });
    return response.data;
  },

  exportPrompts: async (): Promise<string> => {
    const { get } = useApi();
    const response = await get<string>('/api/prompts/export');
    return response.data;
  },

  importPrompts: async (promptsData: string): Promise<PromptConfig> => {
    const { post } = useApi();
    const response = await post<PromptConfig>('/api/prompts/import', { data: promptsData });
    return response.data;
  },
};