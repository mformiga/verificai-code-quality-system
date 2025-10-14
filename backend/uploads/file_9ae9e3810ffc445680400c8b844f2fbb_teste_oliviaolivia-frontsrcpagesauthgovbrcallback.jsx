import { useRouter } from 'next/router';
import { useEffect, useRef } from 'react';
import { useAuth } from '../../../context/AuthContext';

export default function GovBrCallback() {
  const router = useRouter();
  const { handleGovBrCallback } = useAuth();
  const ranRef = useRef(false);

  useEffect(() => {
    if (!router.isReady || ranRef.current) return;

    const params = new URLSearchParams(window.location.search);
    const error = params.get('error');
    const error_description = params.get('error_description');
    const code = params.get('code');
    const state = params.get('state');

    if (error) {
      console.error('GovBR error:', error, error_description);
      return;
    }

    if (code && state) {
      ranRef.current = true;
      handleGovBrCallback(code, state);
    } else {
      console.error('Faltando code/state no callback', router.query);
    }
  }, [router.isReady]);

  return <p>Conectando ao Gov.br…</p>;
}
