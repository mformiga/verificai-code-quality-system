import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { codeEntryService } from './codeEntryService';
import { CodeEntry, CreateCodeEntryRequest, UpdateCodeEntryRequest } from '@/types/codeEntry';

// Mock do fetch global
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('CodeEntryService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all code entries successfully', async () => {
      const mockCodeEntries: CodeEntry[] = [
        {
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
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCodeEntries,
      });

      const result = await codeEntryService.getAll();

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockCodeEntries);
    });

    it('should handle fetch error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ message: 'Internal server error' }),
      });

      await expect(codeEntryService.getAll()).rejects.toThrow('Failed to fetch code entries');
    });

    it('should handle network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(codeEntryService.getAll()).rejects.toThrow('Network error');
    });
  });

  describe('getById', () => {
    it('should fetch code entry by id successfully', async () => {
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

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCodeEntry,
      });

      const result = await codeEntryService.getById('1');

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries/1', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockCodeEntry);
    });

    it('should handle 404 error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Code entry not found' }),
      });

      await expect(codeEntryService.getById('999')).rejects.toThrow('Failed to fetch code entry');
    });
  });

  describe('create', () => {
    it('should create code entry successfully', async () => {
      const createRequest: CreateCodeEntryRequest = {
        codeContent: 'console.log("Hello World");',
        title: 'Test JavaScript',
        description: 'A simple JS code',
        language: 'javascript',
      };

      const mockCreatedEntry: CodeEntry = {
        id: '1',
        ...createRequest,
        linesCount: 1,
        charactersCount: 25,
        createdAt: new Date('2023-12-08T10:00:00Z'),
        updatedAt: new Date('2023-12-08T10:00:00Z'),
        userId: 'user1',
        isActive: true
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCreatedEntry,
      });

      const result = await codeEntryService.create(createRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createRequest),
      });
      expect(result).toEqual(mockCreatedEntry);
    });

    it('should handle validation error', async () => {
      const invalidRequest: CreateCodeEntryRequest = {
        codeContent: '',
        title: '',
        language: '',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Invalid input' }),
      });

      await expect(codeEntryService.create(invalidRequest)).rejects.toThrow('Failed to create code entry');
    });
  });

  describe('update', () => {
    it('should update code entry successfully', async () => {
      const updateRequest: UpdateCodeEntryRequest = {
        title: 'Updated Title',
        description: 'Updated description',
      };

      const mockUpdatedEntry: CodeEntry = {
        id: '1',
        codeContent: 'console.log("Hello World");',
        title: 'Updated Title',
        description: 'Updated description',
        language: 'javascript',
        linesCount: 1,
        charactersCount: 25,
        createdAt: new Date('2023-12-08T10:00:00Z'),
        updatedAt: new Date('2023-12-08T11:00:00Z'),
        userId: 'user1',
        isActive: true
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockUpdatedEntry,
      });

      const result = await codeEntryService.update('1', updateRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateRequest),
      });
      expect(result).toEqual(mockUpdatedEntry);
    });

    it('should handle update error', async () => {
      const updateRequest: UpdateCodeEntryRequest = {
        title: 'Updated Title',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Code entry not found' }),
      });

      await expect(codeEntryService.update('999', updateRequest)).rejects.toThrow('Failed to update code entry');
    });
  });

  describe('delete', () => {
    it('should delete code entry successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Code entry deleted successfully' }),
      });

      await expect(codeEntryService.delete('1')).resolves.not.toThrow();

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries/1', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should handle delete error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Code entry not found' }),
      });

      await expect(codeEntryService.delete('999')).rejects.toThrow('Failed to delete code entry');
    });
  });

  describe('detectLanguage', () => {
    it('should detect language successfully', async () => {
      const code = 'console.log("Hello World");';
      const mockResponse = { language: 'javascript', confidence: 0.95 };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await codeEntryService.detectLanguage(code);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries/detect-language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle language detection error', async () => {
      const code = 'invalid code';

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Invalid code' }),
      });

      await expect(codeEntryService.detectLanguage(code)).rejects.toThrow('Failed to detect language');
    });
  });

  describe('getStats', () => {
    it('should fetch statistics successfully', async () => {
      const mockStats = {
        totalEntries: 100,
        totalLines: 5000,
        totalCharacters: 100000,
        languages: {
          javascript: 40,
          python: 30,
          typescript: 20,
          other: 10
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      });

      const result = await codeEntryService.getStats();

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/code-entries/stats', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockStats);
    });

    it('should handle stats fetch error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ message: 'Internal server error' }),
      });

      await expect(codeEntryService.getStats()).rejects.toThrow('Failed to fetch code entry statistics');
    });
  });
});