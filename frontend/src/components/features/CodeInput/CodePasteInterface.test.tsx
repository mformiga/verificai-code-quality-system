import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CodePasteInterface } from './CodePasteInterface';
import { CodeEntry } from '@/types/codeEntry';
import * as codeEntryService from '@/services/codeEntryService';
import * as languageDetectionUtils from '@/utils/languageDetection';

// Mock do service
vi.mock('@/services/codeEntryService');
vi.mock('@/utils/languageDetection');

describe('CodePasteInterface', () => {
  const mockOnCodeSave = vi.fn();
  const mockOnCodeDelete = vi.fn();
  const mockOnError = vi.fn();

  const mockCodeEntry: CodeEntry = {
    id: '1',
    codeContent: 'console.log("Hello World");',
    title: 'Test JavaScript',
    description: 'A simple JS code',
    language: 'javascript',
    linesCount: 1,
    charactersCount: 25,
    createdAt: new Date('2023-12-08T10:00:00Z'),
    updatedAt: new Date('2023-12-08T10:00:00Z'),
    userId: 'user1',
    isActive: true
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Mock das funções do service
    vi.mocked(codeEntryService.codeEntryService.getAll).mockResolvedValue([mockCodeEntry]);
    vi.mocked(codeEntryService.codeEntryService.create).mockResolvedValue(mockCodeEntry);
    vi.mocked(codeEntryService.codeEntryService.delete).mockResolvedValue();
    vi.mocked(codeEntryService.codeEntryService.detectLanguage).mockResolvedValue({
      language: 'javascript',
      confidence: 0.95
    });

    // Mock das funções de utilidade
    vi.mocked(languageDetectionUtils.detectProgrammingLanguage).mockReturnValue('javascript');
    vi.mocked(languageDetectionUtils.calculateCodeStats).mockReturnValue({
      linesCount: 1,
      charactersCount: 25
    });
    vi.mocked(languageDetectionUtils.generateAutoTitle).mockReturnValue('JavaScript Code - 2023-12-08 10:00');
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  const renderComponent = () => {
    return render(
      <CodePasteInterface
        onCodeSave={mockOnCodeSave}
        onCodeDelete={mockOnCodeDelete}
        onError={mockOnError}
      />
    );
  };

  describe('Initial render', () => {
    it('should render main components correctly', () => {
      renderComponent();

      expect(screen.getByText('Code Paste Interface')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Paste your code here/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Language/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Save Code/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Clear/i })).toBeInTheDocument();
      expect(screen.getByText(/Saved Codes/i)).toBeInTheDocument();
    });

    it('should show loading state initially', () => {
      vi.mocked(codeEntryService.codeEntryService.getAll).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve([mockCodeEntry]), 100))
      );

      renderComponent();

      expect(screen.getByText(/Loading saved codes/i)).toBeInTheDocument();
    });
  });

  describe('Code paste functionality', () => {
    it('should detect language when code is pasted', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      // Aguardar o debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(languageDetectionUtils.detectProgrammingLanguage).toHaveBeenCalledWith(code);
      });
    });

    it('should update stats when code is pasted', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      // Aguardar o debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(languageDetectionUtils.calculateCodeStats).toHaveBeenCalledWith(code);
      });
    });

    it('should generate auto title when language is detected', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      // Aguardar o debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(screen.getByDisplayValue(/JavaScript Code -/i)).toBeInTheDocument();
      });
    });
  });

  describe('Save functionality', () => {
    it('should save code successfully', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const saveButton = screen.getByRole('button', { name: /Save Code/i });

      await user.type(textArea, 'console.log("Hello World");');
      await user.click(saveButton);

      await waitFor(() => {
        expect(codeEntryService.codeEntryService.create).toHaveBeenCalledWith({
          codeContent: 'console.log("Hello World");',
          title: expect.stringContaining('JavaScript Code'),
          description: '',
          language: 'javascript'
        });
      });

      await waitFor(() => {
        expect(mockOnCodeSave).toHaveBeenCalledWith(mockCodeEntry);
      });

      expect(screen.getByText(/Code saved successfully/i)).toBeInTheDocument();
    });

    it('should show validation error for empty code', async () => {
      const user = userEvent.setup();
      renderComponent();

      const saveButton = screen.getByRole('button', { name: /Save Code/i });
      await user.click(saveButton);

      expect(screen.getByText(/Please enter some code/i)).toBeInTheDocument();
      expect(codeEntryService.codeEntryService.create).not.toHaveBeenCalled();
    });

    it('should show validation error for empty title', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const titleInput = screen.getByLabelText(/Title/i);
      const saveButton = screen.getByRole('button', { name: /Save Code/i });

      await user.type(textArea, 'console.log("Hello World");');
      await user.clear(titleInput); // Limpa o título auto-gerado
      await user.click(saveButton);

      expect(screen.getByText(/Title is required/i)).toBeInTheDocument();
      expect(codeEntryService.codeEntryService.create).not.toHaveBeenCalled();
    });

    it('should handle save error gracefully', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Failed to save code';

      vi.mocked(codeEntryService.codeEntryService.create).mockRejectedValueOnce(new Error(errorMessage));

      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const saveButton = screen.getByRole('button', { name: /Save Code/i });

      await user.type(textArea, 'console.log("Hello World");');
      await user.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });

      expect(mockOnError).toHaveBeenCalledWith(errorMessage);
    });

    it('should show loading state during save', async () => {
      const user = userEvent.setup();
      vi.mocked(codeEntryService.codeEntryService.create).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockCodeEntry), 100))
      );

      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const saveButton = screen.getByRole('button', { name: /Save Code/i });

      await user.type(textArea, 'console.log("Hello World");');
      await user.click(saveButton);

      expect(screen.getByText(/Saving/i)).toBeInTheDocument();
      expect(saveButton).toBeDisabled();
    });
  });

  describe('Clear functionality', () => {
    it('should clear form fields', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const titleInput = screen.getByLabelText(/Title/i);
      const descriptionInput = screen.getByLabelText(/Description/i);
      const clearButton = screen.getByRole('button', { name: /Clear/i });

      await user.type(textArea, 'console.log("Hello World");');
      await user.type(titleInput, 'Test Title');
      await user.type(descriptionInput, 'Test Description');
      await user.click(clearButton);

      expect(textArea).toHaveValue('');
      expect(titleInput).toHaveValue('');
      expect(descriptionInput).toHaveValue('');
    });
  });

  describe('Code list functionality', () => {
    it('should display saved codes', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
        expect(screen.getByText('A simple JS code')).toBeInTheDocument();
        expect(screen.getByText('javascript')).toBeInTheDocument();
        expect(screen.getByText('1 lines')).toBeInTheDocument();
      });
    });

    it('should handle delete with confirmation', async () => {
      const user = userEvent.setup();
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', { name: /Delete/i });
      await user.click(deleteButton);

      // Should show confirmation dialog
      expect(screen.getByText(/Are you sure/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Delete/i })).toBeInTheDocument();
    });

    it('should delete code after confirmation', async () => {
      const user = userEvent.setup();
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', { name: /Delete/i });
      await user.click(deleteButton);

      const confirmDeleteButton = screen.getAllByRole('button', { name: /Delete/i })[1]; // Second delete button in dialog
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(codeEntryService.codeEntryService.delete).toHaveBeenCalledWith('1');
      });

      expect(mockOnCodeDelete).toHaveBeenCalledWith('1');
      expect(screen.getByText(/Code deleted successfully/i)).toBeInTheDocument();
    });

    it('should cancel delete when cancelled', async () => {
      const user = userEvent.setup();
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', { name: /Delete/i });
      await user.click(deleteButton);

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      expect(codeEntryService.codeEntryService.delete).not.toHaveBeenCalled();
      expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
    });

    it('should handle delete error gracefully', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Failed to delete code';

      vi.mocked(codeEntryService.codeEntryService.delete).mockRejectedValueOnce(new Error(errorMessage));

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Test JavaScript')).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', { name: /Delete/i });
      await user.click(deleteButton);

      const confirmDeleteButton = screen.getAllByRole('button', { name: /Delete/i })[1];
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });

      expect(mockOnError).toHaveBeenCalledWith(errorMessage);
    });
  });

  describe('Language detection API', () => {
    it('should use API language detection when available', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      // Aguardar o debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(codeEntryService.codeEntryService.detectLanguage).toHaveBeenCalledWith(code);
      });
    });

    it('should fallback to client-side detection on API error', async () => {
      const user = userEvent.setup();
      vi.mocked(codeEntryService.codeEntryService.detectLanguage).mockRejectedValueOnce(new Error('API Error'));

      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      // Aguardar o debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(languageDetectionUtils.detectProgrammingLanguage).toHaveBeenCalledWith(code);
      });
    });
  });

  describe('Preview functionality', () => {
    it('should show code preview when code is entered', async () => {
      const user = userEvent.setup();
      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);
      const code = 'console.log("Hello World");';

      await user.type(textArea, code);

      expect(screen.getByDisplayValue(code)).toBeInTheDocument();
      expect(screen.getByText(/Preview/i)).toBeInTheDocument();
    });
  });

  describe('Error handling', () => {
    it('should clear error when user starts typing', async () => {
      const user = userEvent.setup();

      // Simular um erro pré-existente
      vi.mocked(codeEntryService.codeEntryService.getAll).mockRejectedValueOnce(new Error('Load error'));

      renderComponent();

      const textArea = screen.getByPlaceholderText(/Paste your code here/i);

      await waitFor(() => {
        expect(screen.getByText('Load error')).toBeInTheDocument();
      });

      await user.type(textArea, 'c');

      expect(screen.queryByText('Load error')).not.toBeInTheDocument();
    });
  });
});