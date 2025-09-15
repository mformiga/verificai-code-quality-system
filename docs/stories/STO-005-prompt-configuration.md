# User Story: Prompt Configuration Interface

**ID:** STO-005
**Epic:** Epic 3 - Prompt Management & Configuration System
**Priority:** High
**Estimate:** 4 days
**Status:** Ready for Development

## Description

Como um usuário de QA,
Quero acessar uma tela dedicada para configurar e editar os três tipos de prompts de análise,
Para que possa personalizar como o sistema avaliará o código-fonte.

## Acceptance Criteria

1. **[ ]** Tela dedicada de edição de prompts implementada com layout claro e organizado
2. **[ ]** Três seções distintas para cada tipo de prompt: Critérios Gerais, Conformidade Arquitetural, Conformidade Negocial
3. **[ ]** Editor de texto com syntax highlighting para melhor legibilidade dos prompts
4. **[ ]** Sistema de autosalvamento automático a cada 30 segundos
5. **[ ]** Botões manuais para salvar, descartar alterações e restaurar padrões
6. **[ ]** Indicadores visuais de status (salvo, não salvo, erro)
7. **[ ]** Sistema para salvar uma versão anterior do prompt antes de cada alteração

## Technical Specifications

### Component Structure
```typescript
// components/features/PromptConfig/PromptConfig.tsx
interface PromptConfigProps {
  initialPrompts?: PromptConfig;
  onSave: (prompts: PromptConfig) => void;
}

interface PromptConfig {
  general: Prompt;
  architectural: Prompt;
  business: Prompt;
}

interface Prompt {
  id: string;
  content: string;
  version: number;
  lastModified: Date;
  isDefault: boolean;
}
```

### Sub-components
1. **PromptEditor**: Text editor with syntax highlighting
2. **PromptTabs**: Tab navigation between prompt types
3. **AutoSaveIndicator**: Visual feedback for save status
4. **VersionHistory**: Display and manage prompt versions
5. **PromptToolbar**: Action buttons (save, discard, restore)

### Data Models
```typescript
// Backend API response
interface PromptResponse {
  id: string;
  type: 'general' | 'architectural' | 'business';
  content: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  author: string;
  history: PromptVersion[];
}

interface PromptVersion {
  version: number;
  content: string;
  createdAt: Date;
  author: string;
  changeDescription?: string;
}
```

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003
- **Blocked by**: None
- **Blocking**: Analysis Stories (STO-006, STO-007, STO-008)

## Testing Strategy

1. **Unit Tests**: Test individual components and state management
2. **Integration Tests**: Test API integration and data persistence
3. **User Interface Tests**: Test user interactions and workflows
4. **Performance Tests**: Test auto-save functionality and large prompts
5. **Error Handling Tests**: Test various error scenarios

### Test Cases
- Create and save new prompt
- Edit existing prompt with auto-save
- Switch between prompt types
- Restore previous version
- Discard unsaved changes
- Restore default prompts
- Handle network failures during save
- Test syntax highlighting functionality

## Implementation Details

### State Management
```typescript
// stores/promptStore.ts
interface PromptState {
  prompts: PromptConfig;
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  error: string | null;
  autoSaveTimer: NodeJS.Timeout | null;
}

const usePromptStore = create<PromptState>((set, get) => ({
  // Initial state
  prompts: {
    general: { id: '', content: '', version: 1, lastModified: new Date(), isDefault: true },
    architectural: { id: '', content: '', version: 1, lastModified: new Date(), isDefault: true },
    business: { id: '', content: '', version: 1, lastModified: new Date(), isDefault: true },
  },
  isSaving: false,
  lastSaved: null,
  hasUnsavedChanges: false,
  error: null,
  autoSaveTimer: null,

  // Actions
  updatePrompt: (type: keyof PromptConfig, content: string) => {
    set((state) => ({
      prompts: {
        ...state.prompts,
        [type]: {
          ...state.prompts[type],
          content,
          lastModified: new Date(),
        },
      },
      hasUnsavedChanges: true,
    }));

    // Trigger auto-save
    get().triggerAutoSave();
  },

  triggerAutoSave: () => {
    const state = get();
    if (state.autoSaveTimer) {
      clearTimeout(state.autoSaveTimer);
    }

    const timer = setTimeout(() => {
      get().savePrompts();
    }, 30000); // 30 seconds

    set({ autoSaveTimer: timer });
  },

  savePrompts: async () => {
    set({ isSaving: true, error: null });
    try {
      await promptService.savePrompts(get().prompts);
      set({
        isSaving: false,
        lastSaved: new Date(),
        hasUnsavedChanges: false,
        error: null
      });
    } catch (error) {
      set({ isSaving: false, error: error.message });
    }
  },
}));
```

