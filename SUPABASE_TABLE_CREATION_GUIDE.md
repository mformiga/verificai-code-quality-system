# Guia: Criar Tabela source_codes no Supabase

## Visão Geral
Este guia explica como criar a tabela `source_codes` no seu projeto Supabase (jjxmfidggofuaxcdtkrd) usando os arquivos fornecidos.

## Arquivos Criados

### 1. `create_source_codes_supabase.sql`
Este arquivo contém o SQL completo para criar a tabela com a estrutura exata solicitada:
- UUID como chave primária
- Referência à tabela `auth.users`
- Índices para performance
- Trigger para `updated_at`
- Row Level Security (RLS) configurado

### 2. `execute_create_table.py`
Script Python para executar o SQL no Supabase usando o cliente Python.

## Método 1: Usando o Supabase Dashboard (Recomendado)

1. **Acesse seu projeto Supabase:**
   - Vá para https://app.supabase.com
   - Selecione seu projeto: `jjxmfidggofuaxcdtkrd`

2. **Abra o SQL Editor:**
   - No menu lateral, clique em "SQL Editor"
   - Clique em "New query"

3. **Copie e cole o conteúdo do arquivo `create_source_codes_supabase.sql`:**
   ```sql
   -- Todo o conteúdo do arquivo SQL aqui
   ```

4. **Execute o SQL:**
   - Clique no botão "Run" ou pressione Ctrl+Enter
   - Aguarde a execução completa

5. **Verifique a criação:**
   - Vá para "Table Editor" no menu lateral
   - Procure pela tabela `source_codes`
   - Clique na tabela para ver sua estrutura

## Método 2: Usando o Script Python

### Pré-requisitos
```bash
pip install supabase python-dotenv
```

### Configurar Variáveis de Ambiente
Crie um arquivo `.env` ou configure as variáveis:
```bash
# .env file
SUPABASE_URL=https://jjxmfidggofuaxcdtkrd.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua_service_role_key
```

### Executar o Script
```bash
python execute_create_table.py
```

## Verificação Manual da Tabela

Após a criação, verifique se tudo está correto:

### 1. Estrutura da Tabela
No Supabase Dashboard → Table Editor → source_codes, verifique as colunas:
- ✓ id (UUID, Primary Key)
- ✓ code_id (VARCHAR(255), Unique)
- ✓ title (VARCHAR(255))
- ✓ description (TEXT)
- ✓ content (TEXT)
- ✓ file_name (VARCHAR(255))
- ✓ file_extension (VARCHAR(50))
- ✓ programming_language (VARCHAR(100))
- ✓ line_count (INTEGER)
- ✓ character_count (INTEGER)
- ✓ size_bytes (BIGINT)
- ✓ status (VARCHAR(50), Default: 'active')
- ✓ is_public (BOOLEAN, Default: false)
- ✓ is_processed (BOOLEAN, Default: false)
- ✓ processing_status (VARCHAR(50), Default: 'pending')
- ✓ user_id (UUID, Foreign Key para auth.users)
- ✓ created_at (TIMESTAMP WITH TIME ZONE)
- ✓ updated_at (TIMESTAMP WITH TIME ZONE)

### 2. Índices Criados
Verifique se os seguintes índices existem:
- ✓ idx_source_codes_code_id
- ✓ idx_source_codes_status
- ✓ idx_source_codes_user_id

### 3. Trigger Configurado
- ✓ update_source_codes_updated_at

### 4. Row Level Security (RLS)
Verifique as políticas:
- ✓ "Users can view own source codes"
- ✓ "Users can insert own source codes"
- ✓ "Users can update own source codes"
- ✓ "Users can delete own source codes"
- ✓ "Public source codes are viewable by everyone"

## Teste de Inserção

Para testar se a tabela está funcionando corretamente, você pode inserir um registro de teste:

```sql
INSERT INTO source_codes (
    code_id,
    title,
    description,
    content,
    file_name,
    file_extension,
    programming_language,
    line_count,
    character_count,
    size_bytes,
    user_id
) VALUES (
    'test_example',
    'Test Example',
    'A test source code entry',
    'function hello() {
    console.log("Hello, World!");
}',
    'hello.js',
    '.js',
    'JavaScript',
    3,
    50,
    50,
    NULL  -- or a real user_id from auth.users
);
```

## Solução de Problemas

### Erro: "permission denied for schema auth"
- Certifique-se de estar usando a SERVICE_ROLE_KEY, não a anon key
- A SERVICE_ROLE_KEY tem privilégios administrativos

### Erro: "relation "auth.users" does not exist"
- Isso pode acontecer se o esquema auth não estiver visível
- Verifique se você está conectado com permissões administrativas

### Erro: "function gen_random_uuid() does not exist"
- Execute `CREATE EXTENSION IF NOT EXISTS "pgcrypto";` antes de criar a tabela

## Próximos Passos

1. **Configure a autenticação** se ainda não estiver configurada
2. **Teste as políticas RLS** com usuários reais
3. **Configure as permissões granulares** se necessário
4. **Crie índices adicionais** baseado nos padrões de consulta da sua aplicação

## Contato

Se encontrar algum problema, verifique:
- Logs do Supabase (Dashboard → Logs)
- Permissões do usuário usado para conexão
- Configurações de RLS (Row Level Security)