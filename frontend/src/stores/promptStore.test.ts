import { usePromptStore } from './promptStore';
import { promptService } from '@/services/promptService';
import { act } from '@testing-library/react';

// Mock the prompt service
jest.mock('@/services/promptService');
const mockedPromptService = promptService as jest.Mocked<typeof promptService>;

// Mock timers for auto-save functionality
jest.useFakeTimers();

describe('PromptStore', () => {
  const originalState = usePromptStore.getState();

  beforeEach(() => {
    // Reset store state before each test
    usePromptStore.setState(originalState, true);
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = usePromptStore.getState();

      expect(state.prompts.general.name).toBe('Critérios Gerais');
      expect(state.prompts.general.content).toBe('');
      expect(state.prompts.general.isActive).toBe(true);
      expect(state.prompts.general.isDefault).toBe(true);

      expect(state.prompts.architectural.name).toBe('Conformidade Arquitetural');
      expect(state.prompts.business.name).toBe('Conformidade Negocial');

      expect(state.isSaving).toBe(false);
      expect(state.lastSaved).toBe(null);
      expect(state.hasUnsavedChanges).toBe(false);
      expect(state.error).toBe(null);
      expect(state.autoSaveTimer).toBe(null);
      expect(state.activePromptType).toBe('general');
    });
  });

  describe('updatePrompt', () => {
    it('should update prompt content and set unsaved changes', () => {
      const { updatePrompt } = usePromptStore.getState();

      act(() => {
        updatePrompt('general', 'New content for general prompt');
      });

      const state = usePromptStore.getState();
      expect(state.prompts.general.content).toBe('New content for general prompt');
      expect(state.hasUnsavedChanges).toBe(true);
      expect(state.prompts.general.updatedAt).toBeInstanceOf(Date);
    });

    it('should trigger auto-save timer when prompt is updated', () => {
      const { updatePrompt } = usePromptStore.getState();

      act(() => {
        updatePrompt('general', 'Content that should trigger auto-save');
      });

      const state = usePromptStore.getState();
      expect(state.autoSaveTimer).not.toBeNull();
    });
  });

  describe('triggerAutoSave', () => {
    it('should clear existing timer and set new one', () => {
      const { triggerAutoSave } = usePromptStore.getState();

      // Set initial timer
      act(() => {
        usePromptStore.setState({
          autoSaveTimer: setTimeout(() => {}, 1000),
        });
      });

      const initialTimer = usePromptStore.getState().autoSaveTimer;

      act(() => {
        triggerAutoSave();
      });

      const state = usePromptStore.getState();
      expect(state.autoSaveTimer).not.toBe(initialTimer);
    });

    it('should schedule save for 30 seconds', () => {
      const { triggerAutoSave, savePrompts } = usePromptStore.getState();
      const savePromptsSpy = jest.spyOn(usePromptStore.getState(), 'savePrompts');

      act(() => {
        triggerAutoSave();
      });

      act(() => {
        jest.advanceTimersByTime(30000);
      });

      expect(savePromptsSpy).toHaveBeenCalled();
      savePromptsSpy.mockRestore();
    });
  });

  describe('savePrompts', () => {
    it('should save prompts when there are unsaved changes', async () => {
      mockedPromptService.savePrompts.mockResolvedValue({
        general: { ...usePromptStore.getState().prompts.general, content: 'Saved content' },
        architectural: usePromptStore.getState().prompts.architectural,
        business: usePromptStore.getState().prompts.business,
      });

      const { savePrompts } = usePromptStore.getState();

      // Set unsaved changes
      act(() => {
        usePromptStore.setState({ hasUnsavedChanges: true });
      });

      await act(async () => {
        await savePrompts();
      });

      const state = usePromptStore.getState();
      expect(state.isSaving).toBe(false);
      expect(state.hasUnsavedChanges).toBe(false);
      expect(state.lastSaved).toBeInstanceOf(Date);
      expect(state.error).toBe(null);
      expect(mockedPromptService.savePrompts).toHaveBeenCalled();
    });

    it('should not save prompts when there are no unsaved changes', async () => {
      const { savePrompts } = usePromptStore.getState();

      // Ensure no unsaved changes
      act(() => {
        usePromptStore.setState({ hasUnsavedChanges: false });
      });

      await act(async () => {
        await savePrompts();
      });

      expect(mockedPromptService.savePrompts).not.toHaveBeenCalled();
    });

    it('should handle save errors', async () => {
      const errorMessage = 'Failed to save prompts';
      mockedPromptService.savePrompts.mockRejectedValue(new Error(errorMessage));

      const { savePrompts } = usePromptStore.getState();

      // Set unsaved changes
      act(() => {
        usePromptStore.setState({ hasUnsavedChanges: true });
      });

      await act(async () => {
        await savePrompts();
      });

      const state = usePromptStore.getState();
      expect(state.isSaving).toBe(false);
      expect(state.hasUnsavedChanges).toBe(true);
      expect(state.error).toBe(errorMessage);
    });
  });

  describe('discardChanges', () => {
    it('should load fresh prompts from service', async () => {
      const freshPrompts = {
        general: {
          ...usePromptStore.getState().prompts.general,
          content: 'Fresh content from server',
        },
        architectural: usePromptStore.getState().prompts.architectural,
        business: usePromptStore.getState().prompts.business,
      };

      mockedPromptService.getPrompts.mockResolvedValue(freshPrompts);

      const { discardChanges } = usePromptStore.getState();

      await act(async () => {
        await discardChanges();
      });

      const state = usePromptStore.getState();
      expect(state.prompts.general.content).toBe('Fresh content from server');
      expect(state.hasUnsavedChanges).toBe(false);
      expect(mockedPromptService.getPrompts).toHaveBeenCalled();
    });

    it('should handle discard errors', async () => {
      const errorMessage = 'Failed to discard changes';
      mockedPromptService.getPrompts.mockRejectedValue(new Error(errorMessage));

      const { discardChanges } = usePromptStore.getState();

      await act(async () => {
        await discardChanges();
      });

      const state = usePromptStore.getState();
      expect(state.error).toBe(errorMessage);
    });
  });

  describe('restoreDefaults', () => {
    it('should restore default prompts', async () => {
      const defaultPrompts = {
        general: {
          ...usePromptStore.getState().prompts.general,
          content: 'Default general content',
        },
        architectural: {
          ...usePromptStore.getState().prompts.architectural,
          content: 'Default architectural content',
        },
        business: {
          ...usePromptStore.getState().prompts.business,
          content: 'Default business content',
        },
      };

      mockedPromptService.restoreDefaults.mockResolvedValue(defaultPrompts);

      const { restoreDefaults } = usePromptStore.getState();

      await act(async () => {
        await restoreDefaults();
      });

      const state = usePromptStore.getState();
      expect(state.prompts.general.content).toBe('Default general content');
      expect(state.prompts.architectural.content).toBe('Default architectural content');
      expect(state.prompts.business.content).toBe('Default business content');
      expect(state.hasUnsavedChanges).toBe(false);
      expect(state.lastSaved).toBeInstanceOf(Date);
      expect(mockedPromptService.restoreDefaults).toHaveBeenCalled();
    });

    it('should handle restore defaults errors', async () => {
      const errorMessage = 'Failed to restore defaults';
      mockedPromptService.restoreDefaults.mockRejectedValue(new Error(errorMessage));

      const { restoreDefaults } = usePromptStore.getState();

      await act(async () => {
        await restoreDefaults();
      });

      const state = usePromptStore.getState();
      expect(state.error).toBe(errorMessage);
    });
  });

  describe('loadPrompts', () => {
    it('should load prompts from service', async () => {
      const loadedPrompts = {
        general: {
          ...usePromptStore.getState().prompts.general,
          content: 'Loaded content',
        },
        architectural: usePromptStore.getState().prompts.architectural,
        business: usePromptStore.getState().prompts.business,
      };

      mockedPromptService.getPrompts.mockResolvedValue(loadedPrompts);

      const { loadPrompts } = usePromptStore.getState();

      await act(async () => {
        await loadPrompts();
      });

      const state = usePromptStore.getState();
      expect(state.prompts.general.content).toBe('Loaded content');
      expect(state.hasUnsavedChanges).toBe(false);
      expect(mockedPromptService.getPrompts).toHaveBeenCalled();
    });

    it('should handle load errors', async () => {
      const errorMessage = 'Failed to load prompts';
      mockedPromptService.getPrompts.mockRejectedValue(new Error(errorMessage));

      const { loadPrompts } = usePromptStore.getState();

      await act(async () => {
        await loadPrompts();
      });

      const state = usePromptStore.getState();
      expect(state.error).toBe(errorMessage);
    });
  });

  describe('clearAutoSaveTimer', () => {
    it('should clear auto-save timer', () => {
      // Set a timer
      const timer = setTimeout(() => {}, 30000);
      act(() => {
        usePromptStore.setState({ autoSaveTimer: timer });
      });

      const { clearAutoSaveTimer } = usePromptStore.getState();

      act(() => {
        clearAutoSaveTimer();
      });

      const state = usePromptStore.getState();
      expect(state.autoSaveTimer).toBe(null);
    });
  });

  describe('setActivePromptType', () => {
    it('should change active prompt type', () => {
      const { setActivePromptType } = usePromptStore.getState();

      act(() => {
        setActivePromptType('architectural');
      });

      const state = usePromptStore.getState();
      expect(state.activePromptType).toBe('architectural');

      act(() => {
        setActivePromptType('business');
      });

      expect(usePromptStore.getState().activePromptType).toBe('business');
    });
  });

  describe('reset', () => {
    it('should reset store to initial state', () => {
      const { reset, updatePrompt, setActivePromptType } = usePromptStore.getState();

      // Change state
      act(() => {
        updatePrompt('general', 'Modified content');
        setActivePromptType('business');
        usePromptStore.setState({
          hasUnsavedChanges: true,
          error: 'Some error',
          autoSaveTimer: setTimeout(() => {}, 1000),
        });
      });

      // Reset
      act(() => {
        reset();
      });

      const state = usePromptStore.getState();
      expect(state.prompts.general.content).toBe('');
      expect(state.activePromptType).toBe('general');
      expect(state.hasUnsavedChanges).toBe(false);
      expect(state.error).toBe(null);
      expect(state.autoSaveTimer).toBe(null);
    });
  });

  describe('auto-save behavior', () => {
    it('should not trigger save immediately after update', () => {
      const { updatePrompt, savePrompts } = usePromptStore.getState();
      const savePromptsSpy = jest.spyOn(usePromptStore.getState(), 'savePrompts');

      act(() => {
        updatePrompt('general', 'New content');
      });

      expect(savePromptsSpy).not.toHaveBeenCalled();
      savePromptsSpy.mockRestore();
    });

    it('should trigger save after 30 seconds of inactivity', () => {
      const { updatePrompt, savePrompts } = usePromptStore.getState();
      const savePromptsSpy = jest.spyOn(usePromptStore.getState(), 'savePrompts');

      act(() => {
        updatePrompt('general', 'Content for auto-save test');
      });

      // Fast forward time
      act(() => {
        jest.advanceTimersByTime(30000);
      });

      expect(savePromptsSpy).toHaveBeenCalled();
      savePromptsSpy.mockRestore();
    });

    it('should reset timer when new update occurs before save', () => {
      const { updatePrompt, savePrompts } = usePromptStore.getState();
      const savePromptsSpy = jest.spyOn(usePromptStore.getState(), 'savePrompts');

      act(() => {
        updatePrompt('general', 'First update');
      });

      // Advance 20 seconds (not yet 30)
      act(() => {
        jest.advanceTimersByTime(20000);
      });

      // Update again (should reset timer)
      act(() => {
        updatePrompt('general', 'Second update');
      });

      // Advance another 20 seconds (total 40, but timer was reset)
      act(() => {
        jest.advanceTimersByTime(20000);
      });

      expect(savePromptsSpy).not.toHaveBeenCalled();

      // Advance final 10 seconds
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      expect(savePromptsSpy).toHaveBeenCalled();
      savePromptsSpy.mockRestore();
    });
  });
});