import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '@/pages/LoginPage';

// Componente simples de Dashboard
const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h3">Bem-vindo ao VerificAI!</h1>
            <p className="text-regular text-muted mt-2">
              Sistema de Qualidade de Código com IA
            </p>
          </div>
          <div className="card-content">
            <div className="br-grid">
              <div className="text-center">
                <h2 className="text-h2 mb-4">🎉 Login realizado com sucesso!</h2>
                <p className="text-regular mb-6">
                  Você está autenticado no sistema. Abaixo estão as funcionalidades disponíveis:
                </p>

                <div className="br-list">
                  <div className="br-item">
                    <span className="br-list-title">⚙️</span>
                    <span className="br-list-text">Configuração de Prompts</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">📁</span>
                    <span className="br-list-text">Upload de Código</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">📊</span>
                    <span className="br-list-text">Análise Geral</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">🏗️</span>
                    <span className="br-list-text">Análise Arquitetural</span>
                  </div>
                  <div className="br-item">
                    <span className="br-list-title">💼</span>
                    <span className="br-list-text">Análise de Negócio</span>
                  </div>
                </div>

                <div className="mt-6">
                  <button
                    onClick={() => {
                      // Simples logout - limpar o storage
                      localStorage.removeItem('auth-storage');
                      window.location.reload();
                    }}
                    className="br-button secondary"
                  >
                    Sair do Sistema
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <Routes>
      {/* Dashboard protegido */}
      <Route path="/dashboard" element={<DashboardPage />} />

      {/* Login */}
      <Route path="/login" element={<LoginPage />} />

      {/* Redirecionar raiz para dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;