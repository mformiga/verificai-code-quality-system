/**
 * Types for code entry functionality
 */

export interface CodeEntry {
  id: string;
  code_content: string;
  title: string;
  description?: string;
  language?: string;
  lines_count: number;
  characters_count: number;
  created_at: string;
  updated_at: string;
  user_id: number;
  is_active: boolean;
}

export interface CodeEntryList {
  id: string;
  title: string;
  description?: string;
  language?: string;
  lines_count: number;
  characters_count: number;
  created_at: string;
  is_active: boolean;
}

export interface CodeEntryCreate {
  code_content: string;
  title: string;
  description?: string;
  language?: string;
  lines_count: number;
  characters_count: number;
}

export interface CodeEntryUpdate {
  title?: string;
  description?: string;
  language?: string;
  is_active?: boolean;
}

export interface CodeLanguageDetection {
  language: string;
  confidence?: number;
}

export interface CodeEntryDeleteResponse {
  message: string;
  success: boolean;
}

export interface CodeEntryStats {
  [language: string]: number;
}