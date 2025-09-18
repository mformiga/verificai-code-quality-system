import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Save, X, Loader2 } from 'lucide-react';
import { criteriaService } from '@/services/criteriaService';

interface Criterion {
  id: string;
  text: string;
  active: boolean;
}

interface CriteriaListProps {
  onCriteriaSelect: (selected: string[]) => void;
}

const CriteriaList: React.FC<CriteriaListProps> = ({ onCriteriaSelect }) => {
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingCriterion, setEditingCriterion] = useState<string | null>(null);
  const [editingText, setEditingText] = useState('');

  useEffect(() => {
    loadCriteria();
  }, []);

  const loadCriteria = async () => {
    setLoading(true);
    try {
      const data = await criteriaService.getCriteria();
      setCriteria(data);
    } catch (error) {
      console.error('Failed to load criteria:', error);
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
    } catch (error) {
      console.error('Failed to create criterion:', error);
    }
  };

  const updateCriterion = async (id: string, updates: Partial<Criterion>) => {
    try {
      if (updates.text) {
        await criteriaService.updateCriterion(id, updates.text);
      }
      setCriteria(criteria.map(c =>
        c.id === id ? { ...c, ...updates } : c
      ));
    } catch (error) {
      console.error('Failed to update criterion:', error);
    }
  };

  const deleteCriterion = async (id: string) => {
    try {
      await criteriaService.deleteCriterion(id);
      // Reload the criteria list to ensure we have the latest data
      await loadCriteria();
      if (editingCriterion === id) {
        setEditingCriterion(null);
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
    if (editingCriterion && editingText.trim()) {
      await updateCriterion(editingCriterion, { text: editingText.trim() });
      setEditingCriterion(null);
      setEditingText('');
    }
  };

  const cancelEdit = () => {
    setEditingCriterion(null);
    setEditingText('');
  };

  const toggleCriterion = async (id: string) => {
    const criterion = criteria.find(c => c.id === id);
    if (criterion) {
      await updateCriterion(id, { active: !criterion.active });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Critérios de Avaliação</h2>
        <button
          onClick={addCriterion}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
          Novo Critério
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">Carregando critérios...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {criteria.map((criterion) => (
            <div
              key={criterion.id}
              className={`border rounded-lg p-4 transition-all ${
                criterion.active
                  ? 'border-blue-200 bg-blue-50'
                  : 'border-gray-200 bg-gray-50'
              } ${editingCriterion === criterion.id ? 'ring-2 ring-blue-400' : ''}`}
            >
              <div className="flex items-start gap-3">
                {/* Toggle Switch */}
                <div className="flex items-center h-6">
                  <button
                    onClick={() => toggleCriterion(criterion.id)}
                    disabled={loading}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      criterion.active ? 'bg-blue-600' : 'bg-gray-300'
                    } disabled:opacity-50`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        criterion.active ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                {/* Criterion Content */}
                <div className="flex-1 min-w-0">
                  {editingCriterion === criterion.id ? (
                    <div className="space-y-3">
                      <textarea
                        value={editingText}
                        onChange={(e) => setEditingText(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        rows={3}
                        placeholder="Digite o critério de avaliação..."
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={saveEdit}
                          disabled={loading}
                          className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 transition-colors flex items-center gap-1 disabled:opacity-50"
                        >
                          {loading ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Save className="w-4 h-4" />
                          )}
                          Salvar
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="bg-gray-600 text-white px-3 py-1 rounded-md hover:bg-gray-700 transition-colors flex items-center gap-1"
                        >
                          <X className="w-4 h-4" />
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-gray-800">{criterion.text}</p>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {editingCriterion !== criterion.id && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => startEdit(criterion)}
                      disabled={loading}
                      className="text-blue-600 hover:text-blue-800 transition-colors disabled:opacity-50"
                      title="Editar critério"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteCriterion(criterion.id)}
                      disabled={loading}
                      className="text-red-600 hover:text-red-800 transition-colors disabled:opacity-50"
                      title="Excluir critério"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {criteria.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">
                Nenhum critério configurado ainda.
              </p>
              <button
                onClick={addCriterion}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                Adicionar Primeiro Critério
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CriteriaList;