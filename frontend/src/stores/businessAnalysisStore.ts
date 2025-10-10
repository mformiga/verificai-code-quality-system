import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';

// Types
export interface DocumentInfo {
  id: string;
  name: string;
  type: 'user-story' | 'epic' | 'business-rule' | 'requirement';
  content: string;
  uploadDate: Date;
  metadata?: {
    fileSize: number;
    lastModified: Date;
    [key: string]: any;
  };
}

export interface BusinessAnalysisResult {
  id: string;
  analysisType: 'business';
  timestamp: Date;
  overallAssessment: string;
  businessDocuments: DocumentInfo[];
  semanticResults: any[];
  alignmentScore: number;
  gaps: any[];
  recommendations: string[];
  tokenUsage: {
    prompt: number;
    completion: number;
    total: number;
  };
  processingTime: number;
  status: 'processing' | 'completed' | 'failed' | 'cancelled';
}

export interface LLMInteraction {
  id: string;
  timestamp: Date;
  prompt: string;
  response: string;
  analysisType: 'business';
  documentIds: string[];
  tokenUsage: {
    prompt: number;
    completion: number;
    total: number;
  };
  processingTime: number;
}

export interface TabStatus {
  hasContent: boolean;
  isAccessible: boolean;
  lastUpdated: Date | null;
  status?: 'success' | 'error' | 'warning' | 'loading';
}

export type TabType = 'upload' | 'results' | 'prompt' | 'response';

export interface AnalysisSettings {
  includeUserStories: boolean;
  includeEpics: boolean;
  includeBusinessRules: boolean;
  includeRequirements: boolean;
  sensitivityThreshold: number;
  businessWeight: 'balanced' | 'business-focused' | 'technical-focused';
}

// Store Interface
interface BusinessAnalysisState {
  // Upload state
  businessDocuments: DocumentInfo[];
  selectedDocuments: string[];
  isUploading: boolean;
  uploadProgress: number;

  // Analysis state
  currentAnalysis: BusinessAnalysisResult | null;
  isAnalyzing: boolean;
  progress: number;
  error: string | null;

  // LLM communication state
  lastPromptSent: string | null;
  lastLLMResponse: string | null;
  llmCommunicationHistory: LLMInteraction[];

  // UI state
  activeTab: TabType;
  isManualMode: boolean;
  analysisSettings: AnalysisSettings;
  tabStatuses: Record<TabType, TabStatus>;

  // Actions
  // Document management
  uploadDocuments: (documents: DocumentInfo[]) => void;
  selectDocument: (documentId: string) => void;
  deselectDocument: (documentId: string) => void;
  toggleDocumentSelection: (documentId: string) => void;
  selectAllDocuments: () => void;
  deselectAllDocuments: () => void;
  deleteDocument: (documentId: string) => void;
  clearAllDocuments: () => void;

  // Analysis management
  startAnalysis: () => void;
  cancelAnalysis: () => void;
  setCurrentAnalysis: (analysis: BusinessAnalysisResult | null) => void;
  updateResultManually: (updates: Partial<BusinessAnalysisResult>) => void;

  // LLM communication
  setLastPromptSent: (prompt: string) => void;
  setLastLLMResponse: (response: string) => void;
  addLLMInteraction: (interaction: LLMInteraction) => void;

  // UI management
  setActiveTab: (tab: TabType) => void;
  setIsManualMode: (isManual: boolean) => void;
  updateAnalysisSettings: (settings: Partial<AnalysisSettings>) => void;
  setTabStatus: (tab: TabType, status: Partial<TabStatus>) => void;
  clearError: () => void;
  reset: () => void;
}

