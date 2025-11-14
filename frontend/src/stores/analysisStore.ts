import { create } from 'zustand';
import type { Analysis, AnalysisResult, AnalysisConfig } from '@/types/analysis';

interface AnalysisState {
  currentAnalysis: Analysis | null;
  results: AnalysisResult[];
  loading: boolean;
  error: string | null;
  startAnalysis: (config: AnalysisConfig) => Promise<void>;
  updateResults: (results: AnalysisResult[]) => void;
  resetAnalysis: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentAnalysis: null,
  results: [],
  loading: false,
  error: null,

  startAnalysis: async (config) => {
    set({ loading: true, error: null, results: [] });

    try {
      // Simulate API call
      const analysis: Analysis = {
        id: Date.now().toString(),
        sessionId: 'session-1',
        type: config.type,
        status: 'running',
        progress: 0,
        files: [],
        startTime: new Date(),
        results: [],
      };

      set({ currentAnalysis: analysis });

      // Simulate progress
      const progressInterval = setInterval(() => {
        set((state) => {
          if (state.currentAnalysis && state.currentAnalysis.progress < 100) {
            const newProgress = Math.min(state.currentAnalysis.progress + 10, 100);
            const status = newProgress === 100 ? 'completed' : 'running';
            return {
              currentAnalysis: {
                ...state.currentAnalysis,
                progress: newProgress,
                status,
                endTime: newProgress === 100 ? new Date() : undefined,
              },
            };
          }
          clearInterval(progressInterval);
          return state;
        });
      }, 500);

      // Simulate analysis completion
      await new Promise((resolve) => setTimeout(resolve, 5000));

      const mockResults: AnalysisResult[] = [
        {
          id: '1',
          analysisId: analysis.id,
          criterion: 'Uso de constantes para valores mágicos',
          description: 'O código deve evitar valores mágicos e usar constantes nomeadas',
          status: 'fail',
          score: 0,
          details: 'Encontrado valor mágico "3000" no arquivo config.js sem constante definida',
          fileLocation: 'src/config.js',
          lineNumber: 15,
          createdAt: new Date(),
        },
        {
          id: '2',
          analysisId: analysis.id,
          criterion: 'Nomenclatura de funções',
          description: 'Funções devem seguir convenção camelCase e ser descritivas',
          status: 'pass',
          score: 100,
          details: 'Todas as funções seguem a convenção de nomenclatura adequada',
          createdAt: new Date(),
        },
        {
          id: '3',
          analysisId: analysis.id,
          criterion: 'Tratamento de erros',
          description: 'Funções devem ter tratamento adequado de erros',
          status: 'warning',
          score: 70,
          details: 'Algumas funções não possuem tratamento de erros adequado',
          fileLocation: 'src/services/api.js',
          lineNumber: 45,
          createdAt: new Date(),
        },
      ];

      clearInterval(progressInterval);
      set({
        results: mockResults,
        currentAnalysis: {
          ...analysis,
          progress: 100,
          status: 'completed',
          endTime: new Date(),
        },
        loading: false,
      });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false });
    }
  },

  updateResults: (results) => {
    set({ results });
  },

  resetAnalysis: () => {
    set({
      currentAnalysis: null,
      results: [],
      loading: false,
      error: null,
    });
  },
}));