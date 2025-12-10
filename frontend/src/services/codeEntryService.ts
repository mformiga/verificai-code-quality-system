/**
 * Service for code entry API calls
 */

import { useAuthStore } from '@/stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface CodeEntry {
  id?: string;
  code_content: string;
  title: string;
  description?: string;
  language?: string;
  lines_count?: number;
  characters_count?: number;
  created_at?: string;
  updated_at?: string;
  user_id?: number;
  is_active?: boolean;
}

interface CodeEntryCreate {
  code_content: string;
  title: string;
  description?: string;
  language?: string;
  lines_count: number;
  characters_count: number;
}

interface CodeLanguageDetection {
  language: string;
  confidence?: number;
}

interface CodeEntryDeleteResponse {
  message: string;
  success: boolean;
}

export const codeEntryService = {
  /**
   * Detect programming language from code content
   */
  async detectLanguage(codeContent: string): Promise<CodeLanguageDetection> {
    const { token, isAuthenticated } = useAuthStore.getState();

    if (!token || !isAuthenticated) {
      // Fallback para localStorage ou detecção básica
      console.log('No auth token, using fallback language detection');

      // Detecção básica por extensão ou sintaxe
      const firstLine = codeContent.split('\n')[0].trim();
      let detectedLanguage = 'text';

      if (firstLine.includes('import ') || firstLine.includes('from ')) {
        detectedLanguage = 'python';
      } else if (firstLine.includes('function ') || firstLine.includes('const ') || firstLine.includes('let ')) {
        detectedLanguage = 'javascript';
      } else if (firstLine.includes('def ') || firstLine.includes('class ')) {
        detectedLanguage = 'python';
      } else if (firstLine.includes('public class ') || firstLine.includes('import java')) {
        detectedLanguage = 'java';
      } else if (firstLine.includes('#include') || firstLine.includes('int main')) {
        detectedLanguage = 'cpp';
      }

      return { language: detectedLanguage, confidence: 0.5 };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/code-entries/detect-language`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(codeContent),
      });

      if (!response.ok) {
        console.error('Language detection failed:', response.status);
        // Fallback para detecção básica
        return { language: 'text', confidence: 0.5 };
      }

      return response.json();
    } catch (error) {
      console.error('Language detection error:', error);
      return { language: 'text', confidence: 0.5 };
    }
  },

  /**
   * Create a new code entry
   */
  async createCodeEntry(codeEntry: CodeEntryCreate): Promise<CodeEntry> {
    const { token, isAuthenticated } = useAuthStore.getState();
    console.log('🔍 CODE ENTRY SERVICE DEBUG: createCodeEntry called');
    console.log('🔍 CODE ENTRY SERVICE DEBUG: Token:', token ? 'exists' : 'none');
    console.log('🔍 CODE ENTRY SERVICE DEBUG: isAuthenticated:', isAuthenticated);

    if (!token || !isAuthenticated) {
      console.log('🔍 CODE ENTRY SERVICE DEBUG: No valid token, saving to localStorage');

      // Salvar em localStorage como fallback
      const newEntry: CodeEntry = {
        ...codeEntry,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        user_id: 1,
        is_active: true
      };

      // Obter entradas existentes do localStorage
      const existingEntries = localStorage.getItem('codeEntries');
      const entries = existingEntries ? JSON.parse(existingEntries) : [];

      // Adicionar nova entrada
      entries.unshift(newEntry); // Adicionar no início

      // Manter apenas as 100 entradas mais recentes
      if (entries.length > 100) {
        entries.splice(100);
      }

      // Salvar no localStorage
      localStorage.setItem('codeEntries', JSON.stringify(entries));

      console.log('🔍 CODE ENTRY SERVICE DEBUG: Saved to localStorage');
      return newEntry;
    }

    try {
      console.log('🔍 CODE ENTRY SERVICE DEBUG: Sending to API');
      const response = await fetch(`${API_BASE_URL}/code-entries`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(codeEntry),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Create code entry failed:', response.status, errorText);

        // Fallback para localStorage se API falhar
        console.log('🔍 CODE ENTRY SERVICE DEBUG: API failed, falling back to localStorage');
        const newEntry: CodeEntry = {
          ...codeEntry,
          id: Date.now().toString(),
          created_at: new Date().toISOString(),
          user_id: 1,
          is_active: true
        };

        const existingEntries = localStorage.getItem('codeEntries');
        const entries = existingEntries ? JSON.parse(existingEntries) : [];
        entries.unshift(newEntry);

        if (entries.length > 100) {
          entries.splice(100);
        }

        localStorage.setItem('codeEntries', JSON.stringify(entries));
        return newEntry;
      }

      const result = await response.json();
      console.log('🔍 CODE ENTRY SERVICE DEBUG: API success');
      return result;
    } catch (error) {
      console.error('Create code entry error:', error);

      // Fallback para localStorage em caso de erro
      console.log('🔍 CODE ENTRY SERVICE DEBUG: Error, falling back to localStorage');
      const newEntry: CodeEntry = {
        ...codeEntry,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        user_id: 1,
        is_active: true
      };

      const existingEntries = localStorage.getItem('codeEntries');
      const entries = existingEntries ? JSON.parse(existingEntries) : [];
      entries.unshift(newEntry);

      if (entries.length > 100) {
        entries.splice(100);
      }

      localStorage.setItem('codeEntries', JSON.stringify(entries));
      return newEntry;
    }
  },

  /**
   * Get list of code entries for the current user
   */
  async getCodeEntries(): Promise<CodeEntry[]> {
    const { token, isAuthenticated } = useAuthStore.getState();
    console.log('🔍 CODE ENTRY SERVICE DEBUG: getCodeEntries called');
    console.log('🔍 CODE ENTRY SERVICE DEBUG: Token:', token ? 'exists' : 'none');
    console.log('🔍 CODE ENTRY SERVICE DEBUG: isAuthenticated:', isAuthenticated);

    if (!token || !isAuthenticated) {
      console.log('🔍 CODE ENTRY SERVICE DEBUG: No valid token, loading from localStorage');

      // Tentar obter do localStorage primeiro
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          console.log('🔍 CODE ENTRY SERVICE DEBUG: Found entries in localStorage:', entries.length);
          return entries;
        } catch (error) {
          console.error('Failed to parse stored code entries:', error);
        }
      }

      console.log('🔍 CODE ENTRY SERVICE DEBUG: No entries found, returning empty array');
      return [];
    }

    try {
      console.log('🔍 CODE ENTRY SERVICE DEBUG: Fetching from API');
      const response = await fetch(`${API_BASE_URL}/code-entries`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Get code entries failed:', response.status, errorText);

        // Fallback para localStorage
        console.log('🔍 CODE ENTRY SERVICE DEBUG: API failed, trying localStorage');
        const storedEntries = localStorage.getItem('codeEntries');
        if (storedEntries) {
          try {
            const entries = JSON.parse(storedEntries);
            return entries;
          } catch (error) {
            console.error('Failed to parse stored code entries:', error);
          }
        }
        return [];
      }

      const entries = await response.json();
      console.log('🔍 CODE ENTRY SERVICE DEBUG: API success, entries:', entries);

      // Salvar no localStorage para cache
      localStorage.setItem('codeEntries', JSON.stringify(entries));

      return entries;
    } catch (error) {
      console.error('Get code entries error:', error);

      // Fallback para localStorage
      console.log('🔍 CODE ENTRY SERVICE DEBUG: Error, trying localStorage');
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          return entries;
        } catch (error) {
          console.error('Failed to parse stored code entries:', error);
        }
      }
      return [];
    }
  },

  /**
   * Get a specific code entry by ID
   */
  async getCodeEntry(entryId: string): Promise<CodeEntry | null> {
    const { token, isAuthenticated } = useAuthStore.getState();

    if (!token || !isAuthenticated) {
      // Tentar obter do localStorage
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          return entries.find((entry: CodeEntry) => entry.id === entryId) || null;
        } catch (error) {
          console.error('Failed to parse stored code entries:', error);
        }
      }
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/code-entries/${entryId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('Get code entry failed:', response.status);
        return null;
      }

      return response.json();
    } catch (error) {
      console.error('Get code entry error:', error);

      // Fallback para localStorage
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          return entries.find((entry: CodeEntry) => entry.id === entryId) || null;
        } catch (error) {
          console.error('Failed to parse stored code entries:', error);
        }
      }
      return null;
    }
  },

  /**
   * Delete a code entry (soft delete)
   */
  async deleteCodeEntry(entryId: string): Promise<CodeEntryDeleteResponse> {
    const { token, isAuthenticated } = useAuthStore.getState();

    if (!token || !isAuthenticated) {
      // Remover do localStorage
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          const updatedEntries = entries.filter((entry: CodeEntry) => entry.id !== entryId);
          localStorage.setItem('codeEntries', JSON.stringify(updatedEntries));
          return { message: 'Code entry deleted successfully', success: true };
        } catch (error) {
          console.error('Failed to delete from localStorage:', error);
          return { message: 'Failed to delete code entry', success: false };
        }
      }
      return { message: 'Code entry not found', success: false };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/code-entries/${entryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Delete code entry failed:', response.status, errorText);

        // Fallback para localStorage
        const storedEntries = localStorage.getItem('codeEntries');
        if (storedEntries) {
          try {
            const entries = JSON.parse(storedEntries);
            const updatedEntries = entries.filter((entry: CodeEntry) => entry.id !== entryId);
            localStorage.setItem('codeEntries', JSON.stringify(updatedEntries));
            return { message: 'Code entry deleted successfully (local)', success: true };
          } catch (error) {
            console.error('Failed to delete from localStorage:', error);
          }
        }
        return { message: 'Failed to delete code entry', success: false };
      }

      const result = await response.json();

      // Remover do cache do localStorage
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          const updatedEntries = entries.filter((entry: CodeEntry) => entry.id !== entryId);
          localStorage.setItem('codeEntries', JSON.stringify(updatedEntries));
        } catch (error) {
          console.error('Failed to update localStorage cache:', error);
        }
      }

      return result;
    } catch (error) {
      console.error('Delete code entry error:', error);

      // Fallback para localStorage
      const storedEntries = localStorage.getItem('codeEntries');
      if (storedEntries) {
        try {
          const entries = JSON.parse(storedEntries);
          const updatedEntries = entries.filter((entry: CodeEntry) => entry.id !== entryId);
          localStorage.setItem('codeEntries', JSON.stringify(updatedEntries));
          return { message: 'Code entry deleted successfully (local)', success: true };
        } catch (error) {
          console.error('Failed to delete from localStorage:', error);
        }
      }
      return { message: 'Failed to delete code entry', success: false };
    }
  },

  /**
   * Count lines in code content
   */
  countLines(codeContent: string): number {
    return codeContent.split('\n').length;
  },

  /**
   * Count characters in code content
   */
  countCharacters(codeContent: string): number {
    return codeContent.length;
  },

  /**
   * Generate automatic title if not provided
   */
  generateAutoTitle(codeContent: string, language?: string): string {
    const date = new Date().toISOString();
    const languageName = language ? language.toUpperCase() : 'CODE';
    return `${languageName} - ${date}`;
  },

  /**
   * Validate code content
   */
  validateCodeContent(codeContent: string): { isValid: boolean; error?: string } {
    if (!codeContent || codeContent.trim() === '') {
      return { isValid: false, error: 'Code content cannot be empty' };
    }
    return { isValid: true };
  },

  /**
   * Validate title
   */
  validateTitle(title: string): { isValid: boolean; error?: string } {
    if (!title || title.trim() === '') {
      return { isValid: false, error: 'Title cannot be empty' };
    }
    if (title.length > 500) {
      return { isValid: false, error: 'Title cannot exceed 500 characters' };
    }
    return { isValid: true };
  }
};