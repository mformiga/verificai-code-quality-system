# User Story: Business Document Analysis Interface

**ID:** STO-009
**Epic:** Epic 5 - Document Upload & Analysis Interfaces
**Priority:** High
**Estimate:** 4 days
**Status:** Ready for Development

## Description

Como um usuário de QA,
Quero acessar uma tela dedicada para fazer upload de documentos de negócio e ver resultados da análise semântica,
Para que possa verificar se o código-fonte está alinhado com os requisitos de negócio.

## Acceptance Criteria

1. **[ ]** Tela dedicada implementada com área de upload para documentos de negócio
2. **[ ]** Interface drag-and-drop para upload de documentos de negócio (histórias, épicos, regras)
3. **[ ]** Sistema de preview dos documentos após upload
4. **[ ]** Botão para iniciar análise semântica de negócio usando prompt específico definido na tela de prompts
5. **[ ]** Interface de progresso mostrando status da análise em tempo real
6. **[ ]** Exibição dos resultados da análise semântica formatados em Markdown
7. **[ ]** Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis ou precisa alterar o resultado da análise feita pela IA
8. **[ ]** Botão para download do relatório de análise semântica em formato Markdown

## Technical Specifications

### Component Architecture
```typescript
// components/features/Analysis/BusinessAnalysisPage.tsx
interface BusinessAnalysisProps {
  uploadedFiles: UploadedFile[];
  prompts: PromptConfig;
}

interface BusinessAnalysisResult {
  id: string;
  analysisType: 'business';
  timestamp: Date;
  overallAssessment: string;
  businessDocuments: DocumentInfo[];
  semanticResults: SemanticResult[];
  alignmentScore: number;
  gaps: BusinessGap[];
  recommendations: string[];
  tokenUsage: TokenUsage;
  processingTime: number;
  status: AnalysisStatus;
}

interface DocumentInfo {
  id: string;
  name: string;
  type: 'user-story' | 'epic' | 'business-rule' | 'requirement';
  content: string;
  metadata: DocumentMetadata;
}

interface SemanticResult {
  requirement: string;
  codeAlignment: AlignmentStatus;
  evidence: CodeEvidence[];
  confidence: number;
  businessImpact: 'low' | 'medium' | 'high';
  relatedRequirements: string[];
}

interface BusinessGap {
  description: string;
  affectedRequirements: string[];
  severity: 'low' | 'medium' | 'high';
  suggestedActions: string[];
}
```

### Sub-components
1. **MultiDocumentUpload**: Upload interface for multiple business documents
2. **DocumentOrganizer**: Organize and categorize uploaded documents
3. **SemanticAnalysisControls**: Analysis control buttons and settings
4. **AlignmentResults**: Display semantic alignment results
5. **GapAnalysis**: Show business gaps and misalignments
6. **BusinessIntelligence**: Business insights and recommendations

### State Management
```typescript
// stores/businessAnalysisStore.ts
interface BusinessAnalysisState {
  currentAnalysis: BusinessAnalysisResult | null;
  uploadedDocuments: DocumentInfo[];
  selectedDocuments: string[];
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  isManualMode: boolean;
  analysisSettings: AnalysisSettings;
}

interface AnalysisSettings {
  includeUserStories: boolean;
  includeEpics: boolean;
  includeBusinessRules: boolean;
  sensitivityThreshold: number;
  businessWeight: 'balanced' | 'business-focused' | 'technical-focused';
}

const useBusinessAnalysisStore = create<BusinessAnalysisState>((set, get) => ({
  // Initial state
  currentAnalysis: null,
  uploadedDocuments: [],
  selectedDocuments: [],
  isAnalyzing: false,
  progress: 0,
  error: null,
  isManualMode: false,
  analysisSettings: {
    includeUserStories: true,
    includeEpics: true,
    includeBusinessRules: true,
    sensitivityThreshold: 0.7,
    businessWeight: 'balanced'
  },

  // Actions
  uploadDocuments: async (files: File[]) => {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`documents[${index}]`, file);
      });

      const response = await apiClient.post('/api/documents/business/upload', formData);
      const newDocuments = response.data.map((doc: any) => ({
        ...doc,
        uploadDate: new Date()
      }));

      set((state) => ({
        uploadedDocuments: [...state.uploadedDocuments, ...newDocuments],
        selectedDocuments: [...state.selectedDocuments, ...newDocuments.map(d => d.id)]
      }));
    } catch (error) {
      set({ error: error.message });
    }
  },

  startAnalysis: async () => {
    const state = get();
    if (state.selectedDocuments.length === 0) {
      set({ error: 'Selecione pelo menos um documento de negócio' });
      return;
    }

    set({ isAnalyzing: true, progress: 0, error: null });
    try {
      const result = await analysisService.startBusinessAnalysis({
        documentIds: state.selectedDocuments,
        settings: state.analysisSettings
      });
      set({ currentAnalysis: result, isAnalyzing: false, progress: 100 });
    } catch (error) {
      set({ error: error.message, isAnalyzing: false });
    }
  },

  updateSemanticResult: (requirement: string, updates: Partial<SemanticResult>) => {
    set((state) => ({
      currentAnalysis: state.currentAnalysis ? {
        ...state.currentAnalysis,
        semanticResults: state.currentAnalysis.semanticResults.map(sr =>
          sr.requirement === requirement ? { ...sr, ...updates } : sr
        )
      } : null
    }));
  },

  toggleDocumentSelection: (documentId: string) => {
    set((state) => ({
      selectedDocuments: state.selectedDocuments.includes(documentId)
        ? state.selectedDocuments.filter(id => id !== documentId)
        : [...state.selectedDocuments, documentId]
    }));
  },
}));
```

