# User Story: General Criteria Analysis Interface

**ID:** STO-007
**Epic:** Epic 5 - Document Upload & Analysis Interfaces
**Priority:** High
**Estimate:** 5 days
**Status:** Ready for Development

## Description

Como um usuário de QA,
Quero acessar uma tela dedicada para configurar critérios gerais de avaliação e ver os resultados da análise por IA,
Para que possa avaliar o código-fonte baseado em padrões de qualidade gerais definidos por mim.

## Acceptance Criteria

1. **[ ]** Tela dedicada implementada com área para configuração de critérios gerais
2. **[ ]** Botão para iniciar análise usando o prompt configurado de critérios gerais
3. **[ ]** Interface de progresso mostrando status da análise em tempo real
4. **[ ]** Exibição dos resultados da análise de critérios gerais formatados em Markdown
5. **[ ]** Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis
6. **[ ]** Botão para download do relatório de análise em formato Markdown
7. **[ ]** Sistema mostrando apenas a última análise realizada na tela
8. **[ ]** Sistema apresenta o resultado da análise ao lado de cada critério definido pelo QA

## Technical Specifications

### Component Architecture
```typescript
// components/features/Analysis/GeneralAnalysisPage.tsx
interface GeneralAnalysisProps {
  uploadedFiles: UploadedFile[];
  prompts: PromptConfig;
}

interface AnalysisResult {
  id: string;
  analysisType: 'general';
  timestamp: Date;
  overallAssessment: string;
  criteriaResults: CriteriaResult[];
  tokenUsage: TokenUsage;
  processingTime: number;
  status: AnalysisStatus;
}

interface CriteriaResult {
  criterion: string;
  assessment: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  confidence: number;
  evidence: CodeEvidence[];
  recommendations: string[];
}
```

### Sub-components
1. **CriteriaList**: Display and manage evaluation criteria
2. **AnalysisControls**: Start analysis, download, manual edit buttons
3. **ProgressTracker**: Real-time analysis progress visualization
4. **ResultsTable**: Table-based results display with markdown support
5. **ManualEditor**: Rich text editor for manual result editing
6. **ReportGenerator**: Generate and download analysis reports

### State Management
```typescript
// stores/analysisStore.ts
interface AnalysisState {
  currentAnalysis: AnalysisResult | null;
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  criteria: Criterion[];
  isManualMode: boolean;
}

const useAnalysisStore = create<AnalysisState>((set, get) => ({
  // Initial state
  currentAnalysis: null,
  isAnalyzing: false,
  progress: 0,
  error: null,
  criteria: [],
  isManualMode: false,

  // Actions
  startAnalysis: async (config: AnalysisConfig) => {
    set({ isAnalyzing: true, progress: 0, error: null });
    try {
      const result = await analysisService.startGeneralAnalysis(config);
      set({ currentAnalysis: result, isAnalyzing: false, progress: 100 });
    } catch (error) {
      set({ error: error.message, isAnalyzing: false });
    }
  },

  updateProgress: (progress: number) => {
    set({ progress });
  },

  setManualMode: (enabled: boolean) => {
    set({ isManualMode: enabled });
  },

  updateCriteriaResult: (criterionId: string, result: Partial<CriteriaResult>) => {
    set((state) => ({
      currentAnalysis: state.currentAnalysis ? {
        ...state.currentAnalysis,
        criteriaResults: state.currentAnalysis.criteriaResults.map(cr =>
          cr.criterion === criterionId ? { ...cr, ...result } : cr
        )
      } : null
    }));
  },
}));
```

### Data Flow
```
User Action → API Request → Analysis Queue → LLM Processing → Result Aggregation → UI Update
```

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003, STO-004, STO-005, STO-006
- **Blocked by**: None
- **Blocking**: STO-008, STO-009

## Testing Strategy

1. **Unit Tests**: Test individual components and state management
2. **Integration Tests**: Test analysis workflow and backend integration
3. **User Interface Tests**: Test user interactions and workflows
4. **Performance Tests**: Test analysis performance and UI responsiveness
5. **Error Handling Tests**: Test various error scenarios

### Test Cases
- Start analysis with valid criteria
- Monitor analysis progress in real-time
- View and navigate through results
- Edit results manually
- Download analysis report
- Handle API failures gracefully
- Test with various codebase sizes
- Validate markdown rendering

## Implementation Details

