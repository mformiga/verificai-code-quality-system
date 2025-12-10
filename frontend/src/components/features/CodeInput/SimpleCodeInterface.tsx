/**
 * Simple Code Interface Component - Version simplificada para teste
 */

import React, { useState } from 'react';

interface SimpleCodeInterfaceProps {
  onCodeSave?: (codeData: any) => void;
  onCodeDelete?: (codeId: string) => void;
  onError?: (error: string) => void;
}

export const SimpleCodeInterface: React.FC<SimpleCodeInterfaceProps> = ({
  onCodeSave,
  onCodeDelete,
  onError
}) => {
  // Form state
  const [codeContent, setCodeContent] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('');

  // Mock data for saved codes
  const [savedCodes, setSavedCodes] = useState([
    {
      id: '1',
      title: 'Exemplo de Código JavaScript',
      description: 'Uma função simples de exemplo',
      language: 'javascript',
      lines_count: 5,
      characters_count: 125,
      created_at: new Date().toISOString()
    }
  ]);

  const handleSave = () => {
    if (!codeContent.trim()) {
      onError?.('O conteúdo do código é obrigatório');
      return;
    }

    if (!title.trim()) {
      onError?.('O título é obrigatório');
      return;
    }

    const newCode = {
      id: Date.now().toString(),
      title: title.trim(),
      description: description.trim(),
      language: language || 'text',
      lines_count: codeContent.split('\n').length,
      characters_count: codeContent.length,
      created_at: new Date().toISOString()
    };

    setSavedCodes([newCode, ...savedCodes]);

    // Clear form
    setCodeContent('');
    setTitle('');
    setDescription('');
    setLanguage('');

    onCodeSave?.(newCode);
  };

  const handleDelete = (id: string, title: string) => {
    if (window.confirm(`Tem certeza que deseja excluir "${title}"?`)) {
      setSavedCodes(savedCodes.filter(code => code.id !== id));
      onCodeDelete?.(id);
    }
  };

  return (
    <div className="simple-code-interface">
      <h2 style={{ color: '#1351b4', marginBottom: '24px' }}>Interface de Código Simplificada</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        {/* Input Section */}
        <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#1351b4', marginBottom: '16px' }}>Colar Código</h3>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
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
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
              Conteúdo do Código:
            </label>
            <textarea
              value={codeContent}
              onChange={(e) => setCodeContent(e.target.value)}
              placeholder="Cole seu código aqui..."
              rows={10}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                fontSize: '13px',
                fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
                resize: 'vertical'
              }}
            />
            <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
              {codeContent.split('\n').length} linhas, {codeContent.length} caracteres
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
              Título:
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
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
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
                resize: 'vertical'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleSave}
              disabled={!codeContent.trim() || !title.trim()}
              style={{
                flex: 1,
                padding: '12px 24px',
                background: '#1351b4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                opacity: (!codeContent.trim() || !title.trim()) ? 0.6 : 1
              }}
            >
              Salvar Código
            </button>
          </div>
        </div>

        {/* List Section */}
        <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#1351b4', marginBottom: '16px' }}>Códigos Salvos</h3>

          {savedCodes.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#6c757d' }}>
              <p>Nenhum código salvo ainda.</p>
              <p style={{ fontSize: '14px' }}>Cole e salve seu primeiro trecho de código.</p>
            </div>
          ) : (
            <div>
              {savedCodes.map((code) => (
                <div
                  key={code.id}
                  style={{
                    padding: '16px',
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <h4 style={{ color: '#1351b4', margin: 0, flex: 1 }}>
                      {code.title}
                    </h4>
                    <button
                      onClick={() => handleDelete(code.id, code.title)}
                      style={{
                        background: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        padding: '6px 12px',
                        fontSize: '12px',
                        cursor: 'pointer',
                        marginLeft: '12px'
                      }}
                    >
                      Excluir
                    </button>
                  </div>

                  {code.description && (
                    <p style={{ color: '#6c757d', fontSize: '14px', marginBottom: '12px' }}>
                      {code.description}
                    </p>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '12px', color: '#6c757d' }}>
                    {code.language && (
                      <span style={{ background: '#e9ecef', padding: '4px 8px', borderRadius: '4px' }}>
                        {code.language}
                      </span>
                    )}
                    <span>{code.lines_count} linhas</span>
                    <span>{code.characters_count.toLocaleString()} caracteres</span>
                    <span>
                      {new Date(code.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SimpleCodeInterface;