import React from 'react';
import { VersionHistoryProps } from '@/types/prompt';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export const VersionHistory: React.FC<VersionHistoryProps> = ({
  versions,
  onRestore,
  currentVersion,
}) => {
  const sortedVersions = [...versions].sort((a, b) => b.version - a.version);

  return (
    <div className="version-history br-card">
      <div className="card-header">
        <h3 className="text-h3">Histórico de Versões</h3>
      </div>
      <div className="card-content">
        <div className="version-list br-list">
          {sortedVersions.map((version) => (
            <div
              key={version.version}
              className={`version-item br-item ${
                version.version === currentVersion ? 'current' : ''
              }`}
            >
              <div className="version-header">
                <div className="br-list-title">
                  <span className="version-number">v{version.version}</span>
                  {version.version === currentVersion && (
                    <span className="br-tag success ms-2">Atual</span>
                  )}
                </div>
                <div className="br-list-text">
                  <span className="version-date text-small text-muted">
                    {format(new Date(version.createdAt), 'dd/MM/yyyy HH:mm', {
                      locale: ptBR,
                    })}
                  </span>
                </div>
              </div>
              <div className="version-author text-small text-muted">
                <i className="fas fa-user me-1"></i>
                por {version.author}
              </div>
              {version.changeDescription && (
                <div className="version-description mt-2">
                  <p className="text-regular">{version.changeDescription}</p>
                </div>
              )}
              {version.version !== currentVersion && (
                <div className="mt-3">
                  <button
                    onClick={() => onRestore(version.version)}
                    className="br-button secondary"
                    type="button"
                  >
                    <i className="fas fa-undo me-1"></i>
                    Restaurar esta versão
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};