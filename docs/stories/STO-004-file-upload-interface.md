# User Story: File Upload Interface & Drag-and-Drop

**ID:** STO-004
**Epic:** Epic 2 - Core File Processing & Upload System
**Priority:** High
**Estimate:** 3 days
**Status:** Ready for Development

## Description

Como um usuário de QA,
Quero fazer upload de pastas de código através de interface intuitiva com drag-and-drop,
Para que possa facilmente selecionar e enviar os arquivos para análise.

## Acceptance Criteria

1. **[ ]** Interface drag-and-drop implementada na tela principal com área claramente demarcada
2. **[ ]** Suporte para upload de pastas completas com inclusão automática de subpastas e arquivos
3. **[ ]** Visualização em tempo real do progresso de upload com indicadores de status
4. **[ ]** Interface alternativa de click-to-upload para usuários que preferem navegação tradicional
5. **[ ]** Feedback visual claro para upload concluído com sucesso ou erros
6. **[ ]** Lista de arquivos enviados com informações básicas (Path da pasta e o nome do arquivo)

## Technical Specifications

### Component Structure
```typescript
// components/features/CodeUpload/FileUpload.tsx
interface FileUploadProps {
  onUploadComplete: (files: UploadedFile[]) => void;
  onError: (error: string) => void;
  maxFileSize?: number; // Default: 50MB
  acceptedTypes?: string[];
}

interface UploadedFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  uploadDate: Date;
}
```

### Sub-components
1. **DragDropZone**: Main upload area with drag-and-drop functionality
2. **FileList**: Display uploaded files with metadata
3. **ProgressIndicator**: Real-time upload progress
4. **FilePreview**: Preview of uploaded files when applicable

### File Processing Logic
- **Supported File Types**: JavaScript, TypeScript, Python, Java, C/C++
- **Maximum File Size**: 50MB per file
- **Folder Processing**: Recursive folder traversal
- **File Validation**: Type and size validation
- **Duplicate Handling**: Skip or overwrite options

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003
- **Blocked by**: None
- **Blocking**: STO-005 (Prompt Configuration), Analysis Stories

## Testing Strategy

1. **Unit Tests**: Test individual components and file validation
2. **Integration Tests**: Test upload workflow and backend integration
3. **Performance Tests**: Test large file uploads and concurrent uploads
4. **User Interface Tests**: Test drag-and-drop interactions
5. **Error Handling Tests**: Test various error scenarios

### Test Cases
- Upload single file via drag-and-drop
- Upload folder with subfolders
- Upload multiple files simultaneously
- Cancel upload in progress
- Handle file size limit exceeded
- Handle unsupported file types
- Handle network interruptions
- Test accessibility features

## Implementation Details

### Drag-and-Drop Implementation
```typescript
const useFileUpload = () => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
  }, []);

  return { isDragActive, handleDrag, handleDrop };
};
```

### File Validation
```typescript
const validateFile = (file: File): ValidationResult => {
  const maxSize = 50 * 1024 * 1024; // 50MB
  const acceptedTypes = [
    'application/javascript',
    'text/typescript',
    'text/x-python',
    'text/x-java-source',
    'text/x-csrc',
    'text/x-c++src'
  ];

  if (file.size > maxSize) {
    return { valid: false, error: 'File size exceeds 50MB limit' };
  }

  if (!acceptedTypes.includes(file.type)) {
    return { valid: false, error: 'Unsupported file type' };
  }

  return { valid: true };
};
```

### Upload Progress Tracking
```typescript
const uploadWithProgress = async (file: File): Promise<UploadedFile> => {
  const formData = new FormData();
  formData.append('file', file);

  return new Promise((resolve, reject) => {
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
        resolve(response.data);
      } else {
        reject(new Error('Upload failed'));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error'));
    });

    xhr.open('POST', '/api/upload');
    xhr.send(formData);
  });
};
```

### Error Handling
- **Network Errors**: Retry mechanism with exponential backoff
- **File Validation**: Clear error messages for invalid files
- **Server Errors**: Graceful degradation with user feedback
- **Timeout**: Timeout handling for slow uploads

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for file selection
- **Screen Reader Support**: ARIA labels and live regions
- **Focus Management**: Proper focus states and indicators
- **High Contrast**: Support for high contrast themes
- **Error Announcements**: Screen reader announcements for errors

## Performance Considerations

- **Memory Management**: Handle large file uploads efficiently
- **Progress Updates**: Throttle progress updates to prevent UI blocking
- **File Reading**: Use FileReader API efficiently
- **UI Responsiveness**: Non-blocking file processing
- **Caching**: Cache file metadata for better UX

## Notes

- Consider implementing chunked upload for very large files
- Add support for pause/resume functionality
- Include file preview for supported types
- Consider implementing file compression before upload
- Add upload history and retry functionality

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All unit and integration tests passing
- [ ] Accessibility audit passes
- [ ] Performance benchmarks met
- [ ] Code review completed and approved
- [ ] User acceptance testing completed
- [ ] Error scenarios thoroughly tested
- [ ] Documentation updated