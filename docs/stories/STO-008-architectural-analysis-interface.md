# User Story: Architectural Document Analysis Interface

**ID:** STO-008
**Epic:** Epic 5 - Document Upload & Analysis Interfaces
**Priority:** High
**Estimate:** 4 days
**Status:** Ready for Development

## Description

Como um usuário de QA,
Quero acessar uma tela dedicada para fazer upload de documento de arquitetura e ver resultados da análise de conformidade,
Para que possa verificar se o código-fonte está em conformidade com a arquitetura definida.

## Acceptance Criteria

1. **[ ]** Tela dedicada implementada com área de upload para documentos de arquitetura
2. **[ ]** Interface drag-and-drop para upload de arquivos de arquitetura (PDF, Markdown, DOCX)
3. **[ ]** Sistema de preview do documento de arquitetura após upload
4. **[ ]** Botão para iniciar análise de conformidade arquitetural usando prompt específico definido na tela de prompts
5. **[ ]** Interface de progresso mostrando status da análise em tempo real
6. **[ ]** Exibição dos resultados da análise de conformidade formatados em Markdown
7. **[ ]** Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis ou precisa alterar o resultado da análise feita pela IA
8. **[ ]** Botão para download do relatório de conformidade em formato Markdown

## Technical Specifications

### Component Architecture
```typescript
// components/features/Analysis/ArchitecturalAnalysisPage.tsx
interface ArchitecturalAnalysisProps {
  uploadedFiles: UploadedFile[];
  prompts: PromptConfig;
}

interface ArchitecturalAnalysisResult {
  id: string;
  analysisType: 'architectural';
  timestamp: Date;
  overallAssessment: string;
  architecturalDocument: DocumentInfo;
  complianceResults: ComplianceResult[];
  violations: ArchitecturalViolation[];
  recommendations: string[];
  tokenUsage: TokenUsage;
  processingTime: number;
  status: AnalysisStatus;
}

interface DocumentInfo {
  id: string;
  name: string;
  type: 'pdf' | 'markdown' | 'docx';
  size: number;
  uploadDate: Date;
  content?: string; // For text-based documents
  preview?: string; // Preview text
}

interface ComplianceResult {
  requirement: string;
  description: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  evidence: CodeEvidence[];
  confidence: number;
  impact: 'low' | 'medium' | 'high';
}
```

### Sub-components
1. **DocumentUpload**: Drag-and-drop document upload interface
2. **DocumentPreview**: Preview of uploaded architectural documents
3. **AnalysisControls**: Start analysis and download controls
4. **ComplianceResults**: Display architectural compliance results
5. **ViolationDetails**: Detailed view of architectural violations
6. **ManualEditInterface**: Editor for manual result modification

### State Management
```typescript
// stores/architecturalAnalysisStore.ts
interface ArchitecturalAnalysisState {
  currentAnalysis: ArchitecturalAnalysisResult | null;
  uploadedDocument: DocumentInfo | null;
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  isManualMode: boolean;
}

const useArchitecturalAnalysisStore = create<ArchitecturalAnalysisState>((set, get) => ({
  // Initial state
  currentAnalysis: null,
  uploadedDocument: null,
  isAnalyzing: false,
  progress: 0,
  error: null,
  isManualMode: false,

  // Actions
  uploadDocument: async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('document', file);

      const response = await apiClient.post('/api/documents/architectural', formData);
      set({ uploadedDocument: response.data });
    } catch (error) {
      set({ error: error.message });
    }
  },

  startAnalysis: async () => {
    const state = get();
    if (!state.uploadedDocument) {
      set({ error: 'Nenhum documento de arquitetura enviado' });
      return;
    }

    set({ isAnalyzing: true, progress: 0, error: null });
    try {
      const result = await analysisService.startArchitecturalAnalysis({
        documentId: state.uploadedDocument.id,
        promptId: 'architectural'
      });
      set({ currentAnalysis: result, isAnalyzing: false, progress: 100 });
    } catch (error) {
      set({ error: error.message, isAnalyzing: false });
    }
  },

  updateComplianceResult: (requirement: string, updates: Partial<ComplianceResult>) => {
    set((state) => ({
      currentAnalysis: state.currentAnalysis ? {
        ...state.currentAnalysis,
        complianceResults: state.currentAnalysis.complianceResults.map(cr =>
          cr.requirement === requirement ? { ...cr, ...updates } : cr
        )
      } : null
    }));
  },
}));
```

### Document Processing Pipeline
```
Document Upload → File Processing → Content Extraction → Document Parsing → Analysis → Results
```

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003, STO-004, STO-005, STO-006, STO-007
- **Blocked by**: None
- **Blocking**: STO-009

## Testing Strategy

