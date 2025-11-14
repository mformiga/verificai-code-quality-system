import React, { useState } from 'react';
import { Save, X } from 'lucide-react';

interface CriteriaResult {
  criterion: string;
  assessment: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  confidence: number;
  evidence: Array<{
    code: string;
    language: string;
    filePath: string;
    lineNumbers?: [number, number];
  }>;
  recommendations: string[];
  resultId?: number;
  criterionKey?: string;
  criteriaId?: number;
}

interface ManualEditorProps {
  criterion: string;
  initialResult: CriteriaResult;
  onSave: (result: CriteriaResult) => void;
  onCancel: () => void;
}

const ManualEditor: React.FC<ManualEditorProps> = ({
  criterion,
  initialResult,
  onSave,
  onCancel
}) => {
  // Ensure initialResult has all required properties
  const safeInitialResult: CriteriaResult = {
    criterion: initialResult.criterion || '',
    assessment: initialResult.assessment || '',
    status: initialResult.status || 'partially_compliant',
    confidence: initialResult.confidence || 0.5,
    evidence: initialResult.evidence || [],
    recommendations: initialResult.recommendations || [],
    resultId: initialResult.resultId,
    criterionKey: initialResult.criterionKey,
    criteriaId: initialResult.criteriaId
  };

  const [result, setResult] = useState<CriteriaResult>(safeInitialResult);
  const [assessmentText, setAssessmentText] = useState(safeInitialResult.assessment);
  const [recommendationsText, setRecommendationsText] = useState(
    safeInitialResult.recommendations.join('\n')
  );

  const handleSave = () => {
    console.log('🔄 ManualEditor: handleSave called');
    const updatedResult = {
      ...result,
      assessment: assessmentText,
      recommendations: recommendationsText.split('\n').filter(r => r.trim())
    };
    console.log('🔄 ManualEditor: Calling onSave with:', updatedResult);
    onSave(updatedResult);
  };

  const getStatusOptions = [
    { value: 'compliant', label: 'Conforme' },
    { value: 'partially_compliant', label: 'Parcialmente Conforme' },
    { value: 'non_compliant', label: 'Não Conforme' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="br-card" style={{ maxWidth: '95vw', width: '1300px', maxHeight: '98vh', overflow: 'hidden' }}>
        {/* Header */}
        <div className="card-header">
          <div className="d-flex align-items-center justify-content-between">
            <h3 className="text-h3">
              Editar Resultado Manualmente
            </h3>
            <div className="d-flex align-items-center gap-2">
              <button
                type="button"
                onClick={handleSave}
                className="br-button primary"
                title="Salvar Alterações"
              >
                <Save className="w-4 h-4 mr-2" />
                Salvar
              </button>
              <button
                onClick={onCancel}
                className="br-button circle"
                title="Fechar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="card-content overflow-y-auto" style={{ maxHeight: 'calc(98vh - 140px)' }}>
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
            <div className="space-y-4">
              {/* Status */}
              <div className="br-input">
                <label className="br-label">
                  Status
                </label>
                <select
                  value={result.status}
                  onChange={(e) => setResult({
                    ...result,
                    status: e.target.value as CriteriaResult['status']
                  })}
                  className="br-select"
                >
                  {getStatusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Nível de Confiança */}
              <div className="br-input">
                <label className="br-label">
                  Nível de Confiança: {Math.round(result.confidence * 100)}%
                </label>
                <div className="d-flex align-items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={result.confidence}
                    onChange={(e) => setResult({
                      ...result,
                      confidence: parseFloat(e.target.value)
                    })}
                    className="br-range flex-1"
                    style={{ height: '8px' }}
                  />
                </div>
              </div>

              {/* Avaliação */}
              <div className="br-input">
                <label className="br-label">
                  Avaliação
                </label>
                <div className="br-textarea">
                  <textarea
                    value={assessmentText}
                    onChange={(e) => setAssessmentText(e.target.value)}
                    placeholder="Descreva a avaliação do critério em detalhes..."
                    rows={20}
                    style={{ minHeight: '400px', width: '100%', resize: 'vertical' }}
                  />
                </div>
                <p className="br-help-text">
                  Use markdown para formatação (## cabeçalhos, **negrito**, *itálico*, etc.)
                </p>
              </div>

              {/* Recomendações */}
              <div className="br-input">
                <label className="br-label">
                  Recomendações
                </label>
                <div className="br-textarea">
                  <textarea
                    value={recommendationsText}
                    onChange={(e) => setRecommendationsText(e.target.value)}
                    placeholder="Digite as recomendações, uma por linha..."
                    rows={8}
                    style={{ width: '100%', resize: 'vertical' }}
                  />
                </div>
                <p className="br-help-text">
                  Digite uma recomendação por linha
                </p>
              </div>

              {/* Preview */}
              <div className="border-t pt-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">
                  Visualização
                </h4>
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div>
                    <span className="text-xs text-gray-500">Status:</span>
                    <span className="ml-2 px-2 py-1 rounded-full text-xs font-medium">
                      {getStatusOptions.find(opt => opt.value === result.status)?.label}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Confiança:</span>
                    <span className="ml-2 text-sm">{Math.round(result.confidence * 100)}%</span>
                  </div>
                  {assessmentText && (
                    <div>
                      <span className="text-xs text-gray-500">Avaliação:</span>
                      <div className="mt-1 text-sm bg-white p-2 rounded border">
                        {assessmentText.split('\n').map((line, i) => (
                          <p key={i} className="mb-1 last:mb-0">{line}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="d-flex justify-content-end gap-3 mt-4 pt-4 border-top">
              <button
                type="button"
                onClick={onCancel}
                className="br-button secondary"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="br-button primary"
              >
                <Save className="w-4 h-4 mr-2" />
                Salvar Alterações
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ManualEditor;