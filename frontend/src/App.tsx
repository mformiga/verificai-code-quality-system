import React from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import LoginPage from '@/pages/LoginPage';
import PromptConfigPage from '@/pages/PromptConfigPage';
import CodeUploadPage from '@/pages/CodeUploadPage';
import GeneralAnalysisPage from '@/pages/GeneralAnalysisPage';
import ArchitecturalAnalysisPage from '@/pages/ArchitecturalAnalysisPage';
import BusinessAnalysisPage from '@/pages/BusinessAnalysisPage';

// Componente de proteção de rotas
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

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
                  <Link to="/prompt-config" className="br-item">
                    <span className="br-list-title">⚙️</span>
                    <span className="br-list-text">Configuração de Prompts</span>
                  </Link>
                  <Link to="/code-upload" className="br-item">
                    <span className="br-list-title">📁</span>
                    <span className="br-list-text">Upload de Código</span>
                  </Link>
                  <Link to="/general-analysis" className="br-item">
                    <span className="br-list-title">📊</span>
                    <span className="br-list-text">Análise Geral</span>
                  </Link>
                  <Link to="/architectural-analysis" className="br-item">
                    <span className="br-list-title">🏗️</span>
                    <span className="br-list-text">Análise Arquitetural</span>
                  </Link>
                  <Link to="/business-analysis" className="br-item">
                    <span className="br-list-title">💼</span>
                    <span className="br-list-text">Análise de Negócio</span>
                  </Link>
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
  // Efeito para inicialização do aplicativo
  React.useEffect(() => {
    // Remover apenas dados de autenticação inválidos se existirem
    const authData = localStorage.getItem('auth-storage');
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        // Verificar se há estado inválido (sem usuário ou token)
        if (!parsed.state?.user || !parsed.state?.token) {
          localStorage.removeItem('auth-storage');
        }
      } catch (error) {
        // Remover dados corrompidos
        localStorage.removeItem('auth-storage');
      }
    }
  }, []);

  return (
    <Routes>
      {/* Dashboard protegido */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      } />

      {/* Páginas de funcionalidades protegidas */}
      <Route path="/prompt-config" element={
        <ProtectedRoute>
          <PromptConfigPage />
        </ProtectedRoute>
      } />
      <Route path="/code-upload" element={
        <ProtectedRoute>
          <CodeUploadPage />
        </ProtectedRoute>
      } />
      <Route path="/general-analysis" element={
        <ProtectedRoute>
          <GeneralAnalysisPage />
        </ProtectedRoute>
      } />
      <Route path="/architectural-analysis" element={
        <ProtectedRoute>
          <ArchitecturalAnalysisPage />
        </ProtectedRoute>
      } />
      <Route path="/business-analysis" element={
        <ProtectedRoute>
          <BusinessAnalysisPage />
        </ProtectedRoute>
      } />

      {/* Login - acessível apenas se não estiver autenticado */}
      <Route path="/login" element={
        <PublicRoute>
          <LoginPage />
        </PublicRoute>
      } />

      {/* Redirecionar raiz para dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

// Componente para rotas públicas (redireciona se já estiver autenticado)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
};

export default App;