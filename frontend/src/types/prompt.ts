export interface Prompt {
  id: string;
  name: string;
  type: 'general' | 'architectural' | 'business';
  description: string;
  content: string;
  isActive: boolean;
  isDefault: boolean;
  version?: number;
  createdAt: Date;
  updatedAt: Date;
  createdBy?: string;
}

export interface PromptConfig {
  general: Prompt;
  architectural: Prompt;
  business: Prompt;
}

export interface PromptVersion {
  version: number;
  content: string;
  createdAt: Date;
  author: string;
  changeDescription?: string;
}

export interface PromptResponse {
  id: string;
  type: 'general' | 'architectural' | 'business';
  content: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  author: string;
  history: PromptVersion[];
}

export type PromptType = keyof PromptConfig;

export interface PromptState {
  prompts: PromptConfig;
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  error: string | null;
  autoSaveTimer: any | null;
  activePromptType: PromptType;
  updatePrompt: (type: PromptType, content: string) => void;
  setActivePromptType: (type: PromptType) => void;
  triggerAutoSave: () => void;
  savePrompts: () => Promise<void>;
  discardChanges: () => Promise<void>;
  restoreDefaults: () => Promise<void>;
  loadPrompts: () => Promise<void>;
  clearAutoSaveTimer: () => void;
  reset: () => void;
  getVersionHistory: (promptType: PromptType) => Promise<PromptVersion[]>;
  restoreVersion: (promptType: PromptType, version: number) => Promise<void>;
  createVersionBackup: () => Promise<void>;
}

export interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: 'plaintext' | 'markdown' | 'json';
  placeholder?: string;
  disabled?: boolean;
}

export interface AutoSaveIndicatorProps {
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
}

export interface VersionHistoryProps {
  versions: PromptVersion[];
  onRestore: (version: number) => void;
  currentVersion: number;
}

export interface PromptToolbarProps {
  onSave: () => void;
  onDiscard: () => void;
  onRestoreDefaults: () => void;
  isSaving: boolean;
  hasUnsavedChanges: boolean;
  disabled?: boolean;
}

export interface PromptTemplate {
  id: string;
  name: string;
  category: string;
  template: string;
  variables: PromptVariable[];
  isActive: boolean;
}

export interface PromptVariable {
  name: string;
  type: 'text' | 'select' | 'number' | 'boolean';
  description: string;
  required: boolean;
  defaultValue?: any;
  options?: string[];
}

export interface PromptCategory {
  id: string;
  name: string;
  description: string;
  color: string;
  icon?: string;
}

export interface PromptExecution {
  id: string;
  promptId: string;
  input: string;
  context?: any;
  result: string;
  executionTime: number;
  tokensUsed: number;
  cost?: number;
  createdAt: Date;
}