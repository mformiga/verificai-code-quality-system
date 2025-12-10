import React, { useState } from 'react';
import { Upload, FolderOpen, FileText, AlertCircle } from 'lucide-react';
import FolderSelector from '@/components/features/CodeUpload/FolderSelector';
import PathList from '@/components/features/CodeUpload/PathList';
import toast from 'react-hot-toast';

const CodeUploadPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeTab, setActiveTab] = useState<'upload' | 'paths'>('upload');

  const handleFolderSelect = (paths: any[]) => {
    toast.success(`${paths.length} caminho(s) extraído(s) com sucesso!`);
  };

  const handleFolderError = (error: string) => {
    toast.error(`Erro: ${error}`);
  };

  const handleSelectionComplete = () => {
    // Force refresh the path list when folder selection is complete
    setRefreshKey(prev => prev + 1);
    // Auto-switch to paths tab to show results
    setActiveTab('paths');
  };

  return (
    <div className="code-upload-page">
      {/* Page Header - Following DSGov pattern like other pages */}
      <div className="code-upload-header">
        <div className="br-card">
          <div className="card-header">
            <div className="row align-items-center">
              <div className="br-col">
                <h1 className="text-h1">Upload de Arquivos de Código</h1>
                <p className="text-regular">
                  Selecione pastas e arquivos de código fonte para análise.
                  Os arquivos serão indexados e ficarão disponíveis para análise nos critérios gerais.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Following DSGov pattern like other pages */}
      <div className="br-tabs" data-tabs="code-upload-tabs">
        <nav className="tab-navigation" role="tablist">
          {[
            { id: 'upload', name: 'Upload de Arquivos', icon: Upload },
            { id: 'paths', name: 'Caminhos Indexados', icon: FolderOpen }
          ].map((tab) => (
            <button
              key={tab.id}
              className={`tab-item ${activeTab === tab.id ? 'is-active' : ''}`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id as any)}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content - Following DSGov pattern */}
      <div className="br-container">
        {activeTab === 'upload' && (
          <div className="tab-content" id="tab-upload">
            <div className="br-card">
              <div className="card-header">
                <h2 className="text-h2">Selecionar Pasta de Código</h2>
                <p className="text-regular text-muted">
                  Escolha uma pasta do seu sistema contendo os arquivos de código que deseja analisar.
                  O sistema irá extrair automaticamente todos os arquivos suportados.
                </p>
              </div>
              <div className="card-content">
                <div className="upload-section" style={{
                  border: '2px dashed #dee2e6',
                  borderRadius: '8px',
                  padding: '2rem',
                  textAlign: 'center',
                  backgroundColor: '#f8f9fa',
                  transition: 'border-color 0.3s ease'
                }}>
                  <FolderOpen className="w-16 h-16 mx-auto mb-4" style={{
                    color: '#6c757d',
                    opacity: 0.7
                  }} />

                  <h3 className="text-h3" style={{
                    marginBottom: '1rem',
                    color: '#495057'
                  }}>
                    Upload de Pasta
                  </h3>

                  <p className="text-regular text-muted" style={{
                    marginBottom: '1.5rem',
                    maxWidth: '500px',
                    marginLeft: 'auto',
                    marginRight: 'auto'
                  }}>
                    Use o seletor abaixo para escolher uma pasta do seu computador.
                    Todos os arquivos de código serão automaticamente detectados e indexados.
                  </p>

                  {/* Folder Selector Component */}
                  <div className="folder-selector-wrapper">
                    <FolderSelector
                      onFolderSelect={handleFolderSelect}
                      onError={handleFolderError}
                      onSelectionComplete={handleSelectionComplete}
                    />
                  </div>

                  <div className="supported-formats mt-4" style={{
                    backgroundColor: '#e9ecef',
                    borderRadius: '6px',
                    padding: '1rem',
                    marginTop: '2rem'
                  }}>
                    <h4 className="text-small" style={{
                      fontWeight: '600',
                      marginBottom: '0.5rem',
                      color: '#495057'
                    }}>
                      Formatos Suportados
                    </h4>
                    <p className="text-small text-muted" style={{ margin: 0 }}>
                      JavaScript (.js), TypeScript (.ts), Python (.py), Java (.java), C/C++ (.c, .cpp, .h),
                      C# (.cs), PHP (.php), Ruby (.rb), Go (.go), Rust (.rs), e muitos outros.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'paths' && (
          <div className="tab-content" id="tab-paths">
            <div className="br-card">
              <div className="card-header">
                <div className="row align-items-center">
                  <div className="br-col">
                    <h2 className="text-h2">Caminhos de Arquivos Indexados</h2>
                    <p className="text-regular text-muted">
                      Visualize e gerencie os arquivos de código que foram extraídos e estão disponíveis para análise.
                    </p>
                  </div>
                  <div className="br-col-auto">
                    <button
                      className="br-button primary"
                      onClick={() => setRefreshKey(prev => prev + 1)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <FileText className="w-4 h-4" />
                      Atualizar Lista
                    </button>
                  </div>
                </div>
              </div>
              <div className="card-content">
                {/* Path List Component */}
                <PathList
                  key={refreshKey}
                  autoRefresh={false}
                  onFolderSelect={handleFolderSelect}
                  onError={handleFolderError}
                  onSelectionComplete={handleSelectionComplete}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeUploadPage;