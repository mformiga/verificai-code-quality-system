import React, { useState } from 'react';
import { Plus, Edit2, Trash2, Save, X } from 'lucide-react';

interface Criterion {
  id: string;
  text: string;
  active: boolean;
  createdAt: Date;
}

interface CriteriaListProps {
  criteria: Criterion[];
  onCriteriaChange: (criteria: Criterion[]) => void;
  onCriteriaSelect: (selected: string[]) => void;
}

const CriteriaList: React.FC<CriteriaListProps> = ({
  criteria,
  onCriteriaChange,
  onCriteriaSelect
}) => {
  const [editingCriterion, setEditingCriterion] = useState<string | null>(null);
  const [editingText, setEditingText] = useState('');

  const addCriterion = () => {
    const newCriterion: Criterion = {
      id: `criteria_${Date.now()}`,
      text: 'Novo critério de avaliação',
      active: true,
      createdAt: new Date()
    };
    onCriteriaChange([...criteria, newCriterion]);
    setEditingCriterion(newCriterion.id);
    setEditingText(newCriterion.text);
  };

  const updateCriterion = (id: string, updates: Partial<Criterion>) => {
    onCriteriaChange(criteria.map(c =>
      c.id === id ? { ...c, ...updates } : c
    ));
  };

  const deleteCriterion = (id: string) => {
    onCriteriaChange(criteria.filter(c => c.id !== id));
    if (editingCriterion === id) {
      setEditingCriterion(null);
    }
  };

  const startEdit = (criterion: Criterion) => {
    setEditingCriterion(criterion.id);
    setEditingText(criterion.text);
  };

  const saveEdit = () => {
    if (editingCriterion && editingText.trim()) {
      updateCriterion(editingCriterion, { text: editingText.trim() });
      setEditingCriterion(null);
      setEditingText('');
    }
  };

  const cancelEdit = () => {
    setEditingCriterion(null);
    setEditingText('');
  };

  const toggleCriterion = (id: string) => {
    const criterion = criteria.find(c => c.id === id);
    if (criterion) {
      updateCriterion(id, { active: !criterion.active });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Critérios de Avaliação</h2>
        <button
          onClick={addCriterion}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Novo Critério
        </button>
      </div>

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
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    criterion.active ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
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
                        className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 transition-colors flex items-center gap-1"
                      >
                        <Save className="w-4 h-4" />
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
                    <p className="text-sm text-gray-500 mt-1">
                      Criado em {criterion.createdAt.toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              {editingCriterion !== criterion.id && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => startEdit(criterion)}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                    title="Editar critério"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteCriterion(criterion.id)}
                    className="text-red-600 hover:text-red-800 transition-colors"
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
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
            >
              <Plus className="w-4 h-4" />
              Adicionar Primeiro Critério
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CriteriaList;