1. **Unit Tests**: Test individual components and document processing
2. **Integration Tests**: Test document upload and analysis workflow
3. **Document Processing Tests**: Test different document formats
4. **User Interface Tests**: Test user interactions and workflows
5. **Performance Tests**: Test document processing and analysis performance

### Test Cases
- Upload various document formats (PDF, Markdown, DOCX)
- Preview document content correctly
- Start architectural analysis
- Monitor analysis progress
- View and interpret compliance results
- Edit results manually
- Download compliance report
- Handle processing errors gracefully

## Implementation Details

### Document Upload Component
```typescript
// components/features/Analysis/DocumentUpload.tsx
interface DocumentUploadProps {
  onDocumentUploaded: (document: DocumentInfo) => void;
  acceptedTypes: string[];
  maxSize: number;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onDocumentUploaded,
  acceptedTypes,
  maxSize
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file
    if (file.size > maxSize) {
      alert(`O arquivo deve ter no máximo ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    if (!acceptedTypes.includes(file.type)) {
      alert('Tipo de arquivo não suportado');
      return;
    }

    // Upload file with progress tracking
    const formData = new FormData();
    formData.append('document', file);

    try {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          onDocumentUploaded(response.data);
          setUploadProgress(0);
        }
      });

      xhr.open('POST', '/api/documents/architectural/upload');
      xhr.send(formData);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [acceptedTypes, maxSize, onDocumentUploaded, maxSize]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: handleDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    multiple: false,
    maxSize: maxSize
  });

  return (
    <div
      {...getRootProps()}
      className={`document-upload ${isDragActive ? 'active' : ''}`}
    >
      <input {...getInputProps()} />
      <CloudUploadIcon className="upload-icon" />
      <p>Arraste um documento de arquitetura ou clique para selecionar</p>
      <p className="upload-hint">
        Formatos suportados: PDF, Markdown, DOCX (máx {maxSize / (1024 * 1024)}MB)
      </p>
      {uploadProgress > 0 && (
        <div className="upload-progress">
          <div className="progress-bar" style={{ width: `${uploadProgress}%` }} />
          <span>{uploadProgress}%</span>
        </div>
      )}
    </div>
  );
};
```

### Document Preview Component
```typescript
// components/features/Analysis/DocumentPreview.tsx
interface DocumentPreviewProps {
  document: DocumentInfo;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({ document }) => {
  const [previewContent, setPreviewContent] = useState<string>('');

  useEffect(() => {
    const loadPreview = async () => {
      try {
        const response = await fetch(`/api/documents/${document.id}/preview`);
        const data = await response.json();
        setPreviewContent(data.content);
      } catch (error) {
        console.error('Failed to load preview:', error);
      }
    };

    if (document) {
      loadPreview();
    }
  }, [document]);

  const renderPreview = () => {
    switch (document.type) {
      case 'markdown':
        return (
          <div className="markdown-preview">
            <MarkdownRenderer content={previewContent} />
          </div>
        );
      case 'pdf':
        return (
          <div className="pdf-preview">
            <PDFViewer url={`/api/documents/${document.id}/view`} />
          </div>
        );
      case 'docx':
        return (
          <div className="docx-preview">
            <div className="docx-content">{previewContent}</div>
          </div>
        );
      default:
        return <div>Preview não disponível</div>;
    }
  };

  return (
    <div className="document-preview">
      <div className="preview-header">
        <h3>Prévia do Documento</h3>
        <div className="document-info">
          <span>{document.name}</span>
          <span>{(document.size / 1024).toFixed(1)} KB</span>
        </div>
      </div>
      <div className="preview-content">
        {renderPreview()}
      </div>
    </div>
  );
};
```

### Compliance Results Component
```typescript
// components/features/Analysis/ComplianceResults.tsx
interface ComplianceResultsProps {
  results: ArchitecturalAnalysisResult;
  onEditResult: (requirement: string, updates: Partial<ComplianceResult>) => void;
  onDownloadReport: () => void;
}

const ComplianceResults: React.FC<ComplianceResultsProps> = ({
  results,
  onEditResult,
  onDownloadReport
}) => {
  const [expandedRequirements, setExpandedRequirements] = useState<Set<string>>(new Set());

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'bg-green-100 text-green-800';
      case 'partially_compliant': return 'bg-yellow-100 text-yellow-800';
      case 'non_compliant': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="compliance-results">
      <div className="results-header">
        <h3>Resultados de Conformidade Arquitetural</h3>
        <div className="header-actions">
          <div className="overall-assessment">
            <span className="assessment-label">Avaliação Geral:</span>
            <span className={`assessment-value ${getStatusColor(results.overallAssessment)}`}>
              {results.overallAssessment}
            </span>
          </div>
          <button onClick={onDownloadReport} className="btn-secondary">
            <DownloadIcon /> Baixar Relatório
          </button>
        </div>
      </div>

      <div className="compliance-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-number">{results.complianceResults.length}</span>
            <span className="stat-label">Requisitos Verificados</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">
              {results.complianceResults.filter(r => r.status === 'compliant').length}
            </span>
            <span className="stat-label">Conformes</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">
              {results.complianceResults.filter(r => r.status === 'non_compliant').length}
            </span>
            <span className="stat-label">Não Conformes</span>
          </div>
        </div>
      </div>

      <div className="compliance-list">
        {results.complianceResults.map((result) => (
          <div key={result.requirement} className="compliance-item">
            <div className="compliance-header">
              <div className="compliance-info">
                <span className={`status-badge ${getStatusColor(result.status)}`}>
                  {result.status === 'compliant' ? 'Conforme' :
                   result.status === 'partially_compliant' ? 'Parcialmente Conforme' :
                   'Não Conforme'}
                </span>
                <span className={`impact-badge ${getImpactColor(result.impact)}`}>
                  Impacto: {result.impact === 'high' ? 'Alto' :
                           result.impact === 'medium' ? 'Médio' : 'Baixo'}
                </span>
              </div>
              <button
                onClick={() => {
                  const newExpanded = new Set(expandedRequirements);
                  if (newExpanded.has(result.requirement)) {
                    newExpanded.delete(result.requirement);
                  } else {
                    newExpanded.add(result.requirement);
                  }
                  setExpandedRequirements(newExpanded);
                }}
                className="btn-icon"
              >
                {expandedRequirements.has(result.requirement) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </button>
            </div>

            <div className="requirement-content">
              <h4 className="requirement-title">{result.requirement}</h4>
              <p className="requirement-description">{result.description}</p>
            </div>

            {expandedRequirements.has(result.requirement) && (
              <div className="requirement-details">
                <div className="assessment-section">
                  <h5>Avaliação</h5>
                  <MarkdownRenderer content={result.assessment} />
                </div>

                {result.evidence.length > 0 && (
                  <div className="evidence-section">
                    <h5>Evidências</h5>
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

                <div className="compliance-actions">
                  <button
                    onClick={() => onEditResult(result.requirement, result)}
                    className="btn-text"
                  >
                    <EditIcon /> Editar manualmente
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Backend Document Processing
```python
# services/document_processor.py
class DocumentProcessor:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.markdown_processor = MarkdownProcessor()
        self.docx_processor = DocxProcessor()

    async def process_document(self, file_path: str, file_type: str) -> ProcessedDocument:
        """Process uploaded architectural document"""
        if file_type == 'pdf':
            return await self.pdf_processor.process(file_path)
        elif file_type == 'markdown':
            return await self.markdown_processor.process(file_path)
        elif file_type == 'docx':
            return await self.docx_processor.process(file_path)
        else:
            raise ValueError(f"Unsupported document type: {file_type}")

    async def extract_requirements(self, document: ProcessedDocument) -> List[ArchitecturalRequirement]:
        """Extract architectural requirements from document content"""
        # Use NLP or pattern matching to identify requirements
        pass

    async def generate_preview(self, document: ProcessedDocument) -> str:
        """Generate preview text for document"""
        # Extract first few paragraphs or summary
        pass
```

## Error Handling

### Document Processing Errors
- Handle unsupported file formats
- Manage corrupted or password-protected documents
- Provide clear error messages for processing failures
- Offer retry options for temporary failures

### Analysis Failures
- Detect when LLM analysis fails
- Automatically offer manual mode
- Preserve partial results when possible
- Provide detailed error diagnostics

### User Interface Errors
- Validate user inputs before submission
- Provide clear feedback for invalid operations
- Handle edge cases gracefully
- Maintain application stability

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader Support**: ARIA labels and live regions for updates
- **Focus Management**: Proper focus states and traps for modals
- **High Contrast**: Support for high contrast themes
- **Document Accessibility**: Ensure document previews are accessible

## Performance Considerations

- **Document Processing**: Optimize for large document files
- **Preview Generation**: Lazy loading of document content
- **Memory Management**: Handle large documents efficiently
- **Caching**: Cache processed documents when possible
- **Progressive Loading**: Load content as needed

## Security Considerations

- **File Validation**: Validate uploaded files for security
- **Content Scanning**: Scan for malicious content
- **Access Control**: Ensure only authorized users can access documents
- **Data Privacy**: Protect sensitive architectural information
- **Audit Logging**: Log all document processing activities

## Notes

- Consider implementing OCR for scanned PDF documents
- Add support for additional document formats
- Include document versioning and comparison
- Consider adding architectural pattern detection
- Plan for collaborative document review features

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