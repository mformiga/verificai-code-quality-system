import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PromptConfig } from '../PromptConfig';
import { usePromptStore } from '@/stores/promptStore';

// Mock the store
jest.mock('@/stores/promptStore');
const mockedUsePromptStore = usePromptStore as jest.MockedFunction<typeof usePromptStore>;

describe('PromptConfig Component', () => {
  const mockStore = {
    prompts: {
      general: {
        id: '1',
        name: 'Critérios Gerais',
        type: 'general' as const,
        description: 'Critérios gerais de análise',
        content: '# Critérios Gerais\n\nEste é um prompt de teste.',
        isActive: true,
        isDefault: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      architectural: {
        id: '2',
        name: 'Conformidade Arquitetural',
        type: 'architectural' as const,
        description: 'Critérios arquiteturais',
        content: '# Conformidade Arquitetural\n\nPrompt arquitetural.',
        isActive: true,
        isDefault: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      business: {
        id: '3',
        name: 'Conformidade Negocial',
        type: 'business' as const,
        description: 'Critérios negociais',
        content: '# Conformidade Negocial\n\nPrompt negocial.',
        isActive: true,
        isDefault: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    },
    isSaving: false,
    lastSaved: new Date(),
    hasUnsavedChanges: false,
    error: null,
    activePromptType: 'general' as const,
    updatePrompt: jest.fn(),
    setActivePromptType: jest.fn(),
    savePrompts: jest.fn(),
    discardChanges: jest.fn(),
    restoreDefaults: jest.fn(),
    loadPrompts: jest.fn(),
    clearAutoSaveTimer: jest.fn(),
  };

  beforeEach(() => {
    mockedUsePromptStore.mockReturnValue(mockStore);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders prompt configuration interface', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Configuração de Prompts')).toBeInTheDocument();
    expect(screen.getByText('Personalize os prompts que serão usados para análise do código-fonte.')).toBeInTheDocument();
  });

  it('displays three tab buttons for prompt types', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Critérios Gerais')).toBeInTheDocument();
    expect(screen.getByText('Conformidade Arquitetural')).toBeInTheDocument();
    expect(screen.getByText('Conformidade Negocial')).toBeInTheDocument();
  });

  it('shows active tab correctly', () => {
    render(<PromptConfig />);

    const generalTab = screen.getByText('Critérios Gerais');
    expect(generalTab.closest('button')).toHaveClass('is-active');
  });

  it('switches between prompt types when tabs are clicked', () => {
    render(<PromptConfig />);

    const architecturalTab = screen.getByText('Conformidade Arquitetural');
    fireEvent.click(architecturalTab);

    expect(mockStore.setActivePromptType).toHaveBeenCalledWith('architectural');
  });

  it('displays current prompt content in editor', () => {
    render(<PromptConfig />);

    const textarea = screen.getByDisplayValue('# Critérios Gerais\n\nEste é um prompt de teste.');
    expect(textarea).toBeInTheDocument();
  });

  it('calls updatePrompt when editor content changes', () => {
    render(<PromptConfig />);

    const textarea = screen.getByDisplayValue('# Critérios Gerais\n\nEste é um prompt de teste.');
    fireEvent.change(textarea, { target: { value: 'New content' } });

    expect(mockStore.updatePrompt).toHaveBeenCalledWith('general', 'New content');
  });

  it('shows auto-save indicator', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Salvo')).toBeInTheDocument();
  });

  it('displays error message when there is an error', () => {
    const errorStore = { ...mockStore, error: 'Test error message' };
    mockedUsePromptStore.mockReturnValue(errorStore);

    render(<PromptConfig />);

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('shows prompt information panel', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Informações do Prompt')).toBeInTheDocument();
    expect(screen.getByText('Nome:')).toBeInTheDocument();
    expect(screen.getByText('Descrição:')).toBeInTheDocument();
    expect(screen.getByText('Tipo:')).toBeInTheDocument();
    expect(screen.getByText('Status:')).toBeInTheDocument();
  });

  it('displays version history section', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Histórico de Versões')).toBeInTheDocument();
  });

  it('shows action buttons for prompt management', () => {
    render(<PromptConfig />);

    expect(screen.getByText('Salvar Alterações')).toBeInTheDocument();
    expect(screen.getByText('Descartar')).toBeInTheDocument();
    expect(screen.getByText('Restaurar Padrões')).toBeInTheDocument();
  });

  it('disables action buttons when saving', () => {
    const savingStore = { ...mockStore, isSaving: true };
    mockedUsePromptStore.mockReturnValue(savingStore);

    render(<PromptConfig />);

    expect(screen.getByText('Salvando...')).toBeInTheDocument();
    const saveButton = screen.getByText('Salvar Alterações');
    expect(saveButton).toBeDisabled();
  });
});