import apiClient from './apiClient';

export interface FilePath {
  id: string;
  full_path: string;
  file_name: string;
  file_extension: string;
  folder_path: string;
  file_size?: number;
  last_modified?: string;
  created_at?: string;
  is_processed?: boolean;
  processing_status?: string;
  file?: File; // Add File object for upload
}

export const filePathService = {
  getFilePaths: async (page = 1, perPage = 100): Promise<{ paths: FilePath[], total: number }> => {
    const response = await apiClient.get(`/file-paths/?page=${page}&per_page=${perPage}`);
    return {
      paths: response.data.items || [],
      total: response.data.total || 0
    };
  },

  getProcessedFilePaths: async (): Promise<FilePath[]> => {
    const response = await apiClient.get('/file-paths/public');
    return response.data.items || [];
  },

  createFilePath: async (filePath: Omit<FilePath, 'id' | 'created_at'>): Promise<FilePath> => {
    const response = await apiClient.post('/file-paths/', filePath);
    return response.data;
  },

  updateFilePath: async (id: string, filePath: Partial<FilePath>): Promise<FilePath> => {
    const response = await apiClient.put(`/file-paths/${id}`, filePath);
    return response.data;
  },

  deleteFilePath: async (id: string): Promise<void> => {
    await apiClient.delete(`/file-paths/${id}`);
  }
};