# AVALIA - Supabase Configuration Finalization Guide

## ✅ What's Done
- [x] Database schema created and executed successfully
- [x] Row Level Security (RLS) policies configured
- [x] Backend integration code prepared
- [x] Storage setup script created
- [x] Environment templates created

## 🔧 Next Steps to Complete Configuration

### 1. Configure Your Supabase Credentials

Execute o script para obter suas credenciais:
```bash
python get_supabase_info.py
```

Ou manualmente:
1. Abra https://app.supabase.com
2. Selecione seu projeto
3. Vá para **Project Settings → API**
4. Copie:
   - **Project URL**: `https://SEU_PROJECT_REF.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 2. Update Environment Files

#### Backend (.env.supabase):
```bash
# Supabase Configuration
SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=SUA_ANON_KEY_AQUI
SUPABASE_SERVICE_ROLE_KEY=SUA_SERVICE_ROLE_KEY_AQUI
SUPABASE_PROJECT_REF=SEU_PROJECT_REF
```

#### Frontend (frontend/.env.production):
```bash
# Supabase Configuration - Production
VITE_SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
VITE_SUPABASE_ANON_KEY=SUA_ANON_KEY_AQUI
```

### 3. Execute Storage Setup

No Supabase SQL Editor, execute:
```sql
-- Copie e cole o conteúdo de:
-- supabase_storage_setup.sql
```

Isso criará os buckets:
- `code-files` (para uploads de código)
- `analysis-reports` (para relatórios)
- `user-avatars` (para avatares de usuário)

### 4. Test Configuration

Execute o script de validação:
```bash
python validate_supabase_setup.py
```

### 5. Update Backend Configuration (if needed)

O backend já está configurado para usar Supabase através de:
- `backend/app/core/supabase.py`
- `backend/app/api/v1/supabase_auth.py`

### 6. Authentication Flow Setup

O sistema de autenticação usará:
- Supabase Auth para gerenciamento de usuários
- Row Level Security para controle de acesso
- JWT tokens para sessão

## 📁 Important Files Created

| File | Purpose |
|------|---------|
| `supabase_schema_fixed.sql` | Database schema with tables and RLS |
| `supabase_storage_setup.sql` | Storage buckets and policies |
| `backend/app/core/supabase.py` | Supabase integration utilities |
| `validate_supabase_setup.py` | Configuration validation script |
| `get_supabase_info.py` | Credential guide script |

## 🚀 Testing the Application

After configuration:

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements_supabase.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run build
   npm run preview
   ```

3. **Streamlit** (if using):
   ```bash
   streamlit run app.py
   ```

## 🔍 Verification Checklist

- [ ] Supabase URL and keys configured
- [ ] Database tables created (5 tables)
- [ ] Storage buckets created (3 buckets)
- [ ] RLS policies enabled
- [ ] Backend can connect to Supabase
- [ ] Frontend can authenticate users
- [ ] File upload functionality works

## 🛠️ Troubleshooting

### Connection Issues:
1. Verify URL format: `https://project-ref.supabase.co`
2. Check API keys are correct
3. Ensure project is active

### Permission Errors:
1. Verify RLS policies are enabled
2. Check user authentication
3. Validate bucket permissions

### Storage Issues:
1. Execute storage setup script
2. Check bucket policies
3. Verify file size limits

## 📚 Next Steps

1. Deploy to production
2. Configure custom domain
3. Set up monitoring
4. Add analytics
5. Configure backups

## 🆘 Support

If you encounter issues:
1. Check Supabase dashboard logs
2. Run validation script
3. Review this guide
4. Consult Supabase documentation

---

**Status**: Ready for configuration and testing! 🎉