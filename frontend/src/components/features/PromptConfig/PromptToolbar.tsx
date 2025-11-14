import React from 'react';
import { PromptToolbarProps } from '@/types/prompt';

export const PromptToolbar: React.FC<PromptToolbarProps> = ({
  onSave,
  onDiscard,
  onRestoreDefaults,
  isSaving,
  hasUnsavedChanges,
  disabled = false,
}) => {
  return (
    <div className="prompt-toolbar">
      <div className="br-button-group">
        <button
          onClick={onSave}
          disabled={disabled || isSaving || !hasUnsavedChanges}
          className="br-button primary"
          type="button"
        >
          {isSaving ? (
            <>
              <i className="fas fa-spinner fa-spin me-1"></i>
              Salvando...
            </>
          ) : (
            <>
              <i className="fas fa-save me-1"></i>
              Salvar Alterações
            </>
          )}
        </button>

        <button
          onClick={onDiscard}
          disabled={disabled || isSaving || !hasUnsavedChanges}
          className="br-button secondary"
          type="button"
        >
          <i className="fas fa-undo me-1"></i>
          Descartar
        </button>

        <button
          onClick={onRestoreDefaults}
          disabled={disabled || isSaving}
          className="br-button"
          type="button"
        >
          <i className="fas fa-refresh me-1"></i>
          Restaurar Padrões
        </button>
      </div>
    </div>
  );
};