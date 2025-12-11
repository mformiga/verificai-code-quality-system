# Configurando URL Fixa no Vercel

## Opções disponíveis:

### 1️⃣ Domínio Personalizado (Melhor Opção)
**Vantagens:**
- URL permanente: `backend.seudominio.com`
- SSL incluído
- Aparência profissional

**Como configurar:**
1. Compre um domínio (Ex: Namecheap, GoDaddy, etc.)
2. No dashboard Vercel:
   - Dashboard → Selecione projeto backend → Settings → Domains
   - Adicione: `backend.seudominio.com`
3. Configure DNS:
   - Tipo: CNAME
   - Nome: `backend`
   - Valor: `cname.vercel-dns.com`

### 2️⃣ Subdomínio Vercel (.vercel.app)
**Vantagens:**
- Gratuito
- URL previsível
- Sem necessidade de domínio próprio

**Como configurar:**
1. No dashboard Vercel → Project Settings → Domains
2. Adicione: `verificai-backend.vercel.app`
3. O Vercel criará um alias permanente

### 3️⃣ Usar Branch Production
**URL:** `https://verificai-backend.vercel.app` (ao fazer deploy da branch main)

**Como configurar:**
1. Configure o projeto para usar a branch `main` como production
2. URLs de preview branches mudam, mas a production é fixa
3. Mova o projeto atual para production

### 4️⃣ Configuração via vercel.json
Adicione ao projeto do backend:

```json
{
  "version": 2,
  "alias": "verificai-backend",
  "name": "verificai-backend"
}
```

## Recomendação:
Use **Opção 2** (Subdomínio Vercel) por ser gratuita e prática:

1. Vá ao dashboard do backend no Vercel
2. Settings → Domains
3. Adicione: `verificai-backend.vercel.app`
4. Espere o DNS propagar (2-5 minutos)

## Após configurar:
Atualize o frontend para usar a URL fixa:

```javascript
// frontend/api/proxy.js
const backendUrl = 'https://verificai-backend.vercel.app';
```

OU

Configure a variável de ambiente no Vercel:
- `BACKEND_URL` = `https://verificai-backend.vercel.app`

## URLs Fixas Alternativas:
- `api-verificai.vercel.app`
- `verificai-api.vercel.app`
- `verificai-prod.vercel.app`

Escolha uma que esteja disponível!