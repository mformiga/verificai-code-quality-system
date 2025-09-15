import React, { useEffect } from 'react';
import { usePromptStore } from '@/stores/promptStore';
import { PromptEditor } from './PromptEditor';
import { AutoSaveIndicator } from './AutoSaveIndicator';
import { VersionHistory } from './VersionHistory';
import { PromptToolbar } from './PromptToolbar';
import { PromptType } from '@/types/prompt';
import './PromptConfig.css';

export const PromptConfig: React.FC = () => {
  const {
    prompts,
    isSaving,
    lastSaved,
    hasUnsavedChanges,
    error,
    activePromptType,
    updatePrompt,
    setActivePromptType,
    savePrompts,
    discardChanges,
    restoreDefaults,
    loadPrompts,
    clearAutoSaveTimer,
  } = usePromptStore();

  useEffect(() => {
    loadPrompts();
    return () => {
      clearAutoSaveTimer();
    };
  }, [loadPrompts, clearAutoSaveTimer]);

  const handlePromptChange = (content: string) => {
    updatePrompt(activePromptType, content);
  };

  const handleTabChange = (type: PromptType) => {
    setActivePromptType(type);
  };

  const currentPrompt = prompts[activePromptType];

  const getTabLabel = (type: PromptType) => {
    switch (type) {
      case 'general':
        return 'Critérios Gerais';
      case 'architectural':
        return 'Conformidade Arquitetural';
      case 'business':
        return 'Conformidade Negocial';
    }
  };

  const getPlaceholder = (type: PromptType) => {
    switch (type) {
      case 'general':
        return 'Digite os critérios gerais de análise de código...';
      case 'architectural':
        return 'Digite os critérios de conformidade arquitetural...';
      case 'business':
        return 'Digite os critérios de conformidade negocial...';
    }
  };

  return (
    <div className="prompt-config">
      <div className="prompt-config-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h1">Configuração de Prompts</h1>
            <p className="text-regular">
              Personalize os prompts que serão usados para análise do código-fonte.
              As alterações são salvas automaticamente a cada 30 segundos.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="br-message danger" role="alert">
          <div className="icon">
            <span className="fas fa-exclamation-triangle"></span>
          </div>
          <div className="content" aria-label="Mensagem de erro">
            <p>{error}</p>
          </div>
        </div>
      )}

      <div className="br-tabs" data-tabs="prompt-tabs">
        <nav className="tab-navigation" role="tablist">
          {(['general', 'architectural', 'business'] as PromptType[]).map((type) => (
            <button
              key={type}
              className={`tab-item ${activePromptType === type ? 'is-active' : ''}`}
              role="tab"
              aria-selected={activePromptType === type}
              aria-controls={`tab-${type}`}
              onClick={() => handleTabChange(type)}
            >
              <span className="name">{getTabLabel(type)}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="br-container">
        <div className="br-grid">
          <div className="br-col-12 br-col-md-8">
            <div className="br-card">
              <div className="card-header">
                <div className="row align-items-center">
                  <div className="br-col">
                    <h2 className="text-h2">{getTabLabel(activePromptType)}</h2>
                  </div>
                  <div className="br-col-auto">
                    <AutoSaveIndicator
                      isSaving={isSaving}
                      lastSaved={lastSaved}
                      hasUnsavedChanges={hasUnsavedChanges}
                    />
                  </div>
                </div>
              </div>
              <div className="card-content">
                <PromptEditor
                  value={currentPrompt.content}
                  onChange={handlePromptChange}
                  language="markdown"
                  placeholder={getPlaceholder(activePromptType)}
                  disabled={isSaving}
                />

                <div className="prompt-actions mt-4">
                  <PromptToolbar
                    onSave={savePrompts}
                    onDiscard={discardChanges}
                    onRestoreDefaults={restoreDefaults}
                    isSaving={isSaving}
                    hasUnsavedChanges={hasUnsavedChanges}
                    disabled={isSaving}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="br-col-12 br-col-md-4">
            <div className="br-card mb-3">
              <div className="card-header">
                <h3 className="text-h3">Informações do Prompt</h3>
              </div>
              <div className="card-content">
                <div className="br-list">
                  <div className="br-item">
                    <span className="br-list-title">Nome:</span>
                    <span className="br-list-text">{currentPrompt.name}</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">Descrição:</span>
                    <span className="br-list-text">{currentPrompt.description}</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">Tipo:</span>
                    <span className="br-list-text">{currentPrompt.type}</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">Status:</span>
                    <span className={`br-tag ${currentPrompt.isActive ? 'success' : 'warning'}`}>
                      {currentPrompt.isActive ? 'Ativo' : 'Inativo'}
                    </span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">Padrão:</span>
                    <span className={`br-tag ${currentPrompt.isDefault ? 'info' : 'secondary'}`}>
                      {currentPrompt.isDefault ? 'Sim' : 'Não'}
                    </span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">Última modificação:</span>
                    <span className="br-list-text">
                      {new Date(currentPrompt.updatedAt).toLocaleString('pt-BR')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="br-card">
              <div className="card-header">
                <h3 className="text-h3">Histórico de Versões</h3>
              </div>
              <div className="card-content">
                <VersionHistory
                  versions={[
                    {
                      version: currentPrompt.version || 1,
                      content: currentPrompt.content,
                      createdAt: currentPrompt.updatedAt,
                      author: 'Usuário',
                    },
                  ]}
                  onRestore={() => {}}
                  currentVersion={currentPrompt.version || 1}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};