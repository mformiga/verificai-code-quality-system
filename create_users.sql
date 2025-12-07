-- Criar usuários de teste diretamente no Supabase
-- NOTA: Este método pode não funcionar se o auth.users estiver protegido
-- Use a interface web em: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/auth/users

-- Verificar se usuários existem
SELECT id, email, created_at
FROM auth.users
WHERE email IN ('admin@avalia.com', 'teste@avalia.com');

-- Se não existirem, crie via interface web do Supabase