### Semantic Analysis Pipeline
```
Document Upload → Content Extraction → Semantic Processing → Requirement Mapping → Code Analysis → Alignment Scoring → Results
```

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003, STO-004, STO-005, STO-006, STO-007, STO-008
- **Blocked by**: None
- **Blocking**: None (Final analysis interface)

## Testing Strategy

1. **Unit Tests**: Test individual components and semantic processing
2. **Integration Tests**: Test multi-document upload and analysis workflow
3. **Semantic Analysis Tests**: Test requirement extraction and mapping
4. **User Interface Tests**: Test user interactions and workflows
5. **Performance Tests**: Test processing of multiple business documents

### Test Cases
- Upload multiple business documents simultaneously
- Organize documents by type (user stories, epics, rules)
- Preview document content correctly
- Start semantic analysis with selected documents
- Monitor multi-document analysis progress
- View and interpret semantic alignment results
- Identify business gaps and misalignments
- Edit results manually
- Download comprehensive business analysis report

## Implementation Details

### Multi-Document Upload Component
```typescript
// components/features/Analysis/MultiDocumentUpload.tsx
interface MultiDocumentUploadProps {
  onDocumentsUploaded: (documents: DocumentInfo[]) => void;
  onDocumentTypeChange: (documentId: string, type: DocumentInfo['type']) => void;
}

const MultiDocumentUpload: React.FC<MultiDocumentUploadProps> = ({
  onDocumentsUploaded,
  onDocumentTypeChange
}) => {
  const [uploadQueue, setUploadQueue] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      setUploadQueue(prev => [...prev, ...acceptedFiles]);
    },
    accept: {
      'text/markdown': ['.md'],
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true
  });

  const processUploadQueue = async () => {
    if (uploadQueue.length === 0) return;

    setUploading(true);
    try {
      const formData = new FormData();
      uploadQueue.forEach((file, index) => {
        formData.append(`documents[${index}]`, file);
      });

      const response = await apiClient.post('/api/documents/business/batch-upload', formData);
      onDocumentsUploaded(response.data);
      setUploadQueue([]);
    } catch (error) {
      console.error('Batch upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="multi-document-upload">
      <div {...getRootProps()} className="upload-zone">
        <input {...getInputProps()} />
        <CloudUploadIcon className="upload-icon" />
        <h3>Upload Documentos de Negócio</h3>
        <p>Arraste múltiplos documentos ou clique para selecionar</p>
        <p className="supported-formats">
          Suporta: Markdown, PDF, DOCX, TXT (Histórias, Épicos, Regras)
        </p>
      </div>

      {uploadQueue.length > 0 && (
        <div className="upload-queue">
          <h4>Arquivos para Upload ({uploadQueue.length})</h4>
          <div className="queue-items">
            {uploadQueue.map((file, index) => (
              <div key={index} className="queue-item">
                <DescriptionIcon />
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
                <button
                  onClick={() => setUploadQueue(prev => prev.filter((_, i) => i !== index))}
                  className="btn-icon"
                >
                  <CloseIcon />
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={processUploadQueue}
            disabled={uploading}
            className="btn-primary"
          >
            {uploading ? 'Enviando...' : `Enviar ${uploadQueue.length} arquivos`}
          </button>
        </div>
      )}
    </div>
  );
};
```

