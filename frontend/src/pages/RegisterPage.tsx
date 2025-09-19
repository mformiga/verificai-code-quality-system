import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { validatePassword } from '@/utils/helpers';
import './RegisterPage.css';

const registerSchema = z.object({
  username: z.string().min(3, 'Nome de usuário deve ter pelo menos 3 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Senhas não conferem",
  path: ["confirmPassword"],
}).refine((data) => {
  const validation = validatePassword(data.password);
  return validation.isValid;
}, {
  message: "A senha não atende aos requisitos de segurança",
  path: ["password"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

const RegisterPage: React.FC = () => {
  const { register: registerUser, isLoading } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerUser({
        username: data.username,
        email: data.email,
        password: data.password,
      });
    } catch (error) {
      // Erro já é tratado no hook useAuth
    }
  };

  return (
    <div className="register-page">
      {/* Logo and Page Title */}
      <div className="logo-container">
        <div className="logo">
          <span className="logo-text">V</span>
        </div>
        <h1 className="page-title">Criar conta</h1>
        <p className="page-subtitle">Junte-se ao VerificAI para analisar seu código com IA</p>
      </div>

      {/* Register Form */}
      <div className="register-form-container">
        <div className="br-card">
          <div className="card-header text-center">
            <h2 className="text-h2">Criar nova conta</h2>
            <p className="text-regular">
              Preencha os dados abaixo para se registrar
            </p>
          </div>
          <div className="card-content">
            <form onSubmit={handleSubmit(onSubmit)} className="register-form">
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
                <label htmlFor="email" className="form-label">
                  Email
                </label>
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  placeholder="Digite seu email"
                  disabled={isLoading}
                  className={`form-input ${errors.email ? 'error' : ''}`}
                />
                {errors.email && (
                  <span className="error-message">{errors.email.message}</span>
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
                <div className="password-requirements">
                  <h4>Requisitos da senha:</h4>
                  <ul>
                    <li className={password && password.length >= 8 ? 'valid' : 'invalid'}>
                      Mínimo 8 caracteres
                    </li>
                    <li className={password && /[a-z]/.test(password) ? 'valid' : 'invalid'}>
                      Pelo menos uma letra minúscula
                    </li>
                    <li className={password && /[A-Z]/.test(password) ? 'valid' : 'invalid'}>
                      Pelo menos uma letra maiúscula
                    </li>
                    <li className={password && /\d/.test(password) ? 'valid' : 'invalid'}>
                      Pelo menos um número
                    </li>
                    <li className={password && /[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'valid' : 'invalid'}>
                      Pelo menos um caractere especial
                    </li>
                  </ul>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirmar senha
                </label>
                <input
                  {...register('confirmPassword')}
                  type="password"
                  id="confirmPassword"
                  placeholder="Confirme sua senha"
                  disabled={isLoading}
                  className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                />
                {errors.confirmPassword && (
                  <span className="error-message">{errors.confirmPassword.message}</span>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="register-button"
              >
                {isLoading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Criando conta...
                  </>
                ) : (
                  'Criar conta'
                )}
              </button>

              <div className="login-link">
                <p className="text-regular">
                  Já tem uma conta?{' '}
                  <Link to="/login" className="link">
                    Faça login
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

export default RegisterPage;