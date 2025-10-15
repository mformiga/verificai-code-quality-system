import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/common/Button';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/common/Card';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  const quickActions = [
    {
      title: 'Configurar Prompt',
      description: 'Crie e gerencie prompts para análise de código',
      icon: '🤖',
      link: '/prompts',
      color: 'bg-blue-50 text-blue-600',
    },
    {
      title: 'Upload de Código',
      description: 'Envie seus arquivos de código para análise',
      icon: '📁',
      link: '/upload',
      color: 'bg-green-50 text-green-600',
    },
    {
      title: 'Análise Geral',
      description: 'Análise completa de qualidade e métricas',
      icon: '📊',
      link: '/analysis/general',
      color: 'bg-purple-50 text-purple-600',
    },
    {
      title: 'Análise Arquitetural',
      description: 'Análise de padrões e arquitetura',
      icon: '🏗️',
      link: '/analysis/architectural',
      color: 'bg-orange-50 text-orange-600',
    },
    {
      title: 'Análise de Negócio',
      description: 'Análise de regras de negócio e casos de uso',
      icon: '💼',
      link: '/analysis/business',
      color: 'bg-pink-50 text-pink-600',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Bem-vindo, {user?.username}!</h1>
            <p className="text-gray-600 mt-2">
              Sistema de Qualidade de Código com IA - Dashboard
            </p>
          </div>
          <Button variant="outline" onClick={logout}>
            Sair
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm">📊</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-blue-600">Análises Realizadas</p>
                  <p className="text-2xl font-semibold text-blue-900">0</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-green-50 border-green-200">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-green-600">Prompts Ativos</p>
                  <p className="text-2xl font-semibold text-green-900">0</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm">📁</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-purple-600">Arquivos Analisados</p>
                  <p className="text-2xl font-semibold text-purple-900">0</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-orange-50 border-orange-200">
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm">⭐</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-orange-600">Qualidade Média</p>
                  <p className="text-2xl font-semibold text-orange-900">--</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Ações Rápidas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-start">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${action.color}`}>
                      <span className="text-xl">{action.icon}</span>
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{action.title}</h3>
                      <p className="text-gray-600 text-sm mt-1">{action.description}</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Link to={action.link} className="w-full">
                    <Button variant="outline" className="w-full">
                      Acessar
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>

        {/* Getting Started */}
        <Card className="mt-8">
          <CardHeader
            title="Primeiros Passos"
            subtitle="Siga este guia para começar a usar o AVALIA"
          />
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    1
                  </div>
                </div>
                <div className="ml-4">
                  <h4 className="text-sm font-semibold text-gray-900">Configure um Prompt</h4>
                  <p className="text-sm text-gray-600">Crie prompts personalizados para análise de código específica</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    2
                  </div>
                </div>
                <div className="ml-4">
                  <h4 className="text-sm font-semibold text-gray-900">Faça Upload do Código</h4>
                  <p className="text-sm text-gray-600">Envie seus arquivos de código para análise</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    3
                  </div>
                </div>
                <div className="ml-4">
                  <h4 className="text-sm font-semibold text-gray-900">Analise os Resultados</h4>
                  <p className="text-sm text-gray-600">Revise as análises geradas pela IA e melhore seu código</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;