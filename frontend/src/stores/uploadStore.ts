import { create } from 'zustand';
import type { UploadFile } from '@/types/file';
import { fileUploadService } from '@/services/fileUploadService';

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
      // Process files to handle directory structure (webkitRelativePath)
      const processedFiles = fileUploadService.processDirectoryFiles(files);

      for (const file of processedFiles) {
        const fileData: UploadFile = {
          id: Date.now().toString() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type,
          path: (file as any).webkitRelativePath || file.name,
          status: 'uploading',
          progress: 0,
        };

        set((state) => ({
          files: [...state.files, fileData],
        }));

        try {
          // Real API call to upload file
          const uploadedFile = await fileUploadService.uploadFile(
            file,
            (progress) => {
              // Update progress based on real upload progress
              set((state) => ({
                uploadProgress: {
                  ...state.uploadProgress,
                  [fileData.id]: progress,
                },
              }));
            }
          );

          // Update file with successful upload data
          set((state) => ({
            files: state.files.map((f) =>
              f.id === fileData.id
                ? {
                    ...f,
                    status: 'completed',
                    uploadedAt: new Date(),
                    // Use backend response data if available
                    id: uploadedFile.id || f.id,
                    name: uploadedFile.original_name || f.name,
                    path: uploadedFile.file_path || f.path
                  }
                : f
            ),
            uploadProgress: {
              ...state.uploadProgress,
              [fileData.id]: 100,
            },
          }));

        } catch (uploadError) {
          console.error(`Failed to upload ${file.name}:`, uploadError);

          // Update file with error status
          set((state) => ({
            files: state.files.map((f) =>
              f.id === fileData.id
                ? {
                    ...f,
                    status: 'error',
                    error: uploadError instanceof Error ? uploadError.message : 'Upload failed'
                  }
                : f
            ),
          }));

          // Continue with other files even if one fails
        }
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