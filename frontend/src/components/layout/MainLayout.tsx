import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from '@/components/common/Layout/Header';
import Sidebar from '@/components/common/Layout/Sidebar';
import Footer from '@/components/common/Layout/Footer';

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Configuração de Prompts', href: '/prompts', icon: '⚙️' },
    { name: 'Upload de Código', href: '/upload', icon: '📁' },
    { name: 'Análise Geral', href: '/analysis/general', icon: '📊' },
    { name: 'Análise Arquitetural', href: '/analysis/architectural', icon: '🏗️' },
    { name: 'Análise de Negócio', href: '/analysis/business', icon: '💼' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        navigation={navigation}
        currentPath={location.pathname}
      />

      {/* Main content */}
      <div className="lg:pl-64 flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 py-6">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default MainLayout;