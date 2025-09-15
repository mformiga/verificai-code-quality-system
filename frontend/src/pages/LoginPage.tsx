import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import { Card, CardHeader, CardContent } from '@/components/common/Card';

const loginSchema = z.object({
  username: z.string().min(1, 'Nome de usuário é obrigatório'),
  password: z.string().min(1, 'Senha é obrigatória'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();

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
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-2xl">V</span>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          VerificAI
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sistema de Qualidade de Código com IA
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card>
          <CardHeader
            title="Entrar na sua conta"
            subtitle="Digite suas credenciais para acessar o sistema"
          />
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <Input
                {...register('username')}
                label="Nome de usuário"
                type="text"
                error={errors.username?.message}
                placeholder="Digite seu nome de usuário"
                disabled={isLoading}
              />

              <Input
                {...register('password')}
                label="Senha"
                type="password"
                error={errors.password?.message}
                placeholder="Digite sua senha"
                disabled={isLoading}
              />

              <Button
                type="submit"
                loading={isLoading}
                disabled={isLoading}
                className="w-full"
              >
                Entrar
              </Button>

              <div className="text-center">
                <span className="text-sm text-gray-600">
                  Não tem uma conta?{' '}
                  <Link
                    to="/register"
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    Registre-se
                  </Link>
                </span>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;