import React, { useState } from 'react';
import { Upload, ChartBar, Send, MessageSquare } from 'lucide-react';
import BusinessDocumentUpload from '@/components/features/Analysis/BusinessDocumentUpload';
import BusinessAnalysisResults from '@/components/features/Analysis/BusinessAnalysisResults';
import PromptViewer from '@/components/features/Analysis/PromptViewer';
import LLMResponseViewer from '@/components/features/Analysis/LLMResponseViewer';
import { useBusinessAnalysisStore } from '@/stores/businessAnalysisStore';
import './BusinessAnalysisPage.css';

const BusinessAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'results' | 'prompt' | 'response'>('upload');

  const {
    businessDocuments,
    selectedDocuments,
    isUploading,
    isAnalyzing,
    currentAnalysis,
    lastPromptSent,
    lastLLMResponse,
    startAnalysis,
    uploadDocuments
  } = useBusinessAnalysisStore();

  const handleDocumentsUploaded = (documents: any[]) => {
    uploadDocuments(documents);
  };

  const handleStartAnalysis = () => {
    startAnalysis();
    // Auto-switch to results tab after starting analysis
    setActiveTab('results');
  };

  const handleDownloadReport = () => {
    if (currentAnalysis) {
      alert('Relatório de análise de negócio baixado com sucesso!');
      console.log('Business Analysis Report:', currentAnalysis);
    }
  };

  return (
    <div className="business-analysis-page">
      {/* Header */}
      <div className="business-analysis-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h1">Análise de Negócio</h1>
            <p className="text-regular">
              Upload de documentação negocial e análise de alinhamento com o código-fonte
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Following DSGov pattern like GeneralAnalysisPage */}
      <div className="br-tabs" data-tabs="business-analysis-tabs">
        <nav className="tab-navigation" role="tablist">
          {[
            { id: 'upload', name: 'Upload documentação negocial', icon: Upload },
            { id: 'results', name: 'Resultados', icon: ChartBar },
            { id: 'prompt', name: 'Último Prompt Enviado', icon: Send },
            { id: 'response', name: 'Última Resposta da LLM', icon: MessageSquare }
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
          <BusinessDocumentUpload
            onDocumentsUploaded={handleDocumentsUploaded}
            onStartAnalysis={handleStartAnalysis}
          />
        )}

        {activeTab === 'results' && (
          <BusinessAnalysisResults
            results={currentAnalysis}
            onDownloadReport={handleDownloadReport}
          />
        )}

        {activeTab === 'prompt' && (
          <PromptViewer />
        )}

        {activeTab === 'response' && (
          <LLMResponseViewer />
        )}
      </div>
    </div>
  );
};

export default BusinessAnalysisPage;