### Syntax Highlighting Editor
```typescript
// components/features/PromptConfig/PromptEditor.tsx
interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: 'plaintext' | 'markdown' | 'json';
  placeholder?: string;
}

const PromptEditor: React.FC<PromptEditorProps> = ({
  value,
  onChange,
  language = 'markdown',
  placeholder
}) => {
  const editorRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (newValue: string) => {
    onChange(newValue);
    // Trigger syntax highlighting
    highlightSyntax(newValue);
  };

  return (
    <div className="prompt-editor">
      <div className="editor-toolbar">
        <button onClick={() => insertText('**')} title="Bold">
          <FormatBoldIcon />
        </button>
        <button onClick={() => insertText('*')} title="Italic">
          <FormatItalicIcon />
        </button>
        <button onClick={() => insertText('`')} title="Code">
          <CodeIcon />
        </button>
      </div>

      <textarea
        ref={editorRef}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={placeholder}
        className="editor-textarea"
        rows={20}
      />

      <div className="editor-footer">
        <span className="char-count">{value.length} characters</span>
        <span className="word-count">{value.split(/\s+/).length} words</span>
      </div>
    </div>
  );
};
```

### Version Management
```typescript
// services/promptService.ts
export const promptService = {
  getPrompts: async (): Promise<PromptConfig> => {
    const response = await apiClient.get('/api/prompts');
    return response.data;
  },

  savePrompts: async (prompts: PromptConfig): Promise<PromptConfig> => {
    // Create backup before saving
    await promptService.createVersionBackup(prompts);

    const response = await apiClient.post('/api/prompts', prompts);
    return response.data;
  },

  createVersionBackup: async (prompts: PromptConfig): Promise<void> => {
    await apiClient.post('/api/prompts/backup', prompts);
  },

  getVersionHistory: async (promptId: string): Promise<PromptVersion[]> => {
    const response = await apiClient.get(`/api/prompts/${promptId}/versions`);
    return response.data;
  },

  restoreVersion: async (promptId: string, version: number): Promise<Prompt> => {
    const response = await apiClient.post(`/api/prompts/${promptId}/restore`, { version });
    return response.data;
  },

  restoreDefaults: async (): Promise<PromptConfig> => {
    const response = await apiClient.post('/api/prompts/restore-defaults');
    return response.data;
  },
};
```

### Auto-save Management
```typescript
// hooks/useAutoSave.ts
const useAutoSave = (content: string, onSave: (content: string) => Promise<void>) => {
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const saveTimeout = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (saveTimeout.current) {
      clearTimeout(saveTimeout.current);
    }

    saveTimeout.current = setTimeout(async () => {
      setIsSaving(true);
      try {
        await onSave(content);
        setLastSaved(new Date());
      } catch (error) {
        console.error('Auto-save failed:', error);
      } finally {
        setIsSaving(false);
      }
    }, 30000); // 30 seconds

    return () => {
      if (saveTimeout.current) {
        clearTimeout(saveTimeout.current);
      }
    };
  }, [content, onSave]);

  return { isSaving, lastSaved };
};
```

## Error Handling

### Network Errors
- Retry mechanism with exponential backoff
- Graceful degradation when offline
- Clear error messages for users

### Validation Errors
- Real-time validation of prompt content
- Character limits and formatting checks
- Syntax validation for markdown content

### Version Conflicts
- Handle concurrent editing scenarios
- Merge conflict resolution
- User notification of conflicts

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for editor
- **Screen Reader Support**: ARIA labels and live regions
- **Focus Management**: Proper focus states and indicators
- **High Contrast**: Support for high contrast themes
- **Error Announcements**: Screen reader announcements for errors

## Performance Considerations

- **Debouncing**: Debounce auto-save to prevent excessive API calls
- **Memory Management**: Handle large prompt content efficiently
- **Caching**: Cache prompt content for better performance
- **Optimistic Updates**: Show immediate feedback for user actions

## Security Considerations

- **Input Sanitization**: Sanitize prompt content to prevent XSS
- **Content Validation**: Validate prompt content for security
- **Access Control**: Ensure only authorized users can modify prompts
- **Audit Logging**: Log all prompt modifications

## Notes

- Consider implementing collaborative editing features
- Add support for prompt templates and snippets
- Include import/export functionality for prompts
- Consider implementing AI-assisted prompt optimization
- Add prompt testing and validation features

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All unit and integration tests passing
- [ ] Accessibility audit passes
- [ ] Performance benchmarks met
- [ ] Code review completed and approved
- [ ] User acceptance testing completed
- [ ] Security scan passes
- [ ] Documentation updated