### Criteria Management
```typescript
// components/features/Analysis/CriteriaList.tsx
interface CriteriaListProps {
  criteria: Criterion[];
  onCriteriaChange: (criteria: Criterion[]) => void;
  onCriteriaSelect: (selected: string[]) => void;
}

const CriteriaList: React.FC<CriteriaListProps> = ({
  criteria,
  onCriteriaChange,
  onCriteriaSelect
}) => {
  const [editingCriterion, setEditingCriterion] = useState<string | null>(null);

  const addCriterion = () => {
    const newCriterion: Criterion = {
      id: uuid(),
      text: '',
      active: true,
      createdAt: new Date()
    };
    onCriteriaChange([...criteria, newCriterion]);
  };

  const updateCriterion = (id: string, updates: Partial<Criterion>) => {
    onCriteriaChange(criteria.map(c =>
      c.id === id ? { ...c, ...updates } : c
    ));
  };

  const deleteCriterion = (id: string) => {
    onCriteriaChange(criteria.filter(c => c.id !== id));
  };

  return (
    <div className="criteria-list">
      <div className="criteria-header">
        <h3>Critérios de Avaliação</h3>
        <button onClick={addCriterion} className="btn-primary">
          <AddIcon /> Novo Critério
        </button>
      </div>

      <div className="criteria-items">
        {criteria.map((criterion) => (
          <CriteriaItem
            key={criterion.id}
            criterion={criterion}
            isEditing={editingCriterion === criterion.id}
            onEdit={(updates) => updateCriterion(criterion.id, updates)}
            onDelete={() => deleteCriterion(criterion.id)}
            onToggleEdit={() => setEditingCriterion(
              editingCriterion === criterion.id ? null : criterion.id
            )}
          />
        ))}
      </div>
    </div>
  );
};
```

### Results Table Component
```typescript
// components/features/Analysis/ResultsTable.tsx
interface ResultsTableProps {
  results: CriteriaResult[];
  onEditResult: (criterion: string, result: Partial<CriteriaResult>) => void;
  onDownloadReport: () => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({
  results,
  onEditResult,
  onDownloadReport
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (criterion: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(criterion)) {
      newExpanded.delete(criterion);
    } else {
      newExpanded.add(criterion);
    }
    setExpandedRows(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant': return <CheckCircleIcon className="text-green-500" />;
      case 'partially_compliant': return <WarningIcon className="text-yellow-500" />;
      case 'non_compliant': return <ErrorIcon className="text-red-500" />;
      default: return <HelpIcon className="text-gray-500" />;
    }
  };

  return (
    <div className="results-table-container">
      <div className="table-header">
        <h3>Resultados da Análise</h3>
        <button onClick={onDownloadReport} className="btn-secondary">
          <DownloadIcon /> Baixar Relatório
        </button>
      </div>

      <table className="results-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Critério</th>
            <th>Avaliação</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <>
              <tr key={result.criterion} className="result-row">
                <td>{getStatusIcon(result.status)}</td>
                <td className="criterion-cell">
                  <div className="criterion-text">{result.criterion}</div>
                  <div className="confidence-indicator">
                    Confiança: {Math.round(result.confidence * 100)}%
                  </div>
                </td>
                <td className="assessment-cell">
                  <div className="assessment-summary">
                    {result.assessment.substring(0, 150)}
                    {result.assessment.length > 150 && '...'}
                  </div>
                </td>
                <td className="actions-cell">
                  <button
                    onClick={() => toggleRow(result.criterion)}
                    className="btn-icon"
                    title={expandedRows.has(result.criterion) ? 'Recolher' : 'Expandir'}
                  >
                    {expandedRows.has(result.criterion) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </button>
                  <button
                    onClick={() => onEditResult(result.criterion, result)}
                    className="btn-icon"
                    title="Editar manualmente"
                  >
                    <EditIcon />
                  </button>
                </td>
              </tr>
              {expandedRows.has(result.criterion) && (
                <tr className="expanded-row">
                  <td colSpan={4}>
                    <div className="expanded-content">
                      <div className="assessment-full">
                        <h4>Avaliação Completa</h4>
                        <MarkdownRenderer content={result.assessment} />
                      </div>

                      {result.evidence.length > 0 && (
                        <div className="evidence-section">
                          <h4>Evidências</h4>
                          {result.evidence.map((evidence, index) => (
                            <CodeBlock
                              key={index}
                              code={evidence.code}
                              language={evidence.language}
                              filePath={evidence.filePath}
                              lineNumbers={evidence.lineNumbers}
                            />
                          ))}
                        </div>
                      )}

                      {result.recommendations.length > 0 && (
                        <div className="recommendations-section">
                          <h4>Recomendações</h4>
                          <ul>
                            {result.recommendations.map((rec, index) => (
                              <li key={index}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### Manual Editor Component
```typescript
// components/features/Analysis/ManualEditor.tsx
interface ManualEditorProps {
  criterion: string;
  initialResult: CriteriaResult;
  onSave: (result: CriteriaResult) => void;
  onCancel: () => void;
}

