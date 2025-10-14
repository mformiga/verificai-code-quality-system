import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { BRHeader } from './DSGOV/BRHeader';

const AppHeader = ({ title }) => {
  const { logout } = useAuth();
  const router = useRouter();

  const [userName, setUserName] = useState('');

  useEffect(() => {
    try {
      if (typeof window === 'undefined') return;
      const stored = localStorage.getItem('user');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && typeof parsed.name === 'string') {
          setUserName(parsed.name);
        }
      }
    } catch (_) {}
  }, []);

  const quickLinks = [
    { label: 'Novo Processo', href: '/arquivos' },
    { label: 'Histórico de Processamento', href: '/historico' }
    // { label: 'Editor', href: '/PromptsEditor' }
  ];

  const systemFunctions = [
    {
      label: 'Logout',
      onClick: logout,
      icon: <i className='fas fa-sign-out-alt' aria-hidden />
    }
  ];

  return (
    <BRHeader
      logoSrc={'/assets/OlivIA-SVG.svg'}
      title={userName || title || ''}
      quickLinks={quickLinks}
      systemFunctions={systemFunctions}
      onMenu={() => router.push('/home')}
    />
  );
};

export default AppHeader;
