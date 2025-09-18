import React from 'react';
import { CheckCircle, Circle, AlertCircle, XCircle, Loader2 } from 'lucide-react';

interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
  active: boolean;
}

interface ProgressTrackerProps {
  progress: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  message?: string;
  onCancel: () => void;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progress,
  status,
  message,
  onCancel
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-6 h-6 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-600" />;
      case 'cancelled':
        return <XCircle className="w-6 h-6 text-gray-600" />;
      default:
        return <Circle className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'pending':
        return 'Aguardando início da análise...';
      case 'processing':
        return message || `Processando análise... ${progress}%`;
      case 'completed':
        return 'Análise concluída com sucesso!';
      case 'failed':
        return 'Falha na análise';
      case 'cancelled':
        return 'Análise cancelada';
      default:
        return message || 'Preparando análise...';
    }
  };

  const getProgressColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-blue-600';
      case 'completed':
        return 'bg-green-600';
      case 'failed':
        return 'bg-red-600';
      case 'cancelled':
        return 'bg-gray-600';
      default:
        return 'bg-gray-300';
    }
  };

  const steps: AnalysisStep[] = [
    {
      id: 'preparing',
      name: 'Preparação',
      description: 'Preparando arquivos e configuração',
      icon: <Circle className="w-4 h-4" />,
      completed: progress >= 10,
      active: progress > 0 && progress < 30
    },
    {
      id: 'processing',
      name: 'Processamento',
      description: 'Otimizando conteúdo para análise',
      icon: <Circle className="w-4 h-4" />,
      completed: progress >= 30,
      active: progress >= 20 && progress < 50
    },
    {
      id: 'analyzing',
      name: 'Análise IA',
      description: 'Executando análise com inteligência artificial',
      icon: <Circle className="w-4 h-4" />,
      completed: progress >= 50,
      active: progress >= 40 && progress < 80
    },
    {
      id: 'finalizing',
      name: 'Finalização',
      description: 'Processando resultados e gerando relatório',
      icon: <Circle className="w-4 h-4" />,
      completed: progress >= 80,
      active: progress >= 70 && progress < 100
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Status da Análise</h2>
        {status === 'processing' && (
          <button
            onClick={onCancel}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Cancelar
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm font-medium text-gray-700">
              {getStatusMessage()}
            </span>
          </div>
          <span className="text-sm font-medium text-gray-700">
            {progress}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor()}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Analysis Steps */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Etapas da Análise</h3>
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                step.active
                  ? 'bg-blue-50 border border-blue-200'
                  : step.completed
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-gray-50 border border-gray-200'
              }`}
            >
              <div className="flex-shrink-0">
                {step.completed ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : step.active ? (
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${
                  step.active
                    ? 'text-blue-800'
                    : step.completed
                    ? 'text-green-800'
                    : 'text-gray-600'
                }`}>
                  {step.name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {step.description}
                </p>
              </div>
              {step.completed && (
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Additional Info */}
      {status === 'processing' && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Importante:</strong> Esta análise pode levar alguns minutos dependendo
            do tamanho do código e da complexidade dos critérios avaliados.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;