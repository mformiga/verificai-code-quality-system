import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CodePastePage from './CodePastePage';
import { useAuthStore } from '@/stores/authStore';

// Mock do useAuthStore
vi.mock('@/stores/authStore');
vi.mock('@/components/features/CodeInput', () => ({
  CodePasteInterface: ({ onCodeSave, onCodeDelete, onError }: any) => (
    <div data-testid="code-paste-interface">
      <button onClick={() => onCodeSave({ id: '1', title: 'Test Code' })}>
        Save Code
      </button>
      <button onClick={() => onCodeDelete('1')}>
        Delete Code
      </button>
      <button onClick={() => onError('Test error')}>
        Trigger Error
      </button>
    </div>
  );
}));

vi.mock('@/components/layout/MainLayout', () => ({
  MainLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="main-layout">{children}</div>
  ),
}));

vi.mock('@/components/common/Alert', () => ({
  Alert: ({ type, children }: { type: string; children: React.ReactNode }) => (
    <div data-testid={`alert-${type}`}>{children}</div>
  ),
}));

// Mock do console para não poluir a saída dos testes
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

describe('CodePastePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.log = vi.fn();
    console.error = vi.fn();
  });

  afterAll(() => {
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
  });

  const renderPage = () => {
    return render(
      <BrowserRouter>
        <CodePastePage />
      </BrowserRouter>
    );
  };

  describe('when user is authenticated', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: {
          id: 'user1',
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User'
        }
      } as any);
    });

    it('should render the page with correct title and description', () => {
      renderPage();

      expect(screen.getByText('Code Paste Interface')).toBeInTheDocument();
      expect(
        screen.getByText(/Paste your source code snippets and save them for later reference/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Language detection is automatic/i)
      ).toBeInTheDocument();
    });

    it('should render MainLayout wrapper', () => {
      renderPage();

      expect(screen.getByTestId('main-layout')).toBeInTheDocument();
    });

    it('should render CodePasteInterface when user is authenticated', () => {
      renderPage();

      expect(screen.getByTestId('code-paste-interface')).toBeInTheDocument();
    });

    it('should handle code save events', async () => {
      renderPage();

      const saveButton = screen.getByText('Save Code');
      saveButton.click();

      expect(console.log).toHaveBeenCalledWith('Code saved successfully:', {
        id: '1',
        title: 'Test Code'
      });
    });

    it('should handle code delete events', () => {
      renderPage();

      const deleteButton = screen.getByText('Delete Code');
      deleteButton.click();

      expect(console.log).toHaveBeenCalledWith('Code deleted:', '1');
    });

    it('should handle error events', () => {
      renderPage();

      const errorButton = screen.getByText('Trigger Error');
      errorButton.click();

      expect(console.error).toHaveBeenCalledWith('Code entry error:', 'Test error');
    });
  });

  describe('when user is not authenticated', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: null
      } as any);
    });

    it('should show login prompt when user is not authenticated', () => {
      renderPage();

      expect(screen.getByTestId('alert-info')).toBeInTheDocument();
      expect(screen.getByText('Please log in to use the code paste interface.')).toBeInTheDocument();
    });

    it('should not render CodePasteInterface when user is not authenticated', () => {
      renderPage();

      expect(screen.queryByTestId('code-paste-interface')).not.toBeInTheDocument();
    });
  });

  describe('component structure', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: {
          id: 'user1',
          username: 'testuser'
        }
      } as any);
    });

    it('should have correct page container styling', () => {
      renderPage();

      const container = screen.getByTestId('main-layout').firstChild;
      expect(container).toHaveClass('code-paste-page');
    });

    it('should have proper heading structure', () => {
      renderPage();

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
      expect(heading).toHaveTextContent('Code Paste Interface');
    });

    it('should have descriptive paragraph', () => {
      renderPage();

      const description = screen.getByText(
        /Paste your source code snippets and save them for later reference/i
      );
      expect(description).toBeInTheDocument();
      expect(description.tagName).toBe('P');
    });
  });

  describe('accessibility', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: {
          id: 'user1',
          username: 'testuser'
        }
      } as any);
    });

    it('should have proper heading hierarchy', () => {
      renderPage();

      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    });

    it('should have accessible page title', () => {
      renderPage();

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Code Paste Interface');
    });
  });

  describe('responsive behavior', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: {
          id: 'user1',
          username: 'testuser'
        }
      } as any);
    });

    it('should apply responsive classes', () => {
      renderPage();

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-3xl', 'font-bold', 'text-gray-900');
    });

    it('should have proper spacing classes', () => {
      renderPage();

      const container = screen.getByTestId('main-layout').firstChild as HTMLElement;
      const heading = screen.getByRole('heading', { level: 1 });

      // Verificar se há espaçamento adequado
      expect(container?.querySelector('.mb-6')).toBeInTheDocument();
      expect(heading.nextElementSibling).toHaveClass('text-gray-600', 'mt-2');
    });
  });

  describe('integration with CodePasteInterface', () => {
    beforeEach(() => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: {
          id: 'user1',
          username: 'testuser'
        }
      } as any);
    });

    it('should pass correct props to CodePasteInterface', () => {
      renderPage();

      expect(screen.getByTestId('code-paste-interface')).toBeInTheDocument();
    });

    it('should handle multiple interactions correctly', async () => {
      renderPage();

      // Testar múltiplas interações
      const saveButton = screen.getByText('Save Code');
      const deleteButton = screen.getByText('Delete Code');

      saveButton.click();
      deleteButton.click();

      expect(console.log).toHaveBeenCalledTimes(2);
      expect(console.log).toHaveBeenCalledWith('Code saved successfully:', {
        id: '1',
        title: 'Test Code'
      });
      expect(console.log).toHaveBeenCalledWith('Code deleted:', '1');
    });
  });
});