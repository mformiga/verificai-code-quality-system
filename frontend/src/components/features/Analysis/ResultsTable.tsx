import React, { useState } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Edit3,
  Download,
  ExternalLink
} from 'lucide-react';
import { CodeBlock } from '@/components/common/CodeBlock';

interface CodeEvidence {
  code: string;
  language: string;
  filePath: string;
  lineNumbers?: [number, number];
}

interface CriteriaResult {
  criterion: string;
  assessment: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  confidence: number;
  evidence: CodeEvidence[];
  recommendations: string[];
}

interface ResultsTableProps {
  results: CriteriaResult[];
  onEditResult: (criterion: string, result: Partial<CriteriaResult>) => void;
  onDownloadReport: () => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({
  results,
  onEditResult,
  onDownloadReport
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (criterion: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(criterion)) {
      newExpanded.delete(criterion);
    } else {
      newExpanded.add(criterion);
    }
    setExpandedRows(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'partially_compliant':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'non_compliant':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <HelpCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'Conforme';
      case 'partially_compliant':
        return 'Parcialmente Conforme';
      case 'non_compliant':
        return 'Não Conforme';
      default:
        return 'Não Avaliado';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'partially_compliant':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'non_compliant':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatAssessment = (assessment: string) => {
    return assessment.split('\n').map((line, index) => (
      <p key={index} className="mb-2 last:mb-0">
        {line}
      </p>
    ));
  };

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <HelpCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-800 mb-2">
          Nenhum resultado disponível
        </h3>
        <p className="text-gray-600">
          Aguarde a conclusão da análise ou inicie uma nova análise.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Resultados da Análise</h2>
          <button
            onClick={onDownloadReport}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Baixar Relatório
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Critério
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avaliação
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {results.map((result) => (
              <React.Fragment key={result.criterion}>
                <tr className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(result.status)}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                        {getStatusText(result.status)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {result.criterion}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Confiança: {Math.round(result.confidence * 100)}%
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-md">
                      {result.assessment.length > 150 ? (
                        <>
                          {result.assessment.substring(0, 150)}...
                          <button
                            onClick={() => toggleRow(result.criterion)}
                            className="text-blue-600 hover:text-blue-800 ml-1 text-xs"
                          >
                            Ver mais
                          </button>
                        </>
                      ) : (
                        result.assessment
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => toggleRow(result.criterion)}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                        title={expandedRows.has(result.criterion) ? 'Recolher' : 'Expandir'}
                      >
                        {expandedRows.has(result.criterion) ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => onEditResult(result.criterion, result)}
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Editar manualmente"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedRows.has(result.criterion) && (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 bg-gray-50">
                      <div className="space-y-6">
                        {/* Avaliação Completa */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-800 mb-2">
                            Avaliação Completa
                          </h4>
                          <div className="text-sm text-gray-700 bg-white p-4 rounded border border-gray-200">
                            {formatAssessment(result.assessment)}
                          </div>
                        </div>

                        {/* Evidências */}
                        {result.evidence.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-gray-800 mb-3">
                              Evidências
                            </h4>
                            <div className="space-y-3">
                              {result.evidence.map((evidence, index) => (
                                <div key={index} className="bg-white rounded border border-gray-200">
                                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
                                    <span className="text-sm font-medium text-gray-700">
                                      {evidence.filePath}
                                      {evidence.lineNumbers && (
                                        <span className="text-xs text-gray-500 ml-2">
                                          (Linhas {evidence.lineNumbers[0]}-{evidence.lineNumbers[1]})
                                        </span>
                                      )}
                                    </span>
                                    <ExternalLink className="w-4 h-4 text-gray-400" />
                                  </div>
                                  <div className="p-4">
                                    <CodeBlock
                                      code={evidence.code}
                                      language={evidence.language}
                                    />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Recomendações */}
                        {result.recommendations.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-gray-800 mb-3">
                              Recomendações
                            </h4>
                            <ul className="space-y-2">
                              {result.recommendations.map((recommendation, index) => (
                                <li
                                  key={index}
                                  className="text-sm text-gray-700 flex items-start gap-2"
                                >
                                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                                  {recommendation}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable;