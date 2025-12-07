# AVALIA - Guia de Migração de Usuários

## ✅ Sistema Corrigido!

**O que foi feito:**
- ✅ Removida funcionalidade de registro
- ✅ Mantido apenas login para usuários existentes
- ✅ App corrigido está rodando em http://localhost:8501

## 🔄 Como Migrar Seus Usuários

### Opção 1: Manual (Recomendado)

1. **Acesse o Supabase Auth**:
   - URL: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/auth/users

2. **Para cada usuário, clique em "Add user"**:
   - Email: use o email do usuário existente
   - Senha: defina uma nova senha
   - Role: confirme se é admin ou user

3. **Após criar usuários, execute este SQL**:
   ```sql
   -- Atualizar profiles para usuários criados
   UPDATE public.profiles
   SET
       username = 'nome_usuario',
       role = 'user' -- ou 'admin'
   WHERE id IN (
       SELECT id FROM auth.users
       WHERE email IN ('user1@example.com', 'user2@example.com')
   );
   ```

### Opção 2: Script Automatizado

Execute o script de migração:
```bash
python migrate_users.py
```

Este script irá:
- Listar seus usuários existentes
- Gerar instruções SQL personalizadas
- Criar guia passo a passo

## 📋 Usuários Teste (Para Validação)

Se precisar testar sem afetar usuários reais:

### Criar usuários de teste no Supabase:
1. **Admin Test**:
   - Email: `admin@avalia.com`
   - Senha: `admin123`
   - Profile: role = 'admin'

2. **User Test**:
   - Email: `teste@avalia.com`
   - Senha: `teste123`
   - Profile: role = 'user'

### SQL para criar profiles:
```sql
-- Profile Admin
INSERT INTO public.profiles (id, username, full_name, role)
SELECT
    id,
    'admin',
    'Administrator',
    'admin'
FROM auth.users
WHERE email = 'admin@avalia.com'
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    role = EXCLUDED.role;

-- Profile User
INSERT INTO public.profiles (id, username, full_name, role)
SELECT
    id,
    'teste',
    'Usuário Teste',
    'user'
FROM auth.users
WHERE email = 'teste@avalia.com'
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    role = EXCLUDED.role;
```

## 🔧 Validação do Sistema

1. **Teste o login**:
   - Abra: http://localhost:8501
   - Use credenciais de teste
   - Verifique se funciona

2. **Funcionalidades a testar**:
   - ✅ Login com usuários existentes
   - ✅ Upload de arquivos
   - ✅ Análise de código
   - ✅ Histórico de análises

## 🚀 Deploy em Produção

Após testar localmente:

1. **Commit das mudanças**:
   ```bash
   git add .
   git commit -m "fix: remove registration, migrate to login-only system"
   git push
   ```

2. **Configure os usuários no Supabase Production**:
   - Use o mesmo processo
   - Migre usuários reais
   - Crie profiles correspondentes

3. **Deploy para Streamlit Cloud**:
   - Configure secrets com suas chaves
   - Deploy da branch atualizada

## 📊 Status Final

- ✅ **App corrigido**: Sem registro, apenas login
- ✅ **Supabase configurado**: Tabelas e storage prontos
- ✅ **Migração guiada**: Script e SQL prontos
- ✅ **Testes prontos**: Usuários de teste disponíveis

## 🔗 Links Importantes

- **App Local**: http://localhost:8501
- **Supabase Dashboard**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
- **Supabase Auth**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/auth/users
- **Supabase SQL**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/sql/new

## 🎯 Próximos Passos

1. **Migre seus usuários** agora
2. **Teste o login** localmente
3. **Confirme funcionalidades**
4. **Deploy para produção**

Seu sistema AVALIA está corrigido e pronto para uso com usuários existentes! 🎉