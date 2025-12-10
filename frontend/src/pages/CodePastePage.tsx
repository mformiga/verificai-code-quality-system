/**
 * Code Paste Page
 * Main page for the code paste interface functionality
 */

import React, { useState } from 'react';
import { Code, FileText, AlertCircle, Settings } from 'lucide-react';
import { SimpleCodeInterface } from '../components/features/CodeInput/SimpleCodeInterface';
import { useAuthStore } from '../stores/authStore';
import './CodePastePage.css';

const CodePastePage: React.FC = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'paste' | 'history'>('paste');

  // Handle code save success
  const handleCodeSave = (codeData: any) => {
    console.log('Code saved successfully:', codeData);
  };

  // Handle code delete
  const handleCodeDelete = (codeId: string) => {
    console.log('Code deleted:', codeId);
  };

  // Handle errors
  const handleError = (error: string) => {
    console.error('Code entry error:', error);
  };

  return (
    <div className="code-paste-page">
      {/* Page Header - Following DSGov pattern like other pages */}
      <div className="code-paste-header">
        <div className="br-card">
          <div className="card-header">
            <div className="row align-items-center">
              <div className="br-col">
                <h1 className="text-h1">Interface de Colagem de Código</h1>
                <p className="text-regular">
                  Cole seus trechos de código fonte e salve-os para referência posterior.
                  A detecção de idioma é automática e os códigos ficam disponíveis para análise nos critérios gerais.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Following DSGov pattern like GeneralAnalysisPage and BusinessAnalysisPage */}
      <div className="br-tabs" data-tabs="code-paste-tabs">
        <nav className="tab-navigation" role="tablist">
          {[
            { id: 'paste', name: 'Colar Código', icon: Code },
            { id: 'history', name: 'Histórico', icon: FileText }
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
        {user ? (
          <>
            {activeTab === 'paste' && (
              <div className="tab-content" id="tab-paste">
                <div className="br-card">
                  <div className="card-header">
                    <h2 className="text-h2">Colar Novo Código</h2>
                    <p className="text-regular text-muted">
                      Insira seu código no campo abaixo. O sistema detectará automaticamente a linguagem de programação.
                    </p>
                  </div>
                  <div className="card-content">
                    <SimpleCodeInterface
                      onCodeSave={handleCodeSave}
                      onCodeDelete={handleCodeDelete}
                      onError={handleError}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="tab-content" id="tab-history">
                <div className="br-card">
                  <div className="card-header">
                    <h2 className="text-h2">Histórico de Códigos</h2>
                    <p className="text-regular text-muted">
                      Visualize e gerencie os códigos que você salvou anteriormente.
                    </p>
                  </div>
                  <div className="card-content">
                    <div className="br-list" aria-label="Lista de códigos salvos">
                      <div className="br-item empty-state" style={{
                        textAlign: 'center',
                        padding: '3rem 1rem',
                        color: '#6c757d'
                      }}>
                        <Settings className="w-12 h-12 mx-auto mb-3" style={{ opacity: 0.5 }} />
                        <h3 className="text-h3" style={{ marginBottom: '0.5rem', color: '#495057' }}>
                          Funcionalidade em Desenvolvimento
                        </h3>
                        <p className="text-regular" style={{ margin: 0, maxWidth: '400px', marginLeft: 'auto', marginRight: 'auto' }}>
                          O histórico de códigos salvos estará disponível em breve.
                          Enquanto isso, você pode continuar colando novos códigos na aba anterior.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="br-card">
            <div className="card-content">
              <div className="br-alert br-alert-info">
                <div className="alert-header">
                  <AlertCircle className="w-5 h-5" />
                  <span>Acesso Requerido</span>
                </div>
                <div className="alert-content">
                  <p>Por favor, faça login para usar a interface de colagem de código.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodePastePage;