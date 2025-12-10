/**
 * Hook for managing code entries
 */

import { useState, useEffect, useCallback } from 'react';
import codeEntryService from '../services/codeEntryService';
import {
  CodeEntry,
  CodeEntryList,
  CodeEntryCreate,
  CodeLanguageDetection,
  CodeEntryDeleteResponse
} from '../types/codeEntry';

interface UseCodeEntriesOptions {
  autoLoad?: boolean;
  pageSize?: number;
}

interface UseCodeEntriesReturn {
  // Data
  codeEntries: CodeEntryList[];
  currentEntry: CodeEntry | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;

  // Pagination
  currentPage: number;
  hasMore: boolean;

  // Actions
  loadCodeEntries: (refresh?: boolean) => Promise<void>;
  loadMoreEntries: () => Promise<void>;
  createCodeEntry: (data: CodeEntryCreate) => Promise<CodeEntry | null>;
  detectLanguage: (code: string) => Promise<CodeLanguageDetection>;
  getEntryById: (id: string) => Promise<CodeEntry | null>;
  deleteEntry: (id: string) => Promise<boolean>;
  clearError: () => void;
  setCurrentEntry: (entry: CodeEntry | null) => void;
}

export const useCodeEntries = (options: UseCodeEntriesOptions = {}): UseCodeEntriesReturn => {
  const { autoLoad = true, pageSize = 20 } = options;

  // State
  const [codeEntries, setCodeEntries] = useState<CodeEntryList[]>([]);
  const [currentEntry, setCurrentEntry] = useState<CodeEntry | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  // Clear error helper
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load code entries
  const loadCodeEntries = useCallback(async (refresh = false) => {
    try {
      setIsLoading(true);
      clearError();

      const page = refresh ? 0 : currentPage;
      const entries = await codeEntryService.getCodeEntries({
        skip: page * pageSize,
        limit: pageSize
      });

      if (refresh) {
        setCodeEntries(entries);
        setCurrentPage(0);
      } else {
        setCodeEntries(prev => page === 0 ? entries : [...prev, ...entries]);
      }

      // Check if there are more entries
      setHasMore(entries.length === pageSize);

      if (!refresh) {
        setCurrentPage(page + 1);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load code entries';
      setError(errorMessage);
      console.error('Error loading code entries:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, clearError]);

  // Load more entries
  const loadMoreEntries = useCallback(async () => {
    if (!hasMore || isLoading) return;
    await loadCodeEntries(false);
  }, [hasMore, isLoading, loadCodeEntries]);

  // Create code entry
  const createCodeEntry = useCallback(async (data: CodeEntryCreate): Promise<CodeEntry | null> => {
    try {
      setIsSaving(true);
      clearError();

      const newEntry = await codeEntryService.createCodeEntry(data);

      // Add to the beginning of the list
      setCodeEntries(prev => [newEntry, ...prev]);

      return newEntry;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create code entry';
      setError(errorMessage);
      console.error('Error creating code entry:', err);
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [clearError]);

  // Detect language
  const detectLanguage = useCallback(async (code: string): Promise<CodeLanguageDetection> => {
    try {
      clearError();
      return await codeEntryService.detectLanguage(code);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to detect language';
      setError(errorMessage);
      console.error('Error detecting language:', err);
      // Return default language if detection fails
      return { language: 'text' };
    }
  }, [clearError]);

  // Get entry by ID
  const getEntryById = useCallback(async (id: string): Promise<CodeEntry | null> => {
    try {
      clearError();
      const entry = await codeEntryService.getCodeEntry(id);
      setCurrentEntry(entry);
      return entry;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load code entry';
      setError(errorMessage);
      console.error('Error loading code entry:', err);
      return null;
    }
  }, [clearError]);

  // Delete entry
  const deleteEntry = useCallback(async (id: string): Promise<boolean> => {
    try {
      clearError();

      // Confirm deletion
      const confirmed = window.confirm('Are you sure you want to delete this code entry?');
      if (!confirmed) return false;

      const response = await codeEntryService.deleteCodeEntry(id);

      if (response.success) {
        // Remove from list
        setCodeEntries(prev => prev.filter(entry => entry.id !== id));

        // Clear current entry if it was the deleted one
        if (currentEntry?.id === id) {
          setCurrentEntry(null);
        }

        return true;
      } else {
        setError(response.message);
        return false;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete code entry';
      setError(errorMessage);
      console.error('Error deleting code entry:', err);
      return false;
    }
  }, [clearError, currentEntry]);

  // Auto-load on mount
  useEffect(() => {
    if (autoLoad) {
      loadCodeEntries(true);
    }
  }, [autoLoad, loadCodeEntries]);

  return {
    // Data
    codeEntries,
    currentEntry,
    isLoading,
    isSaving,
    error,

    // Pagination
    currentPage,
    hasMore,

    // Actions
    loadCodeEntries,
    loadMoreEntries,
    createCodeEntry,
    detectLanguage,
    getEntryById,
    deleteEntry,
    clearError,
    setCurrentEntry
  };
};

export default useCodeEntries;