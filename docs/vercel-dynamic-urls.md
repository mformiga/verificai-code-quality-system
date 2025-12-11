# Configuração de URLs dinâmicas do Vercel

## Problema
O Vercel gera URLs diferentes a cada deploy dos projetos. Isso causa problemas de CORS quando o frontend tenta se comunicar com o backend, pois a URL hardcoded no arquivo `proxy.js` fica desatualizada.

## Solução Implementada
Usamos variáveis de ambiente para manter a URL do backend atualizável sem modificar o código.

### Arquivos alterados:

1. **frontend/vercel.json**: Adicionada variável `BACKEND_URL`
2. **frontend/api/proxy.js**: Usa `process.env.BACKEND_URL` com fallback

## Como atualizar após cada deploy do backend:

### Opção 1: Através do Dashboard Vercel (Recomendado)
1. Acesse [vercel.com](https://vercel.com)
2. Vá para o projeto do frontend
3. Clique em "Settings" → "Environment Variables"
4. Atualize a variável `BACKEND_URL` com a nova URL do backend

### Opção 2: Através da CLI Vercel
```bash
vercel env add BACKEND_URL production
# Digite a nova URL do backend quando solicitado
```

### Opção 3: Atualizando o vercel.json (Menos recomendado)
Edite o arquivo `frontend/vercel.json` e atualize o valor de `BACKEND_URL` no campo `env`.

## Automatização Futura
Para automatizar completamente, você pode:
1. Usar domínios personalizados (fixos) em vez das URLs do Vercel
2. Implementar um webhook que atualiza a variável de ambiente automaticamente
3. Usar o Vercel PostHog para descoberta dinâmica de serviços

## Exemplo de workflow após deploy do backend:
1. Faça o deploy do backend
2. Copie a URL gerada (ex: `https://verificai-backend-abc123-mauricios-projects-b3859180.vercel.app`)
3. Atualize a variável `BACKEND_URL` no projeto frontend
4. Faça um novo deploy do frontend (opcional, se atualizado via dashboard)