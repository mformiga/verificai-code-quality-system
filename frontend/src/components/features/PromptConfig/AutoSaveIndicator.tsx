import React from 'react';
import { AutoSaveIndicatorProps } from '@/types/prompt';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export const AutoSaveIndicator: React.FC<AutoSaveIndicatorProps> = ({
  isSaving,
  lastSaved,
  hasUnsavedChanges,
}) => {
  const getStatusText = () => {
    if (isSaving) return 'Salvando...';
    if (hasUnsavedChanges) return 'Não salvo';
    if (lastSaved) return `Salvo ${formatDistanceToNow(lastSaved, {
      addSuffix: true,
      locale: ptBR
    })}`;
    return 'Salvo';
  };

  const getStatusClass = () => {
    if (isSaving) return 'warning';
    if (hasUnsavedChanges) return 'danger';
    return 'success';
  };

  const getStatusIcon = () => {
    if (isSaving) return 'fas fa-spinner fa-spin';
    if (hasUnsavedChanges) return 'fas fa-exclamation-circle';
    return 'fas fa-check-circle';
  };

  return (
    <div className={`br-tag ${getStatusClass()}`}>
      <i className={`${getStatusIcon()} me-1`}></i>
      {getStatusText()}
    </div>
  );
};