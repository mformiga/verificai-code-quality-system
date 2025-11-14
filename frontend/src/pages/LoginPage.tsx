import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import './LoginPage.css';

const loginSchema = z.object({
  username: z.string().min(1, 'Nome de usuário é obrigatório'),
  password: z.string().min(1, 'Senha é obrigatória'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();

  // Definir título da página
  React.useEffect(() => {
    document.title = 'AVALIA Code Quality System - Login';
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      console.log('Tentando fazer login com:', data);
      await login(data);
      console.log('Login realizado com sucesso!');

      // Redirecionar para o dashboard após login bem-sucedido
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Erro no login:', error);
      alert('Erro ao fazer login. Verifique o console para mais detalhes.');
    }
  };

  return (
    <div className="login-page">
      {/* Logo and App Title */}
      <div className="logo-container">
        <div className="logo">
          <span className="logo-text">A</span>
        </div>
        <h1 className="app-title">AVAL<span style={{ color: '#EAB308' }}>IA</span></h1>
        <p className="app-subtitle">Sistema de Qualidade de Código com IA</p>
      </div>

      {/* Login Form */}
      <div className="login-form-container">
        <div className="br-card">
          <div className="card-header text-center">
            <h2 className="text-h2">Entrar na sua conta</h2>
            <p className="text-regular">
              Digite suas credenciais para acessar o sistema
            </p>
          </div>
          <div className="card-content">
            <form onSubmit={handleSubmit(onSubmit)} className="login-form">
              <div className="form-group">
                <label htmlFor="username" className="form-label">
                  Nome de usuário
                </label>
                <input
                  {...register('username')}
                  type="text"
                  id="username"
                  placeholder="Digite seu nome de usuário"
                  disabled={isLoading}
                  className={`form-input ${errors.username ? 'error' : ''}`}
                />
                {errors.username && (
                  <span className="error-message">{errors.username.message}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="password" className="form-label">
                  Senha
                </label>
                <input
                  {...register('password')}
                  type="password"
                  id="password"
                  placeholder="Digite sua senha"
                  disabled={isLoading}
                  className={`form-input ${errors.password ? 'error' : ''}`}
                />
                {errors.password && (
                  <span className="error-message">{errors.password.message}</span>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="login-button"
              >
                {isLoading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Entrando...
                  </>
                ) : (
                  'Entrar'
                )}
              </button>

              <div className="register-link">
                <p className="text-regular">
                  Não tem uma conta?{' '}
                  <Link to="/register" className="link">
                    Registre-se
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;