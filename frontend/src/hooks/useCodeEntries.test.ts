import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCodeEntries } from './useCodeEntries';
import { codeEntryService } from '@/services/codeEntryService';
import { CodeEntry, CreateCodeEntryRequest } from '@/types/codeEntry';

// Mock do service
vi.mock('@/services/codeEntryService');

describe('useCodeEntries', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

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

  describe('initial state', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() => useCodeEntries());

      expect(result.current.codeEntries).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.currentPage).toBe(1);
      expect(result.current.totalPages).toBe(1);
      expect(result.current.totalCount).toBe(0);
      expect(typeof result.current.fetchCodeEntries).toBe('function');
      expect(typeof result.current.createCodeEntry).toBe('function');
      expect(typeof result.current.updateCodeEntry).toBe('function');
      expect(typeof result.current.deleteCodeEntry).toBe('function');
      expect(typeof result.current.detectLanguage).toBe('function');
      expect(typeof result.current.clearError).toBe('function');
      expect(typeof result.current.setPage).toBe('function');
    });
  });

  describe('fetchCodeEntries', () => {
    it('should fetch code entries successfully', async () => {
      const mockCodeEntries = [mockCodeEntry];
      vi.mocked(codeEntryService.getAll).mockResolvedValueOnce(mockCodeEntries);

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<void>;
      act(() => {
        promise = result.current.fetchCodeEntries();
      });

      await act(async () => {
        await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.codeEntries).toEqual(mockCodeEntries);
      expect(result.current.error).toBe(null);
      expect(codeEntryService.getAll).toHaveBeenCalledTimes(1);
    });

    it('should handle fetch error', async () => {
      const errorMessage = 'Failed to fetch code entries';
      vi.mocked(codeEntryService.getAll).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<void>;
      act(() => {
        promise = result.current.fetchCodeEntries();
      });

      await act(async () => {
        await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.codeEntries).toEqual([]);
      expect(result.current.error).toBe(errorMessage);
    });

    it('should set loading state during fetch', async () => {
      vi.mocked(codeEntryService.getAll).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve([mockCodeEntry]), 100))
      );

      const { result } = renderHook(() => useCodeEntries());

      act(() => {
        result.current.fetchCodeEntries();
      });

      expect(result.current.isLoading).toBe(true);

      act(() => {
        vi.advanceTimersByTime(100);
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.codeEntries).toEqual([mockCodeEntry]);
    });
  });

  describe('createCodeEntry', () => {
    it('should create code entry successfully', async () => {
      const createRequest: CreateCodeEntryRequest = {
        codeContent: 'console.log("New code");',
        title: 'New Entry',
        language: 'javascript',
      };

      vi.mocked(codeEntryService.create).mockResolvedValueOnce(mockCodeEntry);

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<CodeEntry | null>;
      act(() => {
        promise = result.current.createCodeEntry(createRequest);
      });

      const createdEntry = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(createdEntry).toEqual(mockCodeEntry);
      expect(codeEntryService.create).toHaveBeenCalledWith(createRequest);
    });

    it('should handle create error', async () => {
      const createRequest: CreateCodeEntryRequest = {
        codeContent: 'console.log("New code");',
        title: 'New Entry',
        language: 'javascript',
      };

      const errorMessage = 'Failed to create code entry';
      vi.mocked(codeEntryService.create).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<CodeEntry | null>;
      act(() => {
        promise = result.current.createCodeEntry(createRequest);
      });

      const createdEntry = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
      expect(createdEntry).toBe(null);
    });

    it('should set loading state during create', async () => {
      const createRequest: CreateCodeEntryRequest = {
        codeContent: 'console.log("New code");',
        title: 'New Entry',
        language: 'javascript',
      };

      vi.mocked(codeEntryService.create).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockCodeEntry), 100))
      );

      const { result } = renderHook(() => useCodeEntries());

      act(() => {
        result.current.createCodeEntry(createRequest);
      });

      expect(result.current.isLoading).toBe(true);

      act(() => {
        vi.advanceTimersByTime(100);
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('updateCodeEntry', () => {
    it('should update code entry successfully', async () => {
      const updateRequest = {
        title: 'Updated Title',
        description: 'Updated description',
      };

      const updatedEntry = { ...mockCodeEntry, ...updateRequest };
      vi.mocked(codeEntryService.update).mockResolvedValueOnce(updatedEntry);

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<CodeEntry | null>;
      act(() => {
        promise = result.current.updateCodeEntry('1', updateRequest);
      });

      const resultEntry = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(resultEntry).toEqual(updatedEntry);
      expect(codeEntryService.update).toHaveBeenCalledWith('1', updateRequest);
    });

    it('should handle update error', async () => {
      const updateRequest = {
        title: 'Updated Title',
      };

      const errorMessage = 'Failed to update code entry';
      vi.mocked(codeEntryService.update).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<CodeEntry | null>;
      act(() => {
        promise = result.current.updateCodeEntry('1', updateRequest);
      });

      const resultEntry = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
      expect(resultEntry).toBe(null);
    });
  });

  describe('deleteCodeEntry', () => {
    it('should delete code entry successfully', async () => {
      vi.mocked(codeEntryService.delete).mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<boolean>;
      act(() => {
        promise = result.current.deleteCodeEntry('1');
      });

      const deleteResult = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(deleteResult).toBe(true);
      expect(codeEntryService.delete).toHaveBeenCalledWith('1');
    });

    it('should handle delete error', async () => {
      const errorMessage = 'Failed to delete code entry';
      vi.mocked(codeEntryService.delete).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<boolean>;
      act(() => {
        promise = result.current.deleteCodeEntry('1');
      });

      const deleteResult = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
      expect(deleteResult).toBe(false);
    });
  });

  describe('detectLanguage', () => {
    it('should detect language successfully', async () => {
      const code = 'console.log("Hello World");';
      const mockResponse = { language: 'javascript', confidence: 0.95 };

      vi.mocked(codeEntryService.detectLanguage).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<{ language: string; confidence: number } | null>;
      act(() => {
        promise = result.current.detectLanguage(code);
      });

      const detectionResult = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(detectionResult).toEqual(mockResponse);
      expect(codeEntryService.detectLanguage).toHaveBeenCalledWith(code);
    });

    it('should handle language detection error', async () => {
      const code = 'invalid code';
      const errorMessage = 'Failed to detect language';
      vi.mocked(codeEntryService.detectLanguage).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useCodeEntries());

      let promise: Promise<{ language: string; confidence: number } | null>;
      act(() => {
        promise = result.current.detectLanguage(code);
      });

      const detectionResult = await act(async () => {
        return await promise;
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
      expect(detectionResult).toBe(null);
    });
  });

  describe('clearError', () => {
    it('should clear error state', () => {
      const { result } = renderHook(() => useCodeEntries());

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBe(null);
    });
  });

  describe('setPage', () => {
    it('should set page correctly', () => {
      const { result } = renderHook(() => useCodeEntries());

      act(() => {
        result.current.setPage(2);
      });

      expect(result.current.currentPage).toBe(2);
    });

    it('should not set page less than 1', () => {
      const { result } = renderHook(() => useCodeEntries());

      act(() => {
        result.current.setPage(0);
      });

      expect(result.current.currentPage).toBe(1);
    });
  });

  describe('optimistic updates', () => {
    it('should remove code entry optimistically on delete', async () => {
      const initialEntries = [mockCodeEntry];
      vi.mocked(codeEntryService.getAll).mockResolvedValueOnce(initialEntries);
      vi.mocked(codeEntryService.delete).mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useCodeEntries());

      // First, load the entries
      let promise: Promise<void>;
      act(() => {
        promise = result.current.fetchCodeEntries();
      });

      await act(async () => {
        await promise;
      });

      expect(result.current.codeEntries).toEqual(initialEntries);

      // Then delete one entry
      act(() => {
        promise = result.current.deleteCodeEntry('1');
      });

      // Check optimistic update
      expect(result.current.codeEntries).toEqual([]);

      await act(async () => {
        await promise;
      });

      expect(result.current.codeEntries).toEqual([]);
    });

    it('should restore code entry on delete failure', async () => {
      const initialEntries = [mockCodeEntry];
      vi.mocked(codeEntryService.getAll).mockResolvedValueOnce(initialEntries);
      vi.mocked(codeEntryService.delete).mockRejectedValueOnce(new Error('Delete failed'));

      const { result } = renderHook(() => useCodeEntries());

      // First, load the entries
      let promise: Promise<void>;
      act(() => {
        promise = result.current.fetchCodeEntries();
      });

      await act(async () => {
        await promise;
      });

      expect(result.current.codeEntries).toEqual(initialEntries);

      // Then try to delete one entry
      act(() => {
        promise = result.current.deleteCodeEntry('1');
      });

      // Check optimistic update
      expect(result.current.codeEntries).toEqual([]);

      await act(async () => {
        await promise;
      });

      // Check restoration
      expect(result.current.codeEntries).toEqual(initialEntries);
      expect(result.current.error).toBe('Delete failed');
    });
  });
});