// Store Implementation
const useBusinessAnalysisStore = create<BusinessAnalysisState>((set, get) => ({
  // Initial state
  businessDocuments: [],
  selectedDocuments: [],
  isUploading: false,
  uploadProgress: 0,
  currentAnalysis: null,
  isAnalyzing: false,
  progress: 0,
  error: null,
  lastPromptSent: null,
  lastLLMResponse: null,
  llmCommunicationHistory: [],
  activeTab: 'upload',
  isManualMode: false,
  analysisSettings: {
    includeUserStories: true,
    includeEpics: true,
    includeBusinessRules: true,
    includeRequirements: true,
    sensitivityThreshold: 0.7,
    businessWeight: 'balanced'
  },
  tabStatuses: {
    upload: { hasContent: false, isAccessible: true, lastUpdated: null },
    results: { hasContent: false, isAccessible: false, lastUpdated: null },
    prompt: { hasContent: false, isAccessible: false, lastUpdated: null },
    response: { hasContent: false, isAccessible: false, lastUpdated: null }
  },

  // Document management actions
  uploadDocuments: (documents) => {
    set((state) => ({
      businessDocuments: [...state.businessDocuments, ...documents],
      selectedDocuments: [...state.selectedDocuments, ...documents.map(d => d.id)],
      isUploading: false,
      uploadProgress: 100,
      tabStatuses: {
        ...state.tabStatuses,
        upload: {
          ...state.tabStatuses.upload,
          hasContent: true,
          lastUpdated: new Date(),
          status: 'success'
        }
      }
    }));
  },

  selectDocument: (documentId) => {
    set((state) => ({
      selectedDocuments: state.selectedDocuments.includes(documentId)
        ? state.selectedDocuments
        : [...state.selectedDocuments, documentId]
    }));
  },

  deselectDocument: (documentId) => {
    set((state) => ({
      selectedDocuments: state.selectedDocuments.filter(id => id !== documentId)
    }));
  },

  toggleDocumentSelection: (documentId) => {
    set((state) => ({
      selectedDocuments: state.selectedDocuments.includes(documentId)
        ? state.selectedDocuments.filter(id => id !== documentId)
        : [...state.selectedDocuments, documentId]
    }));
  },

  selectAllDocuments: () => {
    set((state) => ({
      selectedDocuments: state.businessDocuments.map(doc => doc.id)
    }));
  },

  deselectAllDocuments: () => {
    set({ selectedDocuments: [] });
  },

  deleteDocument: (documentId) => {
    set((state) => ({
      businessDocuments: state.businessDocuments.filter(doc => doc.id !== documentId),
      selectedDocuments: state.selectedDocuments.filter(id => id !== documentId),
      tabStatuses: {
        ...state.tabStatuses,
        upload: {
          ...state.tabStatuses.upload,
          hasContent: state.businessDocuments.length > 1,
          lastUpdated: new Date()
        }
      }
    }));
  },

  clearAllDocuments: () => {
    set({
      businessDocuments: [],
      selectedDocuments: [],
      tabStatuses: {
        ...get().tabStatuses,
        upload: {
          hasContent: false,
          isAccessible: true,
          lastUpdated: new Date()
        }
      }
    });
  },

  // Analysis management actions
  startAnalysis: () => {
    const state = get();
    if (state.selectedDocuments.length === 0) {
      set({ error: 'Selecione pelo menos um documento para análise' });
      return;
    }

    // Mock analysis - in real implementation, this would call the API
    const mockAnalysis: BusinessAnalysisResult = {
      id: uuidv4(),
      analysisType: 'business',
      timestamp: new Date(),
      overallAssessment: `Análise de ${state.selectedDocuments.length} documentos de negócio revelou bom alinhamento geral com score de 85%. Foram identificadas oportunidades de melhoria em segurança e expansão de funcionalidades.`,
      businessDocuments: state.businessDocuments.filter(doc => state.selectedDocuments.includes(doc.id)),
      semanticResults: [],
      alignmentScore: 0.85,
      gaps: [
        { description: 'Falta autenticação de dois fatores', severity: 'high' },
        { description: 'Não há suporte para moedas internacionais', severity: 'medium' }
      ],
      recommendations: [
        'Implementar autenticação de dois fatores',
        'Adicionar suporte para múltiplas moedas',
        'Melhorar validação de crédito com integração externa'
      ],
      tokenUsage: {
        prompt: 1500,
        completion: 800,
        total: 2300
      },
      processingTime: 5000,
      status: 'completed'
    };

    const mockPrompt = `Analise os seguintes documentos de negócio e verifique o alinhamento com o código-fonte implementado:

Documentos:
${state.businessDocuments.filter(doc => state.selectedDocuments.includes(doc.id)).map(doc =>
  `- ${doc.name} (${doc.type}): ${doc.content.substring(0, 200)}...`
).join('\n')}

Por favor, forneça:
1. Score de alinhamento para cada documento (0-100%)
2. Gaps identificados
3. Recomendações de melhoria
4. Avaliação geral do alinhamento de negócio`;

    const mockResponse = `# Análise de Documentação de Negócio

## Resumo
Análise concluída com sucesso. Score geral de alinhamento: 85%

## Resultados por Documento
${state.businessDocuments.filter(doc => state.selectedDocuments.includes(doc.id)).map(doc =>
  `### ${doc.name}
- **Alinhamento:** ${80 + Math.floor(Math.random() * 20)}%
- **Status:** Conforme
- **Observações:** Implementação bem alinhada com os requisitos de negócio`
).join('\n')}

## Recomendações
1. Implementar autenticação de dois fatores
2. Adicionar suporte para múltiplas moedas
3. Melhorar validação de crédito`;

    set({
      isAnalyzing: true,
      progress: 0,
      error: null,
      activeTab: 'results',
      tabStatuses: {
        ...state.tabStatuses,
        results: {
          ...state.tabStatuses.results,
          status: 'loading',
          isAccessible: true
        }
      }
    });

    // Simulate analysis progress
    setTimeout(() => {
      set({ progress: 100, isAnalyzing: false });
    }, 3000);

    // Set results after "analysis" completes
    setTimeout(() => {
      set({
        currentAnalysis: mockAnalysis,
        lastPromptSent: mockPrompt,
        lastLLMResponse: mockResponse,
        tabStatuses: {
          ...get().tabStatuses,
          results: {
            hasContent: true,
            isAccessible: true,
            lastUpdated: new Date(),
            status: 'success'
          },
          prompt: {
            hasContent: true,
            isAccessible: true,
            lastUpdated: new Date(),
            status: 'success'
          },
          response: {
            hasContent: true,
            isAccessible: true,
            lastUpdated: new Date(),
            status: 'success'
          }
        }
      });
    }, 3500);
  },

  cancelAnalysis: () => {
    set({
      isAnalyzing: false,
      progress: 0,
      tabStatuses: {
        ...get().tabStatuses,
        results: {
          ...get().tabStatuses.results,
          status: 'warning' as const
        }
      }
    });
  },

  setCurrentAnalysis: (analysis) => {
    set({ currentAnalysis: analysis });
  },

  updateResultManually: (updates) => {
    set((state) => ({
      currentAnalysis: state.currentAnalysis
        ? { ...state.currentAnalysis, ...updates }
        : null,
      isManualMode: false
    }));
  },

  // LLM communication actions
  setLastPromptSent: (prompt) => {
    set({ lastPromptSent: prompt });
  },

  setLastLLMResponse: (response) => {
    set({ lastLLMResponse: response });
  },

  addLLMInteraction: (interaction) => {
    set((state) => ({
      llmCommunicationHistory: [...state.llmCommunicationHistory, interaction]
    }));
  },

  // UI management actions
  setActiveTab: (tab) => {
    set({ activeTab: tab });
  },

  setIsManualMode: (isManual) => {
    set({ isManualMode: isManual });
  },

  updateAnalysisSettings: (settings) => {
    set((state) => ({
      analysisSettings: { ...state.analysisSettings, ...settings }
    }));
  },

  setTabStatus: (tab, status) => {
    set((state) => ({
      tabStatuses: {
        ...state.tabStatuses,
        [tab]: { ...state.tabStatuses[tab], ...status }
      }
    }));
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      businessDocuments: [],
      selectedDocuments: [],
      isUploading: false,
      uploadProgress: 0,
      currentAnalysis: null,
      isAnalyzing: false,
      progress: 0,
      error: null,
      lastPromptSent: null,
      lastLLMResponse: null,
      llmCommunicationHistory: [],
      activeTab: 'upload',
      isManualMode: false,
      tabStatuses: {
        upload: { hasContent: false, isAccessible: true, lastUpdated: null },
        results: { hasContent: false, isAccessible: false, lastUpdated: null },
        prompt: { hasContent: false, isAccessible: false, lastUpdated: null },
        response: { hasContent: false, isAccessible: false, lastUpdated: null }
      }
    });
  }
}));

export { useBusinessAnalysisStore };