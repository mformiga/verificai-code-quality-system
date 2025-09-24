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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-800">
            Editar Resultado Manualmente
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
            <div className="space-y-6">
              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={result.status}
                  onChange={(e) => setResult({
                    ...result,
                    status: e.target.value as CriteriaResult['status']
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {getStatusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Nível de Confiança */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nível de Confiança
                </label>
                <div className="flex items-center gap-4">
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
                    className="flex-1"
                  />
                  <span className="text-sm font-medium text-gray-700 min-w-[60px]">
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>
              </div>

              {/* Avaliação */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Avaliação
                </label>
                <textarea
                  value={assessmentText}
                  onChange={(e) => setAssessmentText(e.target.value)}
                  placeholder="Descreva a avaliação do critério em detalhes..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={6}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use markdown para formatação (## cabeçalhos, **negrito**, *itálico*, etc.)
                </p>
              </div>

              {/* Recomendações */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recomendações
                </label>
                <textarea
                  value={recommendationsText}
                  onChange={(e) => setRecommendationsText(e.target.value)}
                  placeholder="Digite as recomendações, uma por linha..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                />
                <p className="text-xs text-gray-500 mt-1">
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
            <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
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