# AVALIA - Solução de Erros Supabase

## ❌ Erros Comuns e Soluções

### 1. Erro: `policy already exists`
```
ERROR: 42710: policy "Users can view own profile." for table "profiles" already exists
```

**Solução:** As políticas já foram criadas quando executou o schema pela primeira vez.

**O que fazer:**
- ✅ **Ignore este erro** - significa que as políticas já existem
- ✅ Continue com os próximos passos

---

### 2. Erro: `permission denied for schema storage`
```
ERROR: 42501: permission denied for schema storage
```

**Solução:** Buckets de storage não podem ser criados via SQL no Supabase.

**O que fazer:**
- 🔄 **Crie buckets manualmente** no dashboard
- 📍 Vá para: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/storage

---

## 🔧 Como Criar Buckets de Storage

### Passo 1: Acessar Storage
1. Vá para: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
2. No menu lateral, clique em **Storage**

### Passo 2: Criar Buckets
Crie 3 buckets manualmente:

#### Bucket 1: code-files
- **Nome**: `code-files`
- **Público**: ❌ Não (privado)
- **Tamanho**: 50MB
- **Tipos de arquivo**: `.py, .js, .ts, .java, .cpp, .c, .php, .rb, .go`

#### Bucket 2: analysis-reports
- **Nome**: `analysis-reports`
- **Público**: ❌ Não (privado)
- **Tamanho**: 10MB
- **Tipos de arquivo**: `.json, .txt, .pdf, .html, .md`

#### Bucket 3: user-avatars
- **Nome**: `user-avatars`
- **Público**: ✅ Sim (para imagens de perfil)
- **Tamanho**: 5MB
- **Tipos de arquivo**: `.jpg, .png, .gif, .webp, .svg`

---

## ✅ Verificar Configuração Atual

### Execute estes comandos SQL para verificar:
```sql
-- Verificar tabelas
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verificar políticas
SELECT schemaname, tablename, policyname FROM pg_policies
WHERE schemaname = 'public';

-- Testar conexão
SELECT COUNT(*) FROM test_connection;
```

---

## 🚀 Continuar com Deploy

Se você já executou `supabase_schema_fixed.sql` e viu os erros acima:

1. ✅ **Schema já está criado** (os erros de policy já existem significam isso)
2. 🔄 **Crie buckets de storage manualmente** (instruções acima)
3. ✅ **Continue para o próximo passo**

### Próximos Passos:
1. **Configure suas credenciais** em `.env.supabase`
2. **Crie buckets manualmente** no dashboard
3. **Teste a aplicação**:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## 🔍 Links Úteis

- **Dashboard**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
- **Storage**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/storage
- **SQL Editor**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/sql
- **Settings**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings

---

## ✅ Resumo

- ❌ Não execute `supabase_storage_setup.sql` via SQL
- ✅ Schema já está criado (ignore erros de policy)
- 🔄 Crie buckets manualmente no dashboard Storage
- 🚀 Continue com configuração de credenciais e teste

**Status**: Seu banco está pronto, só precisa dos buckets de storage! 🎉