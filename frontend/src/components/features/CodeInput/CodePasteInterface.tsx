/**
 * Code Paste Interface Component
 * Allows users to paste code and save it to the database
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Card } from '../../common/Card';
import Button from '../../common/Button';
import Alert from '../../common/Alert';
import LoadingSpinner from '../../common/LoadingSpinner';
import useCodeEntries from '../../../hooks/useCodeEntries';
import codeEntryService from '../../../services/codeEntryService';
import { CodeEntryCreate } from '../../../types/codeEntry';

interface CodePasteInterfaceProps {
  onCodeSave?: (codeData: any) => void;
  onCodeDelete?: (codeId: string) => void;
  onError?: (error: string) => void;
}

export const CodePasteInterface: React.FC<CodePasteInterfaceProps> = ({
  onCodeSave,
  onCodeDelete,
  onError
}) => {
  // Form state
  const [codeContent, setCodeContent] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [detectedLanguage, setDetectedLanguage] = useState<string>('');
  const [customLanguage, setCustomLanguage] = useState('');
  const [useAutoTitle, setUseAutoTitle] = useState(true);

  // UI state
  const [isDetecting, setIsDetecting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Custom hook for code entries
  const {
    codeEntries,
    createCodeEntry,
    detectLanguage,
    deleteEntry,
    isSaving,
    error: hookError,
    clearError
  } = useCodeEntries();

  // Auto-detect language when code content changes
  useEffect(() => {
    if (codeContent.trim().length > 10) {
      const timeoutId = setTimeout(async () => {
        try {
          setIsDetecting(true);
          const result = await detectLanguage(codeContent);
          setDetectedLanguage(result.language);
        } catch (err) {
          console.error('Language detection failed:', err);
        } finally {
          setIsDetecting(false);
        }
      }, 500); // Debounce language detection

      return () => clearTimeout(timeoutId);
    } else {
      setDetectedLanguage('');
    }
  }, [codeContent, detectLanguage]);

  // Auto-generate title if enabled
  useEffect(() => {
    if (useAutoTitle && detectedLanguage && !title) {
      const autoTitle = codeEntryService.generateAutoTitle(codeContent, detectedLanguage);
      setTitle(autoTitle);
    }
  }, [detectedLanguage, useAutoTitle, codeContent, title]);

  // Validate form fields
  const validateForm = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate code content
    const codeValidation = codeEntryService.validateCodeContent(codeContent);
    if (!codeValidation.isValid) {
      newErrors.codeContent = codeValidation.error || 'Code content is required';
    }

    // Validate title
    const titleValidation = codeEntryService.validateTitle(title);
    if (!titleValidation.isValid) {
      newErrors.title = titleValidation.error || 'Title is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [codeContent, title]);

  // Handle code content change
  const handleCodeChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setCodeContent(value);

    // Clear code content error when user starts typing
    if (errors.codeContent) {
      setErrors(prev => ({ ...prev, codeContent: '' }));
    }
  }, [errors.codeContent]);

  // Handle title change
  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTitle(value);
    setUseAutoTitle(false); // Disable auto-title when user manually edits

    // Clear title error when user starts typing
    if (errors.title) {
      setErrors(prev => ({ ...prev, title: '' }));
    }
  }, [errors.title]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const linesCount = codeEntryService.countLines(codeContent);
      const charactersCount = codeEntryService.countCharacters(codeContent);

      const codeEntryData: CodeEntryCreate = {
        code_content: codeContent,
        title: title.trim(),
        description: description.trim() || undefined,
        language: customLanguage || detectedLanguage || undefined,
        lines_count: linesCount,
        characters_count: charactersCount
      };

      const savedEntry = await createCodeEntry(codeEntryData);

      if (savedEntry) {
        // Clear form
        setCodeContent('');
        setTitle('');
        setDescription('');
        setCustomLanguage('');
        setDetectedLanguage('');
        setUseAutoTitle(true);
        setErrors({});

        // Call callback
        onCodeSave?.(savedEntry);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save code entry';
      onError?.(errorMessage);
    }
  }, [validateForm, codeContent, title, description, customLanguage, detectedLanguage, createCodeEntry, onCodeSave, onError]);

  // Handle delete
  const handleDelete = useCallback(async (entryId: string, entryTitle: string) => {
    if (window.confirm(`Are you sure you want to delete "${entryTitle}"?`)) {
      const success = await deleteEntry(entryId);
      if (success) {
        onCodeDelete?.(entryId);
      }
    }
  }, [deleteEntry, onCodeDelete]);

  // Get display language
  const displayLanguage = customLanguage || detectedLanguage || 'text';

  return (
    <div className="code-paste-interface">
      {/* Error display */}
      {(hookError || Object.keys(errors).length > 0) && (
        <div className="mb-4">
          {hookError && (
            <div className="br-alert br-alert-error">
              <span>⚠️</span>
              <span>{hookError}</span>
            </div>
          )}
          {Object.entries(errors).map(([field, message]) => (
            <div key={field} className="br-alert br-alert-error">
              <span>⚠️</span>
              <span>{message}</span>
            </div>
          ))}
        </div>
      )}

      <div className="code-paste-content">
        {/* Code Input Section */}
        <div className="code-input-section">
          <div className="br-card">
            <div className="card-header">
              <h3 className="card-title">Cole Seu Código</h3>
              <p className="card-description">
                Cole seu código fonte abaixo. O idioma será detectado automaticamente.
              </p>
            </div>
            <div className="card-content">
              {/* Language detection indicator */}
              {isDetecting && (
                <div className="language-loading">
                  <div className="loading-spinner"></div>
                  <span>Detectando idioma...</span>
                </div>
              )}

              {/* Detected language */}
              {detectedLanguage && !isDetecting && (
                <div className="language-detection">
                  <span className="language-detected">
                    Detectado: <strong>{detectedLanguage}</strong>
                  </span>
                  <button
                    className="br-button br-button-outline"
                    onClick={() => {
                      setCustomLanguage('');
                      setUseAutoTitle(false);
                    }}
                  >
                    Substituir
                  </button>
                </div>
              )}

              {/* Custom language input */}
              {customLanguage || (!detectedLanguage && !isDetecting) ? (
                <div className="form-group">
                  <label className="form-label">
                    Idioma
                  </label>
                  <input
                    type="text"
                    value={customLanguage}
                    onChange={(e) => setCustomLanguage(e.target.value)}
                    placeholder="ex: javascript, python, typescript"
                    className="form-input"
                  />
                </div>
              ) : null}

              {/* Code textarea */}
              <div className="form-group">
                <label className="form-label required">
                  Conteúdo do Código
                </label>
                <textarea
                  value={codeContent}
                  onChange={handleCodeChange}
                  placeholder="Cole seu código aqui..."
                  className={`form-textarea code-input ${
                    errors.codeContent ? 'error' : ''
                  }`}
                />
                {errors.codeContent && (
                  <p className="mt-1 text-sm text-red-600">{errors.codeContent}</p>
                )}
                <div className="stats-display">
                  {codeEntryService.countLines(codeContent)} linhas, {codeEntryService.countCharacters(codeContent)} caracteres
                </div>
              </div>

              {/* Title input */}
              <div className="form-group">
                <div className="flex items-center justify-between mb-1">
                  <label className="form-label required">
                    Título
                  </label>
                  <label className="flex items-center text-xs text-gray-600">
                    <input
                      type="checkbox"
                      checked={useAutoTitle}
                      onChange={(e) => setUseAutoTitle(e.target.checked)}
                      className="mr-1"
                    />
                    Gerar automaticamente
                  </label>
                </div>
                <input
                  type="text"
                  value={title}
                  onChange={handleTitleChange}
                  disabled={useAutoTitle}
                  placeholder="Título do código"
                  className={`form-input ${
                    errors.title ? 'error' : ''
                  } ${useAutoTitle ? 'bg-gray-50 text-gray-500' : ''}`}
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                )}
              </div>

              {/* Description input */}
              <div className="form-group">
                <label className="form-label">
                  Descrição (opcional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Descrição opcional do código..."
                  className="form-textarea"
                  rows={4}
                />
              </div>

              {/* Action buttons */}
              <div className="button-group">
                <button
                  className="br-button br-button-primary"
                  onClick={handleSave}
                  disabled={isSaving || !codeContent.trim()}
                >
                  {isSaving ? (
                    <>
                      <div className="loading-spinner"></div>
                      Salvando...
                    </>
                  ) : (
                    'Salvar Código'
                  )}
                </button>
                <button
                  className="br-button br-button-outline"
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={!codeContent.trim()}
                >
                  {showPreview ? 'Ocultar' : 'Mostrar'} Prévia
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Code List Section */}
        <div className="code-list-section">
          <div className="br-card">
            <div className="card-header">
              <h3 className="card-title">Códigos Salvos</h3>
              <p className="card-description">
                Seus trechos de código salvos anteriormente
              </p>
            </div>
            <div className="card-content">
              {codeEntries.length === 0 ? (
                <div className="empty-state">
                  <h3>Nenhum código salvo ainda</h3>
                  <p>Cole e salve seu primeiro trecho de código para começar.</p>
                </div>
              ) : (
                <div>
                  {codeEntries.map((entry) => (
                    <div
                      key={entry.id}
                      className="code-item"
                    >
                      <div className="code-item-header">
                        <h4 className="code-item-title">
                          {entry.title}
                        </h4>
                        <button
                          className="br-button br-button-outline"
                          onClick={() => handleDelete(entry.id, entry.title)}
                          style={{ background: '#dc3545', color: 'white', borderColor: '#dc3545' }}
                        >
                          Excluir
                        </button>
                      </div>

                      {entry.description && (
                        <p className="code-item-description">{entry.description}</p>
                      )}

                      <div className="code-item-meta">
                        {entry.language && (
                          <span className="code-item-language">
                            {entry.language}
                          </span>
                        )}
                        <span>{entry.lines_count} linhas</span>
                        <span>{entry.characters_count.toLocaleString()} caracteres</span>
                        <span className="code-item-date">
                          {new Date(entry.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Code Preview Modal */}
      {showPreview && codeContent.trim() && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="br-card" style={{ maxWidth: '1200px', width: '100%', maxHeight: '80vh', overflow: 'hidden' }}>
            <div className="card-header" style={{ border: 'none', borderBottom: '1px solid #e9ecef' }}>
              <h3 className="card-title">Prévia do Código</h3>
              <button
                className="br-button br-button-outline"
                onClick={() => setShowPreview(false)}
              >
                Fechar
              </button>
            </div>
            <div className="card-content" style={{ overflow: 'auto', maxHeight: '60vh' }}>
              <div className="mb-4">
                <strong>Título:</strong> {title || 'Sem título'}
                {displayLanguage && (
                  <span className="ml-4">
                    <strong>Idioma:</strong> {displayLanguage}
                  </span>
                )}
                {description && (
                  <p className="mt-2">
                    <strong>Descrição:</strong> {description}
                  </p>
                )}
              </div>
              <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto" style={{ background: '#f8f9fa', border: '1px solid #e9ecef' }}>
                <code className="text-sm font-mono">{codeContent}</code>
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodePasteInterface;