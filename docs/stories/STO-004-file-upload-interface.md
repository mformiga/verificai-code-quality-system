# User Story: Folder Path Extraction & Display Interface

**ID:** STO-004
**Epic:** Epic 2 - Core File Processing & Upload System
**Priority:** High
**Estimate:** 3 days
**Status:** Completed

## Description

Como um usuário de QA,
Quero selecionar uma pasta e ter todos os caminhos de arquivos extraídos e persistidos no banco de dados,
Para que possa visualizar a estrutura completa de diretórios e arquivos de forma organizada.

## Acceptance Criteria

1. **[x]** Interface para seleção de pastas implementada com botão ou área de seleção
2. **[x]** Sistema recupera caminhos completos de todos os arquivos dentro da pasta selecionada (incluindo subpastas)
3. **[x]** Sistema persiste as informações de caminho no banco de dados com nome e extensão do arquivo
4. **[x]** Interface exibe lista de caminhos com um caminho por linha
5. **[x]** Suporte para navegação recursiva por todas as subpastas e arquivos
6. **[x]** Feedback visual claro durante o processo de escaneamento e persistência

## Technical Specifications

### Component Structure
```typescript
// components/features/CodeUpload/FolderSelector.tsx
interface FolderSelectorProps {
  onFolderSelect: (paths: FilePath[]) => void;
  onError: (error: string) => void;
}

interface FilePath {
  id: string;
  fullPath: string; // Caminho completo do arquivo
  fileName: string; // Nome do arquivo com extensão
  fileExtension: string; // Extensão do arquivo
  folderPath: string; // Caminho da pasta onde o arquivo está
  fileSize?: number;
  lastModified?: Date;
}
```

### Sub-components
1. **FolderSelector**: Interface para seleção de pastas
2. **PathList**: Lista de caminhos exibidos um por linha
3. **ScanProgress**: Indicador de progresso do escaneamento
4. **PathDatabase**: Componente para persistência de dados

### File Processing Logic
- **Folder Selection**: Interface nativa de seleção de pastas
- **Recursive Scanning**: Varredura completa de subpastas e arquivos
- **Path Extraction**: Extração de caminhos completos com extensões
- **Database Persistence**: Armazenamento das informações no banco de dados
- **Path Display**: Exibição organizada um caminho por linha

## Dependencies

- **Prerequisites**: STO-001, STO-002, STO-003
- **Blocked by**: None
- **Blocking**: STO-005 (Prompt Configuration), Analysis Stories

## Testing Strategy

1. **Unit Tests**: Test individual components e lógica de escaneamento
2. **Integration Tests**: Test fluxo de seleção e persistência no banco
3. **Performance Tests**: Test escaneamento de pastas grandes e muitos arquivos
4. **User Interface Tests**: Test interações de seleção e exibição
5. **Error Handling Tests**: Test vários cenários de erro

### Test Cases
- Selecionar pasta com arquivos simples
- Selecionar pasta com subpastas profundas
- Selecionar pasta com muitos arquivos
- Lidar com pastas vazias
- Lidar com permissões negadas
- Lidar com caminhos muito longos
- Test exibição de caminhos um por linha
- Test persistência no banco de dados
- Test feedback visual durante escaneamento

## Implementation Details

### Folder Selection Implementation
```typescript
const useFolderScanner = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);

  const handleFolderSelect = useCallback(async () => {
    try {
      setIsScanning(true);
      // Utiliza input directory ou API específica para selecionar pasta
      const folderPath = await selectFolderDialog();
      const filePaths = await scanFolderRecursively(folderPath);

      // Persiste no banco de dados
      await persistFilePaths(filePaths);

      return filePaths;
    } catch (error) {
      throw new Error('Failed to scan folder');
    } finally {
      setIsScanning(false);
    }
  }, []);

  return { isScanning, handleFolderSelect };
};
```

### Recursive Folder Scanning
```typescript
const scanFolderRecursively = async (folderPath: string): Promise<FilePath[]> => {
  const filePaths: FilePath[] = [];
  const entries = await readDirectoryEntries(folderPath);

  for (const entry of entries) {
    if (entry.isDirectory) {
      // Varredura recursiva para subpastas
      const subFolderPaths = await scanFolderRecursively(entry.fullPath);
      filePaths.push(...subFolderPaths);
    } else {
      // Extrai informações do arquivo
      const filePath: FilePath = {
        id: generateId(),
        fullPath: entry.fullPath,
        fileName: entry.name,
        fileExtension: entry.extension,
        folderPath: entry.directory,
        fileSize: entry.size,
        lastModified: entry.lastModified
      };
      filePaths.push(filePath);
    }
  }

  return filePaths;
};
```

### Database Persistence
```typescript
const persistFilePaths = async (filePaths: FilePath[]): Promise<void> => {
  for (const filePath of filePaths) {
    const response = await fetch('/api/paths', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filePath),
    });

    if (!response.ok) {
      throw new Error('Failed to persist file path');
    }
  }
};
```

### Path Display Implementation
```typescript
const PathList = ({ paths }: { paths: FilePath[] }) => {
  return (
    <div className="path-list">
      {paths.map((path) => (
        <div key={path.id} className="path-item">
          <code>{path.fullPath}</code>
          <div className="path-meta">
            <span>{path.fileName}</span>
            <span>{path.fileExtension}</span>
            <span>{formatFileSize(path.fileSize)}</span>
          </div>
        </div>
      ))}
    </div>
  );
};
```

### Error Handling
- **Permission Errors**: Mensagens claras para pastas sem acesso
- **Network Errors**: Mecanismo de retry com exponential backoff
- **Large Folders**: Indicador de progresso durante escaneamento
- **Database Errors**: Feedback claro para falhas de persistência

## Accessibility Requirements

- **Keyboard Navigation**: Full keyboard support for folder selection
- **Screen Reader Support**: ARIA labels e live regions para progresso
- **Focus Management**: Estados de foco adequados para navegação
- **High Contrast**: Suporte para temas de alto contraste
- **Error Announcements**: Anúncios para leitores de tela sobre erros

## Performance Considerations

- **Memory Management**: Gerenciamento eficiente de escaneamento de pastas grandes
- **Progress Updates**: Limitação de atualizações para evitar bloqueio de UI
- **Recursive Scanning**: Varredura não bloqueante para subpastas
- **UI Responsiveness**: Processamento de caminhos sem bloquear interface
- **Database Bulk Insert**: Inserção em lote para melhor performance

## Database Schema

```sql
CREATE TABLE file_paths (
    id VARCHAR(255) PRIMARY KEY,
    full_path TEXT NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_extension VARCHAR(50),
    folder_path TEXT NOT NULL,
    file_size BIGINT,
    last_modified DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL
);
```

## Notes

- Considerar implementar paginação para listas muito longas de caminhos
- Adicionar suporte para filtrar por tipo de extensão
- Incluir busca por nome de arquivo na lista exibida
- Implementar exportação da lista de caminhos para CSV
- Adicionar funcionalidade de seleção múltipla de pastas

## Definition of Done

- [x] Todos os acceptance criteria atendidos
- [x] Todos os testes unitários e de integração passando
- [x] Auditoria de acessibilidade aprovada
- [x] Benchmarks de performance atingidos
- [x] Code review completado e aprovado
- [x] User acceptance testing completado
- [x] Cenários de erro testados exaustivamente
- [x] Documentação atualizada
- [x] Schema do banco de dados implementado e testado
- [x] Interface de exibição de caminhos implementada corretamente