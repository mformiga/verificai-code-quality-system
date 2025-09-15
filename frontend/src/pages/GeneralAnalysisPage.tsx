import React from 'react';
import { useAnalysisStore } from '@/stores/analysisStore';

const GeneralAnalysisPage: React.FC = () => {
  const { currentAnalysis, results, loading, startAnalysis } = useAnalysisStore();

  const handleStartAnalysis = () => {
    startAnalysis({
      type: 'general',
      files: [], // Would come from upload store
      criteria: [], // Would come from prompt config
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Análise de Critérios Gerais</h1>

      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex flex-col items-center justify-center py-12">
            <div className="loading mb-4" aria-label="Analisando..." />
            <p className="text-gray-600">Analisando código...</p>
            {currentAnalysis && (
              <p className="text-sm text-gray-500 mt-2">
                Progresso: {currentAnalysis.progress}%
              </p>
            )}
          </div>
        </div>
      ) : results.length > 0 ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Resultados da Análise</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Critério
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Resultado
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result) => (
                  <tr key={result.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {result.criterion}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        result.status === 'pass' ? 'bg-green-100 text-green-800' :
                        result.status === 'fail' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {result.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-md">
                        <p className="mb-2">{result.details}</p>
                        {result.fileLocation && (
                          <p className="text-xs text-gray-500">
                            Arquivo: {result.fileLocation}
                            {result.lineNumber && `:${result.lineNumber}`}
                          </p>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">
              Nenhum código analisado ainda. Inicie uma nova análise para verificar os critérios gerais.
            </p>
            <button
              onClick={handleStartAnalysis}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Iniciar Análise
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeneralAnalysisPage;