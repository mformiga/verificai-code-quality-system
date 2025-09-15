import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          state: ['zustand'],
          query: ['@tanstack/react-query'],
          ui: ['tailwindcss'],
          utils: ['clsx', 'class-variance-authority', 'date-fns'],
          forms: ['react-hook-form', '@hookform/resolvers', 'zod'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: function (req, res, options) {
          if (req.url.startsWith('/api/auth')) {
            // Mock authentication APIs
            if (req.url === '/api/auth/register' && req.method === 'POST') {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                user: {
                  id: '1',
                  email: 'test@example.com',
                  name: 'Test User',
                },
                access_token: 'mock-jwt-token',
                token_type: 'bearer',
                expires_in: 3600,
                refresh_token: 'mock-refresh-token'
              }));
              return true;
            }

            if (req.url === '/api/auth/login' && req.method === 'POST') {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                user: {
                  id: '1',
                  email: 'test@example.com',
                  name: 'Test User',
                },
                access_token: 'mock-jwt-token',
                token_type: 'bearer',
                expires_in: 3600,
                refresh_token: 'mock-refresh-token'
              }));
              return true;
            }
          }

          if (req.url.startsWith('/api/prompts')) {
            // Mock prompts APIs
            if (req.url === '/api/prompts' && req.method === 'GET') {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                data: {
                  general: {
                    id: '1',
                    name: 'Critérios Gerais',
                    type: 'general',
                    description: 'Critérios gerais de análise de código',
                    content: '# Critérios Gerais de Análise de Código\n\n## Qualidade do Código\n- O código deve seguir boas práticas de programação\n- Deve ser legível e bem documentado\n- Deve seguir os padrões da linguagem\n\n## Segurança\n- Validar todas as entradas de usuário\n- Proteger contra injeção de SQL\n- Implementar autenticação e autorização adequadas',
                    isActive: true,
                    isDefault: true,
                    version: 1,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    createdBy: 'system'
                  },
                  architectural: {
                    id: '2',
                    name: 'Conformidade Arquitetural',
                    type: 'architectural',
                    description: 'Critérios de conformidade arquitetural',
                    content: '# Conformidade Arquitetural\n\n## Padrões Arquiteturais\n- Seguir os padrões de projeto definidos\n- Manter a separação de camadas\n- Utilizar os padrões de microserviços quando aplicável\n\n## Performance\n- Otimizar queries de banco de dados\n- Implementar cache quando necessário\n- Monitorar performance da aplicação',
                    isActive: true,
                    isDefault: true,
                    version: 1,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    createdBy: 'system'
                  },
                  business: {
                    id: '3',
                    name: 'Conformidade Negocial',
                    type: 'business',
                    description: 'Critérios de conformidade negocial',
                    content: '# Conformidade Negocial\n\n## Requisitos de Negócio\n- O código deve atender aos requisitos de negócio\n- Deve seguir as regras de domínio\n- Deve estar alinhado com os objetivos do projeto\n\n## Compliance\n- Seguir as regulamentações aplicáveis\n- Manter conformidade com LGPD\n- Implementar logging adequado para auditoria',
                    isActive: true,
                    isDefault: true,
                    version: 1,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    createdBy: 'system'
                  }
                },
                status: 200,
                message: 'Prompts retrieved successfully'
              }));
              return true;
            }

            if (req.url === '/api/prompts' && req.method === 'POST') {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                data: req.body,
                status: 200,
                message: 'Prompts saved successfully'
              }));
              return true;
            }
          }
        }
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        secure: false,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    reporters: ['verbose'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*'],
      exclude: ['src/main.tsx', 'src/App.tsx', 'src/**/*.test.{ts,tsx}'],
    },
  },
  define: {
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
});