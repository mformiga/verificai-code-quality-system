/**
 * Functional Code Page - Interface completa para colar códigos com integração PostgreSQL
 */

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../services/apiClient';

interface CodeEntry {
  id: string;
  code_content: string;
  title: string;
  description?: string;
  language?: string;
  lines_count: number;
  characters_count: number;
  created_at: string;
}

const FunctionalCodePage: React.FC = () => {
  const { user } = useAuthStore();
  // Form state
  const [codeContent, setCodeContent] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Data state
  const [savedCodes, setSavedCodes] = useState<CodeEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load saved codes from backend
  const loadCodes = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/code-entries');
      setSavedCodes(response.data || []);
    } catch (error) {
      console.warn('Erro ao carregar códigos, usando dados mock:', error);
      // Mock data se houver erro
      setSavedCodes([
        {
          id: '1',
          code_content: 'function helloWorld() {\n  console.log("Hello, World!");\n}',
          title: 'Exemplo JavaScript',
          description: 'Função simples de exemplo',
          language: 'javascript',
          lines_count: 3,
          characters_count: 65,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Save code to backend
  const saveCode = async () => {
    if (!codeContent.trim()) {
      setError('O conteúdo do código é obrigatório');
      return;
    }

    if (!title.trim()) {
      setError('O título é obrigatório');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccess('');

    // Prepare code data outside try block so it's accessible in catch block
    const codeData = {
      code_content: codeContent,
      title: title.trim(),
      description: description.trim() || undefined,
      language: language.trim() || undefined,
      lines_count: codeContent.split('\n').length,
      characters_count: codeContent.length
    };

    try {
      const response = await apiClient.post('/code-entries', codeData);
      const savedCode = response.data;
      setSavedCodes([savedCode, ...savedCodes]);
      setSuccess('Código salvo com sucesso!');

      // Clear form
      setCodeContent('');
      setTitle('');
      setDescription('');
      setLanguage('');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      // Fallback para salvamento local se backend falhar
      console.warn('Backend não disponível, salvando localmente:', error);

      const localCode = {
        ...codeData,
        id: Date.now().toString(),
        created_at: new Date().toISOString()
      };

      setSavedCodes([localCode, ...savedCodes]);
      setSuccess('Código salvo localmente (backend não disponível)');

      // Clear form
      setCodeContent('');
      setTitle('');
      setDescription('');
      setLanguage('');

      setTimeout(() => setSuccess(''), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  // Delete code
  const deleteCode = async (id: string, title: string) => {
    if (!window.confirm(`Tem certeza que deseja excluir "${title}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/code-entries/${id}`);
      setSavedCodes(savedCodes.filter(code => code.id !== id));
    } catch (error) {
      // Fallback para exclusão local se backend falhar
      console.warn('Erro ao excluir código, removendo localmente:', error);
      setSavedCodes(savedCodes.filter(code => code.id !== id));
    }
  };

  // Load codes on component mount
  useEffect(() => {
    loadCodes();
  }, []);

  // Check if user is authenticated
  if (!user) {
    return (
      <div style={{
        padding: '24px',
        minHeight: '100vh',
        backgroundColor: '#f8f9fa',
        fontFamily: 'Arial, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          background: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#1351b4', marginBottom: '16px' }}>
            Autenticação Necessária
          </h2>
          <p style={{ color: '#6c757d', marginBottom: '24px' }}>
            Por favor, faça login para acessar esta funcionalidade.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      padding: '24px',
      minHeight: '100vh',
      backgroundColor: '#f8f9fa',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          color: '#1351b4',
          fontSize: '32px',
          fontWeight: 'bold',
          marginBottom: '12px'
        }}>
          Interface de Colagem de Código
        </h1>
        <p style={{
          color: '#6c757d',
          fontSize: '16px',
          margin: 0,
          lineHeight: 1.5
        }}>
          Cole seus trechos de código fonte e salve-os para referência posterior.
          Cada código será salvo como uma linha separada no PostgreSQL.
        </p>
      </div>

      {/* Messages */}
      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          color: '#721c24',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <strong>Erro:</strong> {error}
        </div>
      )}

      {success && (
        <div style={{
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          color: '#155724',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <strong>Sucesso:</strong> {success}
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '32px',
        alignItems: 'start'
      }}>
        {/* Code Input Section */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '20px',
            borderBottom: '1px solid #e9ecef'
          }}>
            <h2 style={{
              color: '#1351b4',
              fontSize: '20px',
              fontWeight: '600',
              margin: 0,
              marginBottom: '8px'
            }}>
              Colar Código
            </h2>
            <p style={{
              color: '#6c757d',
              margin: 0,
              fontSize: '14px'
            }}>
              Cole seu código fonte abaixo. O idioma pode ser especificado manualmente.
            </p>
          </div>

          <div style={{ padding: '24px' }}>
            {/* Language Field */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#495057'
              }}>
                Idioma:
              </label>
              <input
                type="text"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                placeholder="ex: javascript, python, typescript"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '14px',
                  transition: 'border-color 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1351b4';
                  e.target.style.boxShadow = '0 0 0 2px rgba(19, 81, 180, 0.25)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#ced4da';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>

            {/* Code Content */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#495057'
              }}>
                Conteúdo do Código <span style={{ color: '#dc3545' }}>*</span>:
              </label>
              <textarea
                value={codeContent}
                onChange={(e) => setCodeContent(e.target.value)}
                placeholder="Cole seu código aqui..."
                rows={12}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
                  resize: 'vertical',
                  transition: 'border-color 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1351b4';
                  e.target.style.boxShadow = '0 0 0 2px rgba(19, 81, 180, 0.25)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#ced4da';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <div style={{
                fontSize: '12px',
                color: '#6c757d',
                marginTop: '8px'
              }}>
                {codeContent.split('\n').length} linhas, {codeContent.length} caracteres
              </div>
            </div>

            {/* Title */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#495057'
              }}>
                Título <span style={{ color: '#dc3545' }}>*</span>:
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Título do código"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '14px',
                  transition: 'border-color 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1351b4';
                  e.target.style.boxShadow = '0 0 0 2px rgba(19, 81, 180, 0.25)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#ced4da';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>

            {/* Description */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#495057'
              }}>
                Descrição (opcional):
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Descrição opcional do código..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '14px',
                  resize: 'vertical',
                  transition: 'border-color 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1351b4';
                  e.target.style.boxShadow = '0 0 0 2px rgba(19, 81, 180, 0.25)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#ced4da';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>

            {/* Save Button */}
            <button
              onClick={saveCode}
              disabled={isSaving || !codeContent.trim() || !title.trim()}
              style={{
                width: '100%',
                padding: '14px 24px',
                background: '#1351b4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                opacity: (isSaving || !codeContent.trim() || !title.trim()) ? 0.6 : 1,
                transform: (!isSaving && codeContent.trim() && title.trim()) ? 'translateY(-1px)' : 'none',
                boxShadow: (!isSaving && codeContent.trim() && title.trim()) ? '0 4px 8px rgba(19, 81, 180, 0.3)' : 'none'
              }}
            >
              {isSaving ? (
                <>
                  <span style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '16px',
                    border: '2px solid #ffffff',
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    marginRight: '8px'
                  }}></span>
                  Salvando...
                </>
              ) : (
                'Salvar Código'
              )}
            </button>
          </div>
        </div>

        {/* Saved Codes Section */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '20px',
            borderBottom: '1px solid #e9ecef'
          }}>
            <h2 style={{
              color: '#1351b4',
              fontSize: '20px',
              fontWeight: '600',
              margin: 0,
              marginBottom: '8px'
            }}>
              Códigos Salvos
            </h2>
            <p style={{
              color: '#6c757d',
              margin: 0,
              fontSize: '14px'
            }}>
              Seus trechos de código salvos anteriormente
            </p>
          </div>

          <div style={{
            padding: '0',
            maxHeight: '600px',
            overflowY: 'auto'
          }}>
            {isLoading ? (
              <div style={{
                textAlign: 'center',
                padding: '60px 24px',
                color: '#6c757d'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  border: '3px solid #f3f3f3',
                  borderTop: '3px solid #1351b4',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  margin: '0 auto 16px'
                }}></div>
                <p>Carregando códigos salvos...</p>
              </div>
            ) : savedCodes.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '60px 24px',
                color: '#6c757d'
              }}>
                <h3 style={{ color: '#6c757d', marginBottom: '12px' }}>
                  Nenhum código salvo ainda
                </h3>
                <p style={{ margin: 0 }}>
                  Cole e salve seu primeiro trecho de código para começar.
                </p>
              </div>
            ) : (
              savedCodes.map((code) => (
                <div
                  key={code.id}
                  style={{
                    padding: '20px 24px',
                    borderBottom: '1px solid #e9ecef',
                    transition: 'background-color 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '12px'
                  }}>
                    <h3 style={{
                      color: '#1351b4',
                      margin: 0,
                      flex: 1,
                      fontSize: '16px',
                      fontWeight: '600'
                    }}>
                      {code.title}
                    </h3>
                    <button
                      onClick={() => deleteCode(code.id, code.title)}
                      style={{
                        background: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        padding: '6px 12px',
                        fontSize: '12px',
                        cursor: 'pointer',
                        marginLeft: '12px',
                        transition: 'background-color 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = '#c82333';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = '#dc3545';
                      }}
                    >
                      Excluir
                    </button>
                  </div>

                  {code.description && (
                    <p style={{
                      color: '#6c757d',
                      fontSize: '14px',
                      marginBottom: '12px',
                      lineHeight: 1.4
                    }}>
                      {code.description}
                    </p>
                  )}

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    fontSize: '12px',
                    color: '#6c757d',
                    flexWrap: 'wrap'
                  }}>
                    {code.language && (
                      <span style={{
                        background: '#e9ecef',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontWeight: '500',
                        color: '#495057'
                      }}>
                        {code.language}
                      </span>
                    )}
                    <span>{code.lines_count} linhas</span>
                    <span>{code.characters_count.toLocaleString()} caracteres</span>
                    <span style={{ color: '#868e96' }}>
                      {new Date(code.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* CSS Animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default FunctionalCodePage;