### Document Organizer Component
```typescript
// components/features/Analysis/DocumentOrganizer.tsx
interface DocumentOrganizerProps {
  documents: DocumentInfo[];
  selectedDocuments: string[];
  onSelectionChange: (documentId: string) => void;
  onTypeChange: (documentId: string, type: DocumentInfo['type']) => void;
}

const DocumentOrganizer: React.FC<DocumentOrganizerProps> = ({
  documents,
  selectedDocuments,
  onSelectionChange,
  onTypeChange
}) => {
  const [filter, setFilter] = useState<'all' | DocumentInfo['type']>('all');

  const filteredDocuments = documents.filter(doc =>
    filter === 'all' || doc.type === filter
  );

  const groupedDocuments = filteredDocuments.reduce((acc, doc) => {
    if (!acc[doc.type]) {
      acc[doc.type] = [];
    }
    acc[doc.type].push(doc);
    return acc;
  }, {} as Record<DocumentInfo['type'], DocumentInfo[]>);

  const getTypeIcon = (type: DocumentInfo['type']) => {
    switch (type) {
      case 'user-story': return <StoryIcon />;
      case 'epic': return <EpicIcon />;
      case 'business-rule': return <RuleIcon />;
      case 'requirement': return <RequirementIcon />;
      default: return <DescriptionIcon />;
    }
  };

  const getTypeLabel = (type: DocumentInfo['type']) => {
    switch (type) {
      case 'user-story': return 'Histórias de Usuário';
      case 'epic': return 'Épicos';
      case 'business-rule': return 'Regras de Negócio';
      case 'requirement': return 'Requisitos';
      default: return 'Outros';
    }
  };

  return (
    <div className="document-organizer">
      <div className="organizer-header">
        <h3>Documentos de Negócio</h3>
        <div className="filter-tabs">
          <button
            onClick={() => setFilter('all')}
            className={filter === 'all' ? 'active' : ''}
          >
            Todos ({documents.length})
          </button>
          {Object.entries(groupedDocuments).map(([type, docs]) => (
            <button
              key={type}
              onClick={() => setFilter(type as DocumentInfo['type'])}
              className={filter === type ? 'active' : ''}
            >
              {getTypeLabel(type as DocumentInfo['type'])} ({docs.length})
            </button>
          ))}
        </div>
      </div>

      <div className="document-groups">
        {Object.entries(groupedDocuments).map(([type, docs]) => (
          <div key={type} className="document-group">
            <div className="group-header">
              {getTypeIcon(type as DocumentInfo['type'])}
              <h4>{getTypeLabel(type as DocumentInfo['type'])}</h4>
            </div>
            <div className="document-list">
              {docs.map((doc) => (
                <div key={doc.id} className="document-item">
                  <input
                    type="checkbox"
                    checked={selectedDocuments.includes(doc.id)}
                    onChange={() => onSelectionChange(doc.id)}
                    className="document-checkbox"
                  />
                  <div className="document-preview">
                    <h5>{doc.name}</h5>
                    <p className="document-excerpt">
                      {doc.content.substring(0, 100)}...
                    </p>
                  </div>
                  <div className="document-actions">
                    <select
                      value={doc.type}
                      onChange={(e) => onTypeChange(doc.id, e.target.value as DocumentInfo['type'])}
                      className="type-selector"
                    >
                      <option value="user-story">História</option>
                      <option value="epic">Épico</option>
                      <option value="business-rule">Regra</option>
                      <option value="requirement">Requisito</option>
                    </select>
                    <button
                      onClick={() => {/* Preview logic */}}
                      className="btn-icon"
                      title="Visualizar"
                    >
                      <VisibilityIcon />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Semantic Analysis Results Component
```typescript
// components/features/Analysis/SemanticResults.tsx
interface SemanticResultsProps {
  results: BusinessAnalysisResult;
  onEditResult: (requirement: string, updates: Partial<SemanticResult>) => void;
  onDownloadReport: () => void;
}

const SemanticResults: React.FC<SemanticResultsProps> = ({
  results,
  onEditResult,
  onDownloadReport
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'alignment' | 'gaps' | 'insights'>('overview');

  return (
    <div className="semantic-results">
      <div className="results-header">
        <h3>Análise Semântica de Negócio</h3>
        <div className="header-metrics">
          <div className="alignment-score">
            <CircularProgress value={results.alignmentScore * 100} size={60} />
            <div className="score-details">
              <span className="score-value">{Math.round(results.alignmentScore * 100)}%</span>
              <span className="score-label">Alinhamento</span>
            </div>
          </div>
          <button onClick={onDownloadReport} className="btn-secondary">
            <DownloadIcon /> Baixar Relatório
          </button>
        </div>
      </div>

      <div className="results-tabs">
        <button
          onClick={() => setActiveTab('overview')}
          className={activeTab === 'overview' ? 'active' : ''}
        >
          Visão Geral
        </button>
        <button
          onClick={() => setActiveTab('alignment')}
          className={activeTab === 'alignment' ? 'active' : ''}
        >
          Alinhamento Semântico
        </button>
        <button
          onClick={() => setActiveTab('gaps')}
          className={activeTab === 'gaps' ? 'active' : ''}
        >
          Gaps Identificados
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={activeTab === 'insights' ? 'active' : ''}
        >
          Insights de Negócio
        </button>
      </div>

      <div className="results-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <OverallSummary results={results} />
          </div>
        )}

        {activeTab === 'alignment' && (
          <div className="alignment-tab">
            <AlignmentResults
              results={results.semanticResults}
              onEditResult={onEditResult}
            />
          </div>
        )}

        {activeTab === 'gaps' && (
          <div className="gaps-tab">
            <GapAnalysis gaps={results.gaps} />
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="insights-tab">
            <BusinessIntelligence
              recommendations={results.recommendations}
              results={results}
            />
          </div>
        )}
      </div>
    </div>
  );
};
```

### Backend Semantic Analysis Engine
```python
# services/semantic_analysis_engine.py
class SemanticAnalysisEngine:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.requirement_extractor = RequirementExtractor()
        self.semantic_mapper = SemanticMapper()
        self.business_analyzer = BusinessAnalyzer()

    async def analyze_business_alignment(self, codebase: List[CodeFile], business_docs: List[BusinessDocument]) -> BusinessAnalysisResult:
        """Analyze semantic alignment between code and business requirements"""

        # 1. Extract and structure business requirements
        requirements = await self.requirement_extractor.extract_requirements(business_docs)

        # 2. Perform semantic mapping between code and requirements
        semantic_mappings = await self.semantic_mapper.create_mappings(codebase, requirements)

        # 3. Calculate alignment scores and identify gaps
        alignment_scores = await self.business_analyzer.calculate_alignment(semantic_mappings)

        # 4. Generate business insights and recommendations
        insights = await self.business_analyzer.generate_insights(alignment_scores, requirements)

        # 5. Compile final results
        return BusinessAnalysisResult(
            semantic_results=semantic_mappings,
            alignment_score=alignment_scores.overall_score,
            gaps=alignment_scores.gaps,
            recommendations=insights.recommendations,
            # ... other fields
        )

    async def extract_semantic_relationships(self, requirements: List[BusinessRequirement]) -> SemanticGraph:
        """Extract semantic relationships between business requirements"""
        # Build semantic graph of requirements
        pass

    async def identify_business_impact(self, misalignments: List[CodeMisalignment]) -> List[BusinessImpact]:
        """Identify business impact of code misalignments"""
        # Analyze impact on business objectives
        pass
```

## Error Handling

### Multi-Document Upload Errors
- Handle partial upload failures
- Provide clear error messages per document
- Allow retry for failed uploads
- Maintain upload progress visibility

### Semantic Processing Errors
- Detect when semantic analysis fails
- Provide fallback options for manual analysis
- Preserve partial results when possible
- Offer detailed error diagnostics

### Business Logic Validation
- Validate business document content
- Detect conflicting requirements
- Identify incomplete business specifications
- Provide guidance for requirement refinement

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for complex interactions
- **Screen Reader Support**: ARIA labels for complex data displays
- **Focus Management**: Proper focus management for tabs and modals
- **High Contrast**: Support for high contrast themes
- **Cognitive Accessibility**: Clear information hierarchy and labeling

## Performance Considerations

- **Document Processing**: Optimize for multiple large documents
- **Semantic Analysis**: Efficient NLP processing and caching
- **Memory Management**: Handle large document sets efficiently
- **Progressive Loading**: Load results as they become available
- **Caching Strategy**: Cache semantic analysis results

## Security Considerations

- **Document Privacy**: Protect sensitive business information
- **Access Control**: Ensure proper authorization for business documents
- **Content Validation**: Sanitize business document content
- **Audit Trail**: Log all business analysis activities
- **Data Retention**: Manage business data retention policies

## Notes

- Consider implementing requirement traceability features
- Add support for business process modeling
- Include stakeholder collaboration tools
- Consider adding business impact assessment
- Plan for integration with project management tools

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All unit and integration tests passing
- [ ] Accessibility audit passes
- [ ] Performance benchmarks met
- [ ] Code review completed and approved
- [ ] User acceptance testing completed
- [ ] Security scan passes
- [ ] Documentation updated
- [ ] Business stakeholder validation completed