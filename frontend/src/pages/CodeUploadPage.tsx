import React from 'react';
import { FileX, Info, ArrowLeft, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// FORCE MAJOR UPDATE - 2025-12-09 22:25 - COMPLETE REWRITE

const CodeUploadPage: React.FC = () => {
  const navigate = useNavigate();

  // CRITICAL: Force console detection
  console.log('🔥🔥🔥 CodeUploadPage LOADED - FUNCTIONALITY REMOVED - 2025-12-09 22:25', new Date().toISOString());

  return (
    <div className="code-upload-page">
      {/* Page Header - Following DSGov pattern */}
      <div className="code-upload-header">
        <div className="br-card">
          <div className="card-header">
            <div className="row align-items-center">
              <div className="br-col">
                <h1 className="text-h1">Upload de Arquivos de Código</h1>
                <p className="text-regular">
                  Esta funcionalidade foi descontinuada.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="br-container">
        <div className="br-card">
          <div className="card-content">
            <div className="br-alert br-alert-info" style={{
              textAlign: 'center',
              padding: '3rem 2rem',
              marginBottom: '2rem'
            }}>
              <div style={{ marginBottom: '1.5rem' }}>
                <FileX className="w-16 h-16 mx-auto" style={{
                  color: '#0d6efd',
                  opacity: 0.8
                }} />
              </div>

              <h2 className="text-h2" style={{
                marginBottom: '1rem',
                color: '#495057'
              }}>
                Funcionalidade Descontinuada
              </h2>

              <p className="text-regular text-muted" style={{
                marginBottom: '1.5rem',
                maxWidth: '600px',
                marginLeft: 'auto',
                marginRight: 'auto',
                lineHeight: '1.6'
              }}>
                A funcionalidade de upload de arquivos foi removida do sistema.
                Agora você pode utilizar a <strong>Interface de Colagem de Código</strong>
                para inserir e analisar trechos de código diretamente.
              </p>

              <div className="row justify-content-center">
                <div className="br-col-md-auto">
                  <button
                    className="br-button primary"
                    onClick={() => navigate('/code-paste')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '12px 24px',
                      textDecoration: 'none'
                    }}
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Ir para Interface de Colagem de Código
                  </button>
                </div>
              </div>

              <div style={{
                backgroundColor: '#e7f5ff',
                borderRadius: '6px',
                padding: '1rem',
                marginTop: '2rem',
                border: '1px solid #b3d7ff'
              }}>
                <div className="d-flex align-items-start" style={{ gap: '0.75rem' }}>
                  <Info className="w-5 h-5" style={{
                    color: '#0d6efd',
                    flexShrink: 0,
                    marginTop: '0.125rem'
                  }} />
                  <div>
                    <h4 className="text-small" style={{
                      fontWeight: '600',
                      marginBottom: '0.5rem',
                      color: '#495057'
                    }}>
                      Nova Funcionalidade Disponível
                    </h4>
                    <p className="text-small text-muted" style={{ margin: 0 }}>
                      Acesse a Interface de Colagem de Código para colar diretamente seus trechos de código,
                      com detecção automática de linguagem e análise instantânea.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeUploadPage;