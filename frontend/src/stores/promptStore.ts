import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { PromptConfig, PromptType, PromptState, Prompt } from '@/types/prompt';
import { promptService } from '@/services/promptService';

const createEmptyPrompt = (type: PromptType): Prompt => ({
  id: '',
  name: type === 'general' ? 'Critérios Gerais' :
        type === 'architectural' ? 'Conformidade Arquitetural' : 'Conformidade Negocial',
  type,
  description: type === 'general' ? 'Critérios gerais de análise de código' :
              type === 'architectural' ? 'Critérios de conformidade arquitetural' : 'Critérios de conformidade negocial',
  content: '',
  isActive: true,
  isDefault: true,
  createdAt: new Date(),
  updatedAt: new Date(),
});

export const usePromptStore = create<PromptState>()(
  devtools(
    (set, get) => ({
      prompts: {
        general: createEmptyPrompt('general'),
        architectural: createEmptyPrompt('architectural'),
        business: createEmptyPrompt('business'),
      },
      isSaving: false,
      lastSaved: null,
      hasUnsavedChanges: false,
      error: null,
      autoSaveTimer: null,
      activePromptType: 'general',

      updatePrompt: (type: PromptType, content: string) => {
        set((state) => ({
          prompts: {
            ...state.prompts,
            [type]: {
              ...state.prompts[type],
              content,
              updatedAt: new Date(),
            },
          },
          hasUnsavedChanges: true,
        }));

        get().triggerAutoSave();
      },

      setActivePromptType: (type: PromptType) => {
        set({ activePromptType: type });
      },

      triggerAutoSave: () => {
        const state = get();
        if (state.autoSaveTimer) {
          clearTimeout(state.autoSaveTimer);
        }

        const timer = setTimeout(() => {
          get().savePrompts();
        }, 30000);

        set({ autoSaveTimer: timer });
      },

      savePrompts: async () => {
        const state = get();
        if (!state.hasUnsavedChanges) return;

        set({ isSaving: true, error: null });

        try {
          await promptService.savePrompts(state.prompts);
          set({
            isSaving: false,
            lastSaved: new Date(),
            hasUnsavedChanges: false,
            error: null,
          });
        } catch (error) {
          set({
            isSaving: false,
            error: error instanceof Error ? error.message : 'Erro ao salvar prompts',
          });
        }
      },

      discardChanges: async () => {
        set({ isSaving: true, error: null });

        try {
          const freshPrompts = await promptService.getPrompts();
          set({
            prompts: freshPrompts,
            isSaving: false,
            hasUnsavedChanges: false,
            error: null,
          });
        } catch (error) {
          set({
            isSaving: false,
            error: error instanceof Error ? error.message : 'Erro ao descartar alterações',
          });
        }
      },

      restoreDefaults: async () => {
        set({ isSaving: true, error: null });

        try {
          const defaultPrompts = await promptService.restoreDefaults();
          set({
            prompts: defaultPrompts,
            isSaving: false,
            hasUnsavedChanges: false,
            lastSaved: new Date(),
            error: null,
          });
        } catch (error) {
          set({
            isSaving: false,
            error: error instanceof Error ? error.message : 'Erro ao restaurar padrões',
          });
        }
      },

      loadPrompts: async () => {
        set({ isSaving: true, error: null });

        try {
          const prompts = await promptService.getPrompts();
          set({
            prompts,
            isSaving: false,
            hasUnsavedChanges: false,
            error: null,
          });
        } catch (error) {
          set({
            isSaving: false,
            error: error instanceof Error ? error.message : 'Erro ao carregar prompts',
          });
        }
      },

      clearAutoSaveTimer: () => {
        const state = get();
        if (state.autoSaveTimer) {
          clearTimeout(state.autoSaveTimer);
          set({ autoSaveTimer: null });
        }
      },

      reset: () => {
        get().clearAutoSaveTimer();
        set({
          prompts: {
            general: createEmptyPrompt('general'),
            architectural: createEmptyPrompt('architectural'),
            business: createEmptyPrompt('business'),
          },
          isSaving: false,
          lastSaved: null,
          hasUnsavedChanges: false,
          error: null,
          autoSaveTimer: null,
          activePromptType: 'general',
        });
      },
    }),
    {
      name: 'prompt-store',
    }
  )
);