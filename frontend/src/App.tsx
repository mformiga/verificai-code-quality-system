import React from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import LoginPage from '@/pages/LoginPage';
import PromptConfigPage from '@/pages/PromptConfigPage';
import CodeUploadPage from '@/pages/CodeUploadPage';
import GeneralAnalysisPage from '@/pages/GeneralAnalysisPage';
import ArchitecturalAnalysisPage from '@/pages/ArchitecturalAnalysisPage';
import BusinessAnalysisPage from '@/pages/BusinessAnalysisPage';
import './pages/DashboardPage.css';

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
    <div className="dashboard-page">
      {/* Header */}
      <div className="dashboard-header">
        <div className="br-card">
          <div className="card-header text-center">
            <h1 className="text-h3">Bem-vindo ao VerificAI!</h1>
            <p className="text-regular">
              Sistema de Qualidade de Código com IA
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="br-card">
          <div className="card-content">
            <div className="welcome-section">
              <h2 className="text-h2">🎉 Login realizado com sucesso!</h2>
              <p className="text-regular">
                Você está autenticado no sistema. Abaixo estão as funcionalidades disponíveis:
              </p>
            </div>

            {/* Features Grid */}
            <div className="features-grid">
              <Link to="/prompt-config" className="feature-card">
                <span className="feature-icon">⚙️</span>
                <h3 className="feature-title">Configuração de Prompts</h3>
                <p className="feature-description">
                  Configure e gerencie os prompts de análise de código
                </p>
              </Link>

              <Link to="/code-upload" className="feature-card">
                <span className="feature-icon">📁</span>
                <h3 className="feature-title">Upload de Código</h3>
                <p className="feature-description">
                  Faça upload dos arquivos de código para análise
                </p>
              </Link>

              <Link to="/general-analysis" className="feature-card">
                <span className="feature-icon">📊</span>
                <h3 className="feature-title">Análise Geral</h3>
                <p className="feature-description">
                  Análise de código baseada em critérios gerais de qualidade
                </p>
              </Link>

              <Link to="/architectural-analysis" className="feature-card">
                <span className="feature-icon">🏗️</span>
                <h3 className="feature-title">Análise Arquitetural</h3>
                <p className="feature-description">
                  Avaliação da arquitetura e estrutura do projeto
                </p>
              </Link>

              <Link to="/business-analysis" className="feature-card">
                <span className="feature-icon">💼</span>
                <h3 className="feature-title">Análise de Negócio</h3>
                <p className="feature-description">
                  Análise de impacto e valor de negócio do código
                </p>
              </Link>
            </div>

            {/* Features List (fallback for mobile) */}
            <div className="features-list">
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
            </div>

            {/* Logout Section */}
            <div className="logout-section">
              <button
                onClick={() => {
                  // Simples logout - limpar o storage
                  localStorage.removeItem('auth-storage');
                  window.location.reload();
                }}
                className="logout-button"
              >
                Sair do Sistema
              </button>
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
    // Criar usuário de desenvolvimento para testes
    const devUser = {
      user: {
        id: 'dev-user-1',
        username: 'dev',
        email: 'dev@verificai.com',
        full_name: 'Developer User'
      },
      token: 'dev-token-12345',
      isAuthenticated: true,
      isLoading: false
    };

    // Verificar se já existe um usuário autenticado
    const authData = localStorage.getItem('auth-storage');
    if (!authData) {
      // Criar usuário de desenvolvimento
      localStorage.setItem('auth-storage', JSON.stringify({ state: devUser }));
    } else {
      try {
        const parsed = JSON.parse(authData);
        // Verificar se há estado inválido (sem usuário ou token)
        if (!parsed.state?.user || !parsed.state?.token) {
          localStorage.setItem('auth-storage', JSON.stringify({ state: devUser }));
        }
      } catch (error) {
        // Remover dados corrompidos e criar usuário de desenvolvimento
        localStorage.setItem('auth-storage', JSON.stringify({ state: devUser }));
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