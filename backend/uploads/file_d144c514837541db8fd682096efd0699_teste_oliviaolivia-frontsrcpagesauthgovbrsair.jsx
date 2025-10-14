import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function GovbrSair() {
  const router = useRouter();

  useEffect(() => {
    try {
      sessionStorage.clear();
      localStorage.removeItem('user');
      router.push('/');
    } catch {}
  }, []);

  return <p>Você saiu do sistema.</p>;
}
