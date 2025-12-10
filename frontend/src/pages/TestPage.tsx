/**
 * Test Page - Componente mínimo para diagnóstico
 */

import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <h1 style={{ color: '#1351b4', fontSize: '32px', marginBottom: '20px' }}>
        Página de Teste Funcionando!
      </h1>
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{ color: '#1351b4', marginBottom: '16px' }}>Teste de Renderização</h2>
        <p>Se você está vendo esta página, o React está funcionando corretamente.</p>
        <div style={{
          background: '#e3f2fd',
          padding: '16px',
          borderRadius: '4px',
          marginTop: '16px'
        }}>
          <strong>Status:</strong> ✅ Página renderizada com sucesso
        </div>
      </div>

      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: '#1351b4', marginBottom: '16px' }}>Formulário de Teste</h3>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Código de Teste:
          </label>
          <textarea
            placeholder="Cole seu código aqui..."
            style={{
              width: '100%',
              height: '150px',
              padding: '12px',
              border: '1px solid #ced4da',
              borderRadius: '4px',
              fontSize: '14px',
              fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace'
            }}
          />
        </div>
        <button
          style={{
            background: '#1351b4',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
          onClick={() => alert('Botão funcionando!')}
        >
          Testar Botão
        </button>
      </div>
    </div>
  );
};

export default TestPage;