const ManualEditor: React.FC<ManualEditorProps> = ({
  criterion,
  initialResult,
  onSave,
  onCancel
}) => {
  const [result, setResult] = useState<CriteriaResult>(initialResult);

  const handleSave = () => {
    onSave(result);
  };

  return (
    <div className="manual-editor-modal">
      <div className="modal-header">
        <h3>Editar Resultado Manualmente</h3>
        <button onClick={onCancel} className="btn-icon">
          <CloseIcon />
        </button>
      </div>

      <div className="modal-content">
        <div className="form-group">
          <label>Status</label>
          <select
            value={result.status}
            onChange={(e) => setResult({
              ...result,
              status: e.target.value as CriteriaResult['status']
            })}
          >
            <option value="compliant">Conforme</option>
            <option value="partially_compliant">Parcialmente Conforme</option>
            <option value="non_compliant">Não Conforme</option>
          </select>
        </div>

        <div className="form-group">
          <label>Avaliação</label>
          <MarkdownEditor
            value={result.assessment}
            onChange={(assessment) => setResult({ ...result, assessment })}
            placeholder="Descreva a avaliação do critério..."
          />
        </div>

        <div className="form-group">
          <label>Nível de Confiança</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={result.confidence}
            onChange={(e) => setResult({
              ...result,
              confidence: parseFloat(e.target.value)
            })}
          />
          <span>{Math.round(result.confidence * 100)}%</span>
        </div>

        <div className="form-actions">
          <button onClick={onCancel} className="btn-secondary">
            Cancelar
          </button>
          <button onClick={handleSave} className="btn-primary">
            Salvar
          </button>
        </div>
      </div>
    </div>
  );
};
```

### Real-time Progress Tracking
```typescript
// components/features/Analysis/ProgressTracker.tsx
interface ProgressTrackerProps {
  progress: number;
  status: AnalysisStatus;
  message?: string;
  onCancel: () => void;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progress,
  status,
  message,
  onCancel
}) => {
  const getStatusMessage = () => {
    switch (status) {
      case 'queued': return 'Análise na fila...';
      case 'processing': return `Processando análise... ${progress}%`;
      case 'completed': return 'Análise concluída!';
      case 'failed': return 'Análise falhou';
      case 'cancelled': return 'Análise cancelada';
      default: return message || 'Preparando análise...';
    }
  };

  return (
    <div className="progress-tracker">
      <div className="progress-header">
        <h3>Status da Análise</h3>
        {status === 'processing' && (
          <button onClick={onCancel} className="btn-danger">
            Cancelar
          </button>
        )}
      </div>

      <div className="progress-content">
        <div className="progress-bar-container">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="progress-info">
          <span className="progress-message">{getStatusMessage()}</span>
          <span className="progress-percentage">{progress}%</span>
        </div>

        {status === 'processing' && (
          <div className="progress-details">
            <div className="progress-step">
              <CheckCircleIcon className={progress > 20 ? 'active' : ''} />
              <span>Preparando arquivos</span>
            </div>
            <div className="progress-step">
              <CheckCircleIcon className={progress > 40 ? 'active' : ''} />
              <span>Otimizando conteúdo</span>
            </div>
            <div className="progress-step">
              <CheckCircleIcon className={progress > 60 ? 'active' : ''} />
              <span>Analisando com IA</span>
            </div>
            <div className="progress-step">
              <CheckCircleIcon className={progress > 80 ? 'active' : ''} />
              <span>Processando resultados</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
```

## Error Handling

### API Failures
- Detect when LLM APIs are unavailable
- Automatically switch to manual mode
- Provide clear error messages to users
- Offer retry options when appropriate

### Network Issues
- Handle network interruptions gracefully
- Implement retry logic with exponential backoff
- Show offline/online status indicators
- Cache results when possible

### Validation Errors
- Validate analysis configuration before submission
- Provide clear validation feedback
- Prevent invalid state transitions
- Handle edge cases appropriately

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader Support**: ARIA labels and live regions for updates
- **Focus Management**: Proper focus states and traps for modals
- **High Contrast**: Support for high contrast themes
- **Error Announcements**: Screen reader announcements for errors and progress

## Performance Considerations

- **Virtual Scrolling**: For large result sets
- **Lazy Loading**: Load content as needed
- **Debouncing**: For rapid user input
- **Memoization**: For expensive component renders
- **Code Splitting**: For optimal bundle size

## Security Considerations

- **Input Validation**: Sanitize all user inputs
- **XSS Prevention**: Proper escaping of dynamic content
- **CSRF Protection**: For all form submissions
- **Content Security Policy**: Appropriate CSP headers
- **Authentication**: Verify user permissions for actions

## Notes

- Consider implementing analysis templates
- Add support for bulk criteria operations
- Include export to different formats (PDF, Excel)
- Consider adding analysis scheduling
- Plan for collaborative analysis features

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All unit and integration tests passing
- [ ] Accessibility audit passes
- [ ] Performance benchmarks met
- [ ] Code review completed and approved
- [ ] User acceptance testing completed
- [ ] Security scan passes
- [ ] Documentation updated
- [ ] Cross-browser testing completed