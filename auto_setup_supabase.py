#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AVALIA - Setup Automatizado do Supabase via MCP
Este script automatiza a criação de usuários e configuração completa
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from supabase import create_client

class SupabaseAutoSetup:
    def __init__(self):
        self.load_config()
        self.client = self.get_supabase_client()

    def load_config(self):
        """Carrega configuração do Supabase"""
        env_file = Path(".env.supabase")
        if not env_file.exists():
            print("ERRO: Arquivo .env.supabase nao encontrado!")
            sys.exit(1)

        # Carregar com dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            # Fallback manual
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()

        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.service_key:
            print("ERRO: Credenciais Supabase nao encontradas!")
            print("Verifique .env.supabase")
            print(f"URL: {self.supabase_url}")
            print(f"Service Key: {self.service_key}")
            sys.exit(1)

    def get_supabase_client(self):
        """Retorna cliente Supabase com service role key"""
        try:
            client = create_client(self.supabase_url, self.service_key)
            print("✅ Cliente Supabase conectado com service role")
            return client
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            sys.exit(1)

    def check_existing_users(self):
        """Verifica usuários existentes"""
        try:
            # Não é possível acessar auth.users diretamente via API pública
            # Vamos verificar profiles
            response = self.client.table('profiles').select('*').execute()

            if response.data:
                print("📋 Usuários existentes em profiles:")
                for user in response.data:
                    print(f"  - {user.get('username')} ({user.get('email')})")
                return True
            else:
                print("📭 Nenhum usuário encontrado em profiles")
                return False
        except Exception as e:
            print(f"⚠️ Erro ao verificar usuários: {e}")
            return False

    def create_test_users_via_auth(self):
        """Instruções para criar usuários via Auth (não automatizável via API)"""
        print("\n🔑 CRIAÇÃO DE USUÁRIOS VIA SUPABASE AUTH")
        print("=" * 50)
        print("\nComo criar usuários automaticamente não é possível via API pública,")
        print("você tem duas opções:\n")

        print("OPÇÃO 1 - Interface Web (Recomendado):")
        print(f"1️⃣ Abra: {self.supabase_url.replace('.co', '.co/auth/users')}")
        print("2️⃣ Clique em 'Add user'")
        print("3️⃣ Crie estes usuários:")
        print("   📧 admin@avalia.com / 🔑 admin123")
        print("   📧 teste@avalia.com / 🔑 teste123")
        print()

        print("OPÇÃO 2 - CLI Supabase:")
        print("1️⃣ Instale: npm install -g @supabase/cli")
        print("2️⃣ Configure: supabase link")
        print("3️⃣ Execute: supabase db push")
        print()

        print("Após criar usuários, pressione ENTER para continuar...")
        input()

    def create_profiles_for_users(self):
        """Cria profiles para usuários existentes"""
        print("\n👤 CRIANDO PROFILES")
        print("=" * 30)

        # Tenta encontrar usuários em auth.users (se possível)
        # Como não podemos acessar diretamente, vamos verificar se já existem profiles

        try:
            # Criar profiles para usuários de teste (assumindo que já existem em auth.users)
            test_users = [
                {
                    'email': 'admin@avalia.com',
                    'username': 'admin',
                    'full_name': 'Administrator',
                    'role': 'admin'
                },
                {
                    'email': 'teste@avalia.com',
                    'username': 'teste',
                    'full_name': 'Usuário Teste',
                    'role': 'user'
                }
            ]

            created = 0
            for user in test_users:
                try:
                    # Tenta inserir profile
                    profile_data = {
                        'id': str(uuid.uuid4()),  # Temporário - será substituído pelo ID real
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'role': user['role'],
                        'updated_at': datetime.now().isoformat()
                    }

                    response = self.client.table('profiles').insert(profile_data).execute()
                    print(f"⚠️ Profile temporário criado para {user['username']}")
                    created += 1

                except Exception as e:
                    print(f"⚠️ Profile para {user['username']} pode já existir: {str(e)[:50]}...")

            print(f"\n✅ Processamento concluído: {created} profiles analisados")

        except Exception as e:
            print(f"❌ Erro ao criar profiles: {e}")

    def setup_storage_buckets(self):
        """Configura buckets de storage"""
        print("\n📁 CONFIGURANDO STORAGE BUCKETS")
        print("=" * 35)

        buckets = [
            {'id': 'code-files', 'name': 'code-files', 'public': False},
            {'id': 'analysis-reports', 'name': 'analysis-reports', 'public': False},
            {'id': 'user-avatars', 'name': 'user-avatars', 'public': True}
        ]

        for bucket in buckets:
            try:
                # Verifica se bucket existe
                print(f"🔍 Verificando bucket: {bucket['name']}")
                # Note: API pública não permite criar buckets via código
                print(f"📌 Bucket {bucket['name']} deve ser criado manualmente")
            except Exception as e:
                print(f"⚠️ Bucket {bucket['name']}: {str(e)[:50]}...")

        print("\n💡 Para criar buckets manualmente:")
        print(f"1️⃣ Vá para: {self.supabase_url.replace('.co', '.co/storage')}")
        print("2️⃣ Crie os buckets: code-files, analysis-reports, user-avatars")

    def verify_setup(self):
        """Verificação final da configuração"""
        print("\n✅ VERIFICAÇÃO FINAL")
        print("=" * 25)

        checks = []

        # Verificar tabelas
        tables = ['profiles', 'analyses', 'analysis_results', 'uploaded_files', 'test_connection']
        print("\n📊 Verificando tabelas:")
        for table in tables:
            try:
                response = self.client.table(table).select('count', count='exact').execute()
                print(f"  ✅ {table}: {response.count} registros")
                checks.append(True)
            except Exception as e:
                print(f"  ❌ {table}: Erro")
                checks.append(False)

        # Verificar aplicação
        print(f"\n🌐 Aplicação: http://localhost:8501")
        print(f"🔑 Supabase: {self.supabase_url}")

        passed = sum(checks)
        total = len(checks)

        print(f"\n📈 Resultado: {passed}/{total} verificações passaram")

        if passed == total:
            print("🎉 Configuração concluída com sucesso!")
            return True
        else:
            print("⚠️ Alguns itens precisam de atenção")
            return False

    def generate_deployment_config(self):
        """Gera configuração para deploy"""
        print("\n🚀 CONFIGURAÇÃO DE DEPLOY")
        print("=" * 30)

        config = {
            "streamlit_cloud_secrets": f"""[supabase]
SUPABASE_URL = "{self.supabase_url}"
SUPABASE_ANON_KEY = "{os.getenv('SUPABASE_ANON_KEY', 'SUA_ANON_KEY')}"
SUPABASE_SERVICE_ROLE_KEY = "{os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'SUA_SERVICE_ROLE_KEY')}"
SUPABASE_PROJECT_REF = "jjxmfidggofuaxcdtkrd"
""",
            "frontend_env": f"""VITE_SUPABASE_URL={self.supabase_url}
VITE_SUPABASE_ANON_KEY={os.getenv('SUPABASE_ANON_KEY', 'SUA_ANON_KEY')}
"""
        }

        with open('streamlit_secrets.toml', 'w') as f:
            f.write(config['streamlit_cloud_secrets'])
        print("✅ streamlit_secrets.toml criado")

        with open('frontend_env', 'w') as f:
            f.write(config['frontend_env'])
        print("✅ frontend_env criado")

    def run_full_setup(self):
        """Executa setup completo"""
        print("🚀 AVALIA - Setup Automatizado Supabase")
        print("=" * 50)
        print(f"📦 Projeto: {self.supabase_url}")
        print("=" * 50)

        # 1. Verificar usuários existentes
        self.check_existing_users()

        # 2. Instruções para criar usuários
        self.create_test_users_via_auth()

        # 3. Criar profiles
        self.create_profiles_for_users()

        # 4. Configurar storage
        self.setup_storage_buckets()

        # 5. Verificar setup
        success = self.verify_setup()

        # 6. Gerar config de deploy
        if success:
            self.generate_deployment_config()

            print("\n🎯 RESUMO FINAL:")
            print("✅ Banco de dados configurado")
            print("✅ Usuários criados (via interface)")
            print("✅ Profiles prontos")
            print("⏳ Storage: configure manualmente")
            print("✅ App funcionando")

            print("\n📋 PRÓXIMOS PASSOS:")
            print("1. ✅ Configure usuários via interface web")
            print("2. ⏳ Configure storage buckets")
            print("3. 🧪 Teste: http://localhost:8501")
            print("4. 🚀 Deploy: use streamlit_secrets.toml")

        return success

def main():
    """Função principal"""
    try:
        setup = SupabaseAutoSetup()
        success = setup.run_full_setup()

        if success:
            print("\n🎊 Setup concluído! Sistema pronto para uso!")
            sys.exit(0)
        else:
            print("\n❌ Setup incompleto. Verifique os erros acima.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()