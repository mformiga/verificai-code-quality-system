import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Save, X, Loader2, Play, Square, CheckSquare } from 'lucide-react';
import { criteriaService } from '@/services/criteriaService';

interface Criterion {
  id: number | string;
  text: string;
  active: boolean;
  order: number;
}

interface CriteriaListProps {
  onCriteriaSelect: (selected: number[]) => void;
  onAnalyzeCriterion?: (criterion: Criterion) => void;
  onAnalyzeSelected?: (selected: string[]) => void;
  onCriteriaChange?: () => void;
}

const CriteriaList: React.FC<CriteriaListProps> = ({ onCriteriaSelect, onAnalyzeCriterion, onAnalyzeSelected, onCriteriaChange }) => {
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingCriterion, setEditingCriterion] = useState<number | null>(null);
  const [editingText, setEditingText] = useState('');
  const [selectedCriteria, setSelectedCriteria] = useState<Set<number>>(new Set());

  // Debug: Log criteria changes
  useEffect(() => {
    console.log('🔍 DEBUG: Criteria state changed:', criteria);
  }, [criteria]);

  // Sort criteria by order number and assign display numbers
  const sortedCriteria = [...criteria].sort((a, b) => (a.order || 0) - (b.order || 0))
    .map((criterion, index) => ({
      ...criterion,
      displayOrder: index + 1
    }));

  useEffect(() => {
    loadCriteria();
  }, []);

  const loadCriteria = async () => {
    setLoading(true);
    try {
      console.log('🔍 DEBUG: Loading criteria...');
      const data = await criteriaService.getCriteria();
      console.log('🔍 DEBUG: Data received from service:', data);
      console.log('🔍 DEBUG: About to setCriteria with data length:', data.length);
      setCriteria(data);
      console.log('🔍 DEBUG: setCriteria called, current criteria state length:', criteria.length);
      console.log('🔍 DEBUG: State updated with', data.length, 'criteria');
    } catch (error) {
      console.error('🔍 DEBUG: Failed to load criteria:', error);
    } finally {
      setLoading(false);
    }
  };

  const addCriterion = async () => {
    try {
      const newCriterion = await criteriaService.createCriterion('Novo critério de avaliação');
      setCriteria([...criteria, newCriterion]);
      setEditingCriterion(newCriterion.id);
      setEditingText(newCriterion.text);

      // Notificar que os critérios mudaram
      if (onCriteriaChange) {
        onCriteriaChange();
      }
    } catch (error) {
      console.error('Failed to create criterion:', error);
    }
  };

  const updateCriterion = async (id: number, updates: Partial<Criterion>) => {
    try {
      console.log('🔍 DEBUG: updateCriterion called with:', id, updates);
      if (updates.text) {
        console.log('🔍 DEBUG: Calling criteriaService.updateCriterion...');
        await criteriaService.updateCriterion(id, updates.text);
        console.log('🔍 DEBUG: Service update completed');

        // Update the specific criterion in state directly
        const updatedCriteria = criteria.map(criterion =>
          criterion.id === id ? { ...criterion, text: updates.text || '' } : criterion
        );
        console.log('🔍 DEBUG: Updating state directly with:', updatedCriteria);
        setCriteria(updatedCriteria);

        // Also reload to ensure consistency with localStorage
        console.log('🔍 DEBUG: Reloading criteria for consistency...');
        await loadCriteria();
        console.log('🔍 DEBUG: Criteria reloaded');

        // Notificar que os critérios mudaram
        if (onCriteriaChange) {
          onCriteriaChange();
        }
      }
    } catch (error) {
      console.error('🔍 DEBUG: Failed to update criterion:', error);
    }
  };

  const deleteCriterion = async (id: number) => {
    try {
      await criteriaService.deleteCriterion(id);
      // Reload the criteria list to ensure we have the latest data
      await loadCriteria();
      if (editingCriterion === id) {
        setEditingCriterion(null);
      }

      // Notificar que os critérios mudaram
      if (onCriteriaChange) {
        onCriteriaChange();
      }
    } catch (error) {
      console.error('Failed to delete criterion:', error);
    }
  };

  const startEdit = (criterion: Criterion) => {
    setEditingCriterion(criterion.id);
    setEditingText(criterion.text);
  };

  const saveEdit = async () => {
    console.log('🔍 DEBUG: saveEdit called');
    console.log('🔍 DEBUG: editingCriterion:', editingCriterion);
    console.log('🔍 DEBUG: editingText:', editingText);

    if (editingCriterion && editingText.trim()) {
      console.log('🔍 DEBUG: Starting save edit...');
      console.log('🔍 DEBUG: Editing criterion:', editingCriterion);
      console.log('🔍 DEBUG: New text:', editingText.trim());

      try {
        console.log('🔍 DEBUG: About to call updateCriterion...');
        await updateCriterion(editingCriterion, { text: editingText.trim() });
        console.log('🔍 DEBUG: Update completed successfully');
        setEditingCriterion(null);
        setEditingText('');
        console.log('🔍 DEBUG: Edit mode closed');
      } catch (error) {
        console.error('🔍 DEBUG: Error in saveEdit:', error);
        console.error('🔍 DEBUG: Error details:', JSON.stringify(error, null, 2));
      }
    } else {
      console.log('🔍 DEBUG: Invalid input for save edit');
      console.log('🔍 DEBUG: editingCriterion is null/empty:', !editingCriterion);
      console.log('🔍 DEBUG: editingText is empty:', !editingText.trim());
    }
  };

  const cancelEdit = () => {
    setEditingCriterion(null);
    setEditingText('');
  };

  const toggleCriterion = async (id: number) => {
    const criterion = criteria.find(c => c.id === id);
    if (criterion) {
      try {
        await criteriaService.toggleCriterion(id, !criterion.active);
        // Reload criteria to ensure consistency with localStorage
        await loadCriteria();

        // Notificar que os critérios mudaram
        if (onCriteriaChange) {
          onCriteriaChange();
        }
      } catch (error) {
        console.error('Failed to toggle criterion:', error);
      }
    }
  };

  const handleAnalyze = (criterion: Criterion) => {
    if (onAnalyzeCriterion) {
      onAnalyzeCriterion(criterion);
    }
  };

  const toggleCriterionSelection = (id: number) => {
    const newSelected = new Set(selectedCriteria);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedCriteria(newSelected);
    // Converter para formato de string esperado pelo callback
    const stringIds = Array.from(newSelected).map(numericId => `criteria_${numericId}`);
    onCriteriaSelect(Array.from(newSelected));
  };

  const selectAllCriteria = () => {
    const allCriteriaIds = sortedCriteria.map(c => c.id);
    if (selectedCriteria.size === sortedCriteria.length) {
      setSelectedCriteria(new Set());
    } else {
      setSelectedCriteria(new Set(allCriteriaIds));
      // Ativar todos os critérios quando selecionar todos
      sortedCriteria.forEach(criterion => {
        if (!criterion.active) {
          toggleCriterion(criterion.id);
        }
      });
    }
    // Converter para formato de string esperado pelo callback
    const selectedIds = selectedCriteria.size === sortedCriteria.length ? [] : allCriteriaIds;
    onCriteriaSelect(selectedIds);
  };

  const isAllSelected = () => {
    return sortedCriteria.length > 0 && selectedCriteria.size === sortedCriteria.length;
  };

  const handleAnalyzeSelected = () => {
    if (onAnalyzeSelected && selectedCriteria.size > 0) {
      const selectedIds = sortedCriteria
        .filter(c => selectedCriteria.has(c.id))
        .map(c => c.id)
        .map(id => `criteria_${id}`);  // ✅ Convertendo para formato esperado pelo backend!
      onAnalyzeSelected(selectedIds);
    }
  };

  return (
    <div className="br-card">
      <div className="card-header">
        <div className="row align-items-center">
          <div className="br-col">
            <h2 className="text-h2">Critérios de Avaliação</h2>
            <p className="text-regular text-muted">
              Configure os critérios que serão usados para análise do código-fonte
            </p>
          </div>
          <div className="br-col-auto">
            <div className="btn-group">
              <button
                onClick={selectAllCriteria}
                disabled={loading || sortedCriteria.length === 0}
                className="br-button secondary"
              >
                {isAllSelected() ? <CheckSquare className="w-4 h-4 mr-2" /> : <Square className="w-4 h-4 mr-2" />}
                Selecionar Todos
              </button>
              <button
                onClick={handleAnalyzeSelected}
                disabled={loading || selectedCriteria.size === 0}
                className="br-button primary"
              >
                <Play className="w-4 h-4 mr-2" />
                Analisar Selecionados ({selectedCriteria.size})
              </button>
              <button
                onClick={addCriterion}
                disabled={loading}
                className="br-button primary"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Plus className="w-4 h-4 mr-2" />
                )}
                Novo Critério
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="card-content">
        {loading ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">Carregando critérios...</p>
          </div>
        ) : (
          <div className="space-y-4">
          {sortedCriteria.map((criterion) => (
            <div
              key={criterion.id}
              className={`br-item ${criterion.active ? 'is-active' : ''} ${editingCriterion === criterion.id ? 'ring-2 ring-blue-400' : ''}`}
            >
              <div className="row align-items-start">
                {/* Order Number Column - Primeira coluna */}
                <div style={{
                  width: '35px',
                  backgroundColor: '#e9ecef',
                  borderRight: '2px solid #adb5bd',
                  padding: '8px 4px',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: '40px'
                }}>
                  <span style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#495057'
                  }}>
                    {criterion.displayOrder}
                  </span>
                </div>

                {/* Selection/Activation Checkbox */}
                <div className="br-col-auto">
                  <div className="br-checkbox">
                    <input
                      type="checkbox"
                      id={`criterion-${criterion.id}`}
                      checked={selectedCriteria.has(criterion.id)}
                      onChange={() => {
                        toggleCriterionSelection(criterion.id);
                        if (!criterion.active) {
                          toggleCriterion(criterion.id);
                        }
                      }}
                      disabled={loading}
                    />
                    <label htmlFor={`criterion-${criterion.id}`} className="br-checkbox-label"></label>
                  </div>
                </div>

                {/* Criterion Content - Largura máxima */}
                <div className="br-col" style={{ maxWidth: 'none', flex: '1 1 0%' }}>
                  {editingCriterion === criterion.id ? (
                    <div className="space-y-3">
                      <textarea
                        value={editingText}
                        onChange={(e) => setEditingText(e.target.value)}
                        className="br-textarea"
                        rows={3}
                        placeholder="Digite o critério de avaliação..."
                        style={{ width: '100%', minWidth: '800px' }}
                      />
                      <div className="btn-group">
                        <button
                          onClick={saveEdit}
                          disabled={loading}
                          className="br-button success"
                        >
                          {loading ? (
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          ) : (
                            <Save className="w-4 h-4 mr-2" />
                          )}
                          Salvar
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="br-button secondary"
                        >
                          <X className="w-4 h-4 mr-2" />
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-regular">{criterion.text}</p>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {editingCriterion !== criterion.id && (
                  <div className="br-col-auto">
                    <div className="btn-group">
                      <button
                        onClick={() => startEdit(criterion)}
                        disabled={loading}
                        className="br-button circle"
                        title="Editar critério"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteCriterion(criterion.id)}
                        disabled={loading}
                        className="br-button circle"
                        title="Excluir critério"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      {onAnalyzeCriterion && (
                        <button
                          onClick={() => handleAnalyze(criterion)}
                          disabled={loading || !criterion.active}
                          className={`br-button circle ${criterion.active ? 'primary' : 'secondary'}`}
                          title="Analisar critério"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {sortedCriteria.length === 0 && (
            <div className="text-center py-8">
              <p className="text-regular text-muted mb-4">
                Nenhum critério configurado ainda.
              </p>
              <button
                onClick={addCriterion}
                disabled={loading}
                className="br-button primary mx-auto"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Plus className="w-4 h-4 mr-2" />
                )}
                Adicionar Primeiro Critério
              </button>
            </div>
          )}
        </div>
      )}
    </div>
    </div>
  );
};

export default CriteriaList;