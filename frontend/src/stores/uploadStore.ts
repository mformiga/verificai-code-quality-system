import { create } from 'zustand';
import type { UploadFile } from '@/types/file';

interface UploadState {
  files: UploadFile[];
  uploadProgress: Record<string, number>;
  uploading: boolean;
  error: string | null;
  uploadFiles: (files: globalThis.File[]) => Promise<void>;
  removeFile: (id: string) => void;
  clearFiles: () => void;
}

export const useUploadStore = create<UploadState>((set) => ({
  files: [],
  uploadProgress: {},
  uploading: false,
  error: null,

  uploadFiles: async (files) => {
    set({ uploading: true, error: null });

    try {
      for (const file of files) {
        const fileData: UploadFile = {
          id: Date.now().toString() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type,
          path: file.name,
          status: 'uploading',
          progress: 0,
        };

        set((state) => ({
          files: [...state.files, fileData],
        }));

        // Simulate upload progress
        const progressInterval = setInterval(() => {
          set((state) => {
            const currentProgress = state.uploadProgress[fileData.id] || 0;
            if (currentProgress < 100) {
              return {
                uploadProgress: {
                  ...state.uploadProgress,
                  [fileData.id]: Math.min(currentProgress + 10, 100),
                },
              };
            }
            clearInterval(progressInterval);
            return state;
          });
        }, 200);

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 2000));

        clearInterval(progressInterval);
        set((state) => ({
          files: state.files.map((f) =>
            f.id === fileData.id
              ? { ...f, status: 'completed', uploadedAt: new Date() }
              : f
          ),
          uploadProgress: {
            ...state.uploadProgress,
            [fileData.id]: 100,
          },
        }));
      }
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ uploading: false });
    }
  },

  removeFile: (id) => {
    set((state) => ({
      files: state.files.filter((f) => f.id !== id),
      uploadProgress: Object.fromEntries(
        Object.entries(state.uploadProgress).filter(([key]) => key !== id)
      ),
    }));
  },

  clearFiles: () => {
    set({
      files: [],
      uploadProgress: {},
      error: null,
    });
  },
}));