import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import Base, engine
from app.models.user import User
from app.models.prompt import GeneralAnalysisResult
from sqlalchemy.orm import Session
from sqlalchemy import inspect

print("=== VERIFICAÇÃO DO BANCO DE DADOS ===")

# Verificar tabelas
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tabelas existentes: {tables}")

# Verificar se tabela de usuários existe
if 'users' in tables:
    columns = inspector.get_columns('users')
    print(f"\nColunas da tabela 'users':")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

# Verificar se tabela de análises existe
if 'general_analysis_results' in tables:
    columns = inspector.get_columns('general_analysis_results')
    print(f"\nColunas da tabela 'general_analysis_results':")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

# Verificar usuários existentes
with Session(engine) as session:
    try:
        users = session.query(User).all()
        print(f"\nUsuários existentes: {len(users)}")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Nome: {user.name}")
    except Exception as e:
        print(f"Erro ao consultar usuários: {e}")

    # Verificar análises existentes
    try:
        analyses = session.query(GeneralAnalysisResult).all()
        print(f"\nAnálises existentes: {len(analyses)}")
        for analysis in analyses:
            print(f"  - ID: {analysis.id}, Nome: {analysis.analysis_name}, User ID: {analysis.user_id}")
    except Exception as e:
        print(f"Erro ao consultar análises: {e}")

print("\n=== FIM DA VERIFICAÇÃO ===")