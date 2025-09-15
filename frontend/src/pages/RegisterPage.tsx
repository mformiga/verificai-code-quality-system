import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import { Card, CardHeader, CardContent } from '@/components/common/Card';
import { validatePassword } from '@/utils/helpers';

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
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-2xl">V</span>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Criar conta
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Junte-se ao VerificAI para analisar seu código com IA
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card>
          <CardHeader
            title="Criar nova conta"
            subtitle="Preencha os dados abaixo para se registrar"
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
                {...register('email')}
                label="Email"
                type="email"
                error={errors.email?.message}
                placeholder="Digite seu email"
                disabled={isLoading}
              />

              <Input
                {...register('password')}
                label="Senha"
                type="password"
                error={errors.password?.message}
                placeholder="Digite sua senha"
                disabled={isLoading}
                helperText="Mínimo 8 caracteres, incluindo maiúscula, minúscula, número e caractere especial"
              />

              <Input
                {...register('confirmPassword')}
                label="Confirmar senha"
                type="password"
                error={errors.confirmPassword?.message}
                placeholder="Confirme sua senha"
                disabled={isLoading}
              />

              <Button
                type="submit"
                loading={isLoading}
                disabled={isLoading}
                className="w-full"
              >
                Criar conta
              </Button>

              <div className="text-center">
                <span className="text-sm text-gray-600">
                  Já tem uma conta?{' '}
                  <Link
                    to="/login"
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    Faça login
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

export default RegisterPage;