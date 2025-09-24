import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Edit,
  Download,
  ExternalLink,
  Trash2,
  File
} from 'lucide-react';
import CodeBlock from '@/components/common/CodeBlock';
import { criteriaService } from '@/services/criteriaService';

interface CodeEvidence {
  code: string;
  language: string;
  filePath: string;
  lineNumbers?: [number, number];
}

interface CriteriaResult {
  id?: number;
  criterion: string;
  assessment: string;
  status: 'compliant' | 'partially_compliant' | 'non_compliant';
  confidence: number;
  evidence: CodeEvidence[];
  recommendations: string[];
  order?: number;
  // Para resultados carregados do banco, precisamos de uma referência ao ID do resultado pai
  resultId?: number;
  criterionKey?: string;
  criteriaId?: number;
}

interface ResultsTableProps {
  results: CriteriaResult[];
  onEditResult: (criterion: string, result: Partial<CriteriaResult>) => void;
  onDownloadDocx: () => void;
  onDeleteResults?: (selectedIds: number[]) => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({
  results,
  onEditResult,
  onDownloadDocx,
  onDeleteResults
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set());
  const [showDeleteButton, setShowDeleteButton] = useState(false);
  const [fullCriteriaText, setFullCriteriaText] = useState<{[key: string]: string}>({});
  const [allCriteria, setAllCriteria] = useState<any[]>([]);

  
  // Debug log
  console.log('🔍 ResultsTable renderizado com:', results.length, 'resultados');
  console.log('🔍 IDs dos resultados:', results.map(r => ({ id: r.id, criterion: r.criterion.substring(0, 50) + '...' })));
  console.log('🔍 Resultados com IDs válidos:', results.filter(r => r.id !== undefined && !isNaN(r.id)).length, 'de', results.length);
  console.log('🔍 Resultados com IDs inválidos:', results.filter(r => r.id === undefined || isNaN(r.id)).length, 'de', results.length);

  // Carregar todos os critérios para obter o texto completo
  useEffect(() => {
    const loadAllCriteria = async () => {
      try {
        const criteria = await criteriaService.getCriteria();
        setAllCriteria(criteria);

        // Criar mapeamento de nome do critério para texto completo
        const textMapping: {[key: string]: string} = {};
        criteria.forEach(criterion => {
          // Extrair o nome curto do critério (parte antes dos dois pontos, se existir)
          const shortName = criterion.text.split(':')[0];
          textMapping[shortName] = criterion.text;
          textMapping[criterion.text] = criterion.text; // Também mapear o texto completo
        });

        setFullCriteriaText(textMapping);
        console.log('🔍 Critérios carregados:', criteria.length, 'mapeamento criado');
      } catch (error) {
        console.error('Erro ao carregar critérios:', error);
      }
    };

    loadAllCriteria();
  }, []);

  // Função para obter o texto completo do critério
  const getFullCriterionText = (criterionName: string) => {
    // Tentar encontrar correspondência exata primeiro
    if (fullCriteriaText[criterionName]) {
      return fullCriteriaText[criterionName];
    }

    // Tentar encontrar por substring
    const matchingCriterion = allCriteria.find(criterion =>
      criterion.text.includes(criterionName) || criterionName.includes(criterion.text.split(':')[0])
    );

    return matchingCriterion ? matchingCriterion.text : criterionName;
  };

  // Sort results by order number and assign temporary IDs if needed
  const sortedResults = [...results].sort((a, b) => (a.order || 0) - (b.order || 0))
    .map((result, index) => ({
      ...result,
      id: result.id || (Date.now() + index), // Generate temporary ID if none exists
      displayOrder: index + 1
    }));

  const toggleRow = (criterion: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(criterion)) {
      newExpanded.delete(criterion);
    } else {
      newExpanded.add(criterion);
    }
    setExpandedRows(newExpanded);
  };

  
  const handleSelectResult = (resultId: number) => {
    console.log('🔍 handleSelectResult chamado com resultId:', resultId);
    console.log('🔍 selectedResults antes:', Array.from(selectedResults));

    const newSelected = new Set(selectedResults);
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId);
      console.log('🔍 Removendo resultId da seleção');
    } else {
      newSelected.add(resultId);
      console.log('🔍 Adicionando resultId à seleção');
    }

    console.log('🔍 selectedResults depois:', Array.from(newSelected));
    setSelectedResults(newSelected);
    setShowDeleteButton(newSelected.size > 0);
  };

  const handleSelectAll = () => {
    // Agora todos os resultados têm IDs graças à atribuição acima
    const allIds = sortedResults.map(r => r.id) as number[];

    if (selectedResults.size === allIds.length) {
      setSelectedResults(new Set());
      setShowDeleteButton(false);
    } else {
      setSelectedResults(new Set(allIds));
      setShowDeleteButton(true);
    }
  };

  const handleDeleteSelected = () => {
    if (selectedResults.size > 0 && onDeleteResults) {
      onDeleteResults(Array.from(selectedResults));
      setSelectedResults(new Set());
      setShowDeleteButton(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'partially_compliant':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'non_compliant':
        return <XCircle className="w-4 h-4 text-danger" />;
      default:
        return <HelpCircle className="w-4 h-4 text-muted" />;
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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'partially_compliant':
        return 'warning';
      case 'non_compliant':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  const formatAssessment = (assessment: string) => {
    return assessment.split('\n\n').map((paragraph, pIndex) => (
      <div key={pIndex} className="mb-3 last:mb-0">
        {paragraph.split('\n').map((line, lIndex) => {
          // Check if line is a heading (starts with #)
          if (line.trim().startsWith('#')) {
            const headingLevel = line.trim().match(/^#+/)?.[0].length || 1;
            const headingText = line.trim().replace(/^#+\s*/, '');
            const HeadingTag = `h${Math.min(headingLevel + 2, 6)}` as keyof JSX.IntrinsicElements;
            return (
              <HeadingTag key={`${pIndex}-${lIndex}`} className={`mt-4 mb-2 text-h${Math.min(headingLevel + 2, 6)}`}>
                {headingText}
              </HeadingTag>
            );
          }

          // Check if line is a list item (starts with - or *)
          if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
            const itemText = line.trim().replace(/^[-*]\s*/, '');
            return (
              <div key={`${pIndex}-${lIndex}`} className="d-flex align-items-start mb-1 ms-3">
                <div className="w-2 h-2 bg-primary rounded-circle mt-2 flex-shrink-0 me-2" />
                <span className="text-regular">{itemText}</span>
              </div>
            );
          }

          // Regular paragraph line
          return (
            <p key={`${pIndex}-${lIndex}`} className="mb-2 last:mb-0">
              {line}
            </p>
          );
        })}
      </div>
    ));
  };

  if (results.length === 0) {
    return (
      <div className="br-card text-center">
        <div className="card-content">
          <HelpCircle className="w-12 h-12 text-muted mx-auto mb-4" />
          <h3 className="text-h3 text-muted mb-2">
            Nenhum resultado disponível
          </h3>
          <p className="text-regular text-muted">
            Aguarde a conclusão da análise ou inicie uma nova análise.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="br-card">
      <div className="card-header">
        <div className="row align-items-center">
          <div className="br-col">
            <h2 className="text-h2">Resultados da Análise</h2>
            <p className="text-regular text-muted">
              {results.length > 0
                ? `Análise concluída com ${results.length} critérios avaliados`
                : 'Nenhuma análise concluída ainda'
              }
            </p>
          </div>
          <div className="br-col-auto">
            <div className="d-flex gap-2">
              {showDeleteButton && (
                <button
                  onClick={handleDeleteSelected}
                  className="br-button danger"
                  title={`Excluir ${selectedResults.size} resultado(s) selecionado(s)`}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Excluir ({selectedResults.size})
                </button>
              )}
              {results.length > 0 && (
                <button
                  onClick={onDownloadDocx}
                  className="br-button secondary"
                  title="Baixar relatório em formato DOCX editável"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Baixar Relatório (DOCX)
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card-content p-0">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th className="text-center" style={{ width: '50px' }}>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={results.length > 0 && selectedResults.size === sortedResults.length}
                    onChange={handleSelectAll}
                    disabled={results.length === 0}
                    title="Selecionar todos"
                  />
                </th>
                <th>
                  Status
                </th>
                <th>
                  Critério
                </th>
                <th>
                  Avaliação
                </th>
                <th className="text-center">
                  Ações
                </th>
              </tr>
            </thead>
          <tbody>
            {sortedResults.map((result) => (
              <React.Fragment key={result.criterion}>
                <tr style={{
                  borderBottom: '1px solid #e9ecef'
                }}>
                  {/* Checkbox de seleção */}
                  <td className="text-center align-middle" style={{
                    width: '60px',
                    backgroundColor: '#f8f9fa',
                    borderRight: '3px solid #dee2e6',
                    verticalAlign: 'middle',
                    padding: '16px 8px',
                    borderBottom: '1px solid #e9ecef'
                  }}>
                    <div className="d-flex align-items-center justify-content-center">
                      <input
                        type="checkbox"
                        className="form-check-input me-2"
                        checked={result.id ? selectedResults.has(result.id) : false}
                        onChange={() => {
                          console.log('🔍 Checkbox clicado para resultado:', result.criterion.substring(0, 30) + '...', 'ID:', result.id);
                          if (result.id) {
                            handleSelectResult(result.id);
                          } else {
                            console.log('🔍 ID inválido, não pode selecionar');
                          }
                        }}
                        disabled={!result.id}
                        title={result.id ? "Selecionar resultado" : "ID inválido - não pode selecionar"}
                      />
                      <span className="text-regular fw-bold text-dark">
                        {result.displayOrder}
                      </span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="align-middle" style={{
                    borderRight: '1px solid #e9ecef',
                    padding: '16px 12px',
                    borderBottom: '1px solid #e9ecef'
                  }}>
                    <div className="d-flex align-items-center gap-2">
                      {getStatusIcon(result.status)}
                      <span className={`badge bg-${getStatusBadge(result.status)}`}>
                        {getStatusText(result.status)}
                      </span>
                    </div>
                  </td>

                  {/* Critério */}
                  <td className="align-middle" style={{
                    width: '35%',
                    borderRight: '1px solid #e9ecef',
                    padding: '16px 12px',
                    borderBottom: '1px solid #e9ecef'
                  }}>
                    <div>
                      <div className="text-regular fw-medium">
                        {getFullCriterionText(result.criterion)}
                      </div>
                      <div className="text-small text-muted mt-1">
                        Confiança: {Math.round(result.confidence * 100)}%
                      </div>
                    </div>
                  </td>

                  {/* Avaliação Resumida */}
                  <td className="align-middle" style={{
                    width: '45%',
                    borderRight: '1px solid #e9ecef',
                    padding: '16px 12px',
                    borderBottom: '1px solid #e9ecef'
                  }}>
                    <div className="text-regular text-truncate" style={{ maxWidth: 'none' }}>
                      {result.assessment.length > 100 ? (
                        <>
                          {result.assessment.substring(0, 100)}...
                          <button
                            onClick={() => toggleRow(result.criterion)}
                            className="btn btn-link p-0 ms-1 text-primary"
                          >
                            Ver mais
                          </button>
                        </>
                      ) : (
                        result.assessment
                      )}
                    </div>
                  </td>

                  {/* Ações */}
                  <td className="align-middle text-center" style={{
                    padding: '16px 12px',
                    borderBottom: '1px solid #e9ecef'
                  }}>
                    <div className="btn-group">
                      <button
                        onClick={() => toggleRow(result.criterion)}
                        className="br-button circle"
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
                        className="br-button circle warning"
                        title="Editar resultado (modal completo)"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedRows.has(result.criterion) && (
                  <tr>
                    <td colSpan={5} className="p-0">
                      <div className="br-item-expanded">
                        <div className="p-4">
                          {/* Avaliação */}
                          <div className="mb-4">
                            <div className="d-flex align-items-center justify-content-between mb-3">
                              <h4 className="text-h4">
                                Avaliação
                              </h4>
                            </div>
                            <div className="br-card">
                              <div className="card-content p-0">
                                <div className="p-4 text-regular" style={{
                                  maxHeight: '600px',
                                  overflowY: 'auto',
                                  whiteSpace: 'pre-wrap',
                                  wordWrap: 'break-word'
                                }}>
                                  {formatAssessment(result.assessment)}
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Evidências */}
                          {result.evidence.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-h4 mb-3">
                                Evidências
                              </h4>
                              <div className="space-y-3">
                                {result.evidence.map((evidence, index) => (
                                  <div key={index} className="br-card">
                                    <div className="card-header">
                                      <div className="d-flex align-items-center justify-content-between">
                                        <span className="text-regular fw-medium">
                                          {evidence.filePath}
                                          {evidence.lineNumbers && (
                                            <span className="text-small text-muted ms-2">
                                              (Linhas {evidence.lineNumbers[0]}-{evidence.lineNumbers[1]})
                                            </span>
                                          )}
                                        </span>
                                        <ExternalLink className="w-4 h-4 text-muted" />
                                      </div>
                                    </div>
                                    <div className="card-content p-0">
                                      <div className="p-3">
                                        <CodeBlock
                                          code={evidence.code}
                                          language={evidence.language}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Recomendações */}
                          {result.recommendations.length > 0 && (
                            <div>
                              <h4 className="text-h4 mb-3">
                                Recomendações
                              </h4>
                              <ul className="list-unstyled">
                                {result.recommendations.map((recommendation, index) => (
                                  <li
                                    key={index}
                                    className="d-flex align-items-start gap-2 mb-2"
                                  >
                                    <div className="w-2 h-2 bg-primary rounded-circle mt-2 flex-shrink-0" />
                                    <span className="text-regular">{recommendation}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
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
    </div>
  );
};

export default ResultsTable;