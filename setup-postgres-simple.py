#!/usr/bin/env python3
"""
Script para configurar e inicializar o PostgreSQL para o VerificAI (versão sem emojis)
"""
import os
import sys
import subprocess
import time
import psycopg2
from pathlib import Path

def check_postgres_running():
    """Verificar se PostgreSQL está rodando na porta 5432"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='verificai',
            password='verificai123',
            database='verificai'
        )
        conn.close()
        return True
    except:
        return False

def start_docker_postgres():
    """Iniciar PostgreSQL usando Docker"""
    print("Iniciando PostgreSQL com Docker...")

    # Verificar se Docker está rodando
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
    except:
        print("ERRO: Docker não está instalado ou não está no PATH")
        return False

    # Parar container existente se houver
    subprocess.run(['docker', 'stop', 'verificai-postgres'], capture_output=True)
    subprocess.run(['docker', 'rm', 'verificai-postgres'], capture_output=True)

    # Iniciar novo container
    cmd = [
        'docker', 'run', '-d',
        '--name', 'verificai-postgres',
        '-e', 'POSTGRES_DB=verificai',
        '-e', 'POSTGRES_USER=verificai',
        '-e', 'POSTGRES_PASSWORD=verificai123',
        '-p', '5432:5432',
        '-v', 'verificai-postgres-data:/var/lib/postgresql/data',
        'postgres:15-alpine'
    ]

    try:
        subprocess.run(cmd, check=True)
        print("PostgreSQL iniciado com sucesso!")
        print("Aguardando 10 segundos para o banco de dados inicializar...")
        time.sleep(10)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao iniciar PostgreSQL: {e}")
        return False

def create_database_if_not_exists():
    """Criar banco de dados se não existir"""
    try:
        # Conectar ao PostgreSQL padrão
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='verificai',
            password='verificai123',
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar se banco de dados existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'verificai'")
        exists = cursor.fetchone()

        if not exists:
            print("Criando banco de dados 'verificai'...")
            cursor.execute("CREATE DATABASE verificai")
            print("Banco de dados criado com sucesso!")
        else:
            print("Banco de dados 'verificai' já existe")

        conn.close()
        return True
    except Exception as e:
        print(f"ERRO ao criar banco de dados: {e}")
        return False

def setup_environment():
    """Configurar variáveis de ambiente"""
    print("Configurando variáveis de ambiente...")

    # Garantir que o .env exista com as configurações corretas
    env_content = """# Environment Variables for VerificAI
# PostgreSQL Configuration
DATABASE_URL=postgresql://verificai:verificai123@localhost:5432/verificai
REDIS_URL=redis://localhost:6379

# Application Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ENVIRONMENT=development
DEBUG=true

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Pool Settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Logging
LOG_LEVEL=INFO
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("Arquivo .env configurado com PostgreSQL")

def verify_backend_config():
    """Verificar e atualizar configuração do backend"""
    print("Verificando configuração do backend...")

    # Verificar se o arquivo de configuração do backend tem o validador
    config_file = Path('backend/app/core/config.py')
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()

        if 'validate_database_url' not in content:
            print("ATENÇÃO: Configuração do backend não tem validador PostgreSQL")
        else:
            print("Configuração do backend está correta")
    else:
        print("AVISO: Arquivo de configuração do backend não encontrado")

def main():
    """Função principal"""
    print("=== Configuração do PostgreSQL para VerificAI ===")
    print()

    # 1. Verificar se PostgreSQL está rodando
    if not check_postgres_running():
        print("PostgreSQL não está rodando. Tentando iniciar...")

        # 2. Tentar iniciar com Docker
        if not start_docker_postgres():
            print("ERRO: Não foi possível iniciar o PostgreSQL")
            print("Por favor, inicie o PostgreSQL manualmente na porta 5432")
            return False

        # 3. Verificar novamente
        if not check_postgres_running():
            print("ERRO: PostgreSQL ainda não está acessível após inicialização")
            return False

    print("PostgreSQL está rodando e acessível!")

    # 4. Criar banco de dados se necessário
    if not create_database_if_not_exists():
        print("ERRO: Não foi possível configurar o banco de dados")
        return False

    # 5. Configurar ambiente
    setup_environment()

    # 6. Verificar configuração do backend
    verify_backend_config()

    print()
    print("[OK] Configuração concluída com sucesso!")
    print()
    print("Próximos passos:")
    print("1. Execute 'npm run dev' para iniciar a aplicação")
    print("2. Use as credenciais: admin/admin")
    print("3. Acesse: http://localhost:3011")
    print()
    print("O sistema agora usará PostgreSQL permanentemente!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)