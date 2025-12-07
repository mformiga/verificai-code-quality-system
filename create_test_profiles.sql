-- Criar profiles para usuários de teste
-- Execute isso no Supabase SQL Editor

-- Profile para Admin
INSERT INTO public.profiles (id, username, full_name, role, updated_at)
SELECT
    id,
    'admin',
    'Administrator',
    'admin',
    NOW()
FROM auth.users
WHERE email = 'admin@avalia.com'
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role,
    updated_at = EXCLUDED.updated_at;

-- Profile para User Teste
INSERT INTO public.profiles (id, username, full_name, role, updated_at)
SELECT
    id,
    'teste',
    'Usuário Teste',
    'user',
    NOW()
FROM auth.users
WHERE email = 'teste@avalia.com'
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role,
    updated_at = EXCLUDED.updated_at;