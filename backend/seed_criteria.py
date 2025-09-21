#!/usr/bin/env python3
"""
Script para popular critérios padrão para análise de código
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.prompt import GeneralCriteria
from sqlalchemy.orm import Session

# Critérios padrão para análise de código
DEFAULT_CRITERIA = [
    "Código segue boas práticas e padrões de codificação",
    "Variáveis e funções têm nomes descritivos e significativos",
    "Código é legível e bem documentado",
    "Tratamento adequado de erros e exceções",
    "Uso eficiente de estruturas de dados e algoritmos",
    "Segurança implementada corretamente (prevenção de XSS, SQL Injection, etc.)",
    "Performance considerada e otimizada quando necessário",
    "Testes unitários cobrem as funcionalidades principais",
    "Arquitetura do código segue princípios SOLID",
    "Código é modular e fácil de manter"
]

def seed_criteria():
    """Popula critérios padrão para todos os usuários"""
    db = SessionLocal()

    try:
        # Buscar todos os usuários
        users = db.query(User).all()

        if not users:
            print("Nenhum usuário encontrado no banco de dados")
            return

        print(f"Encontrados {len(users)} usuários")

        total_criteria_added = 0

        for user in users:
            # Verificar se usuário já tem critérios
            existing_criteria = db.query(GeneralCriteria).filter(
                GeneralCriteria.user_id == user.id
            ).count()

            if existing_criteria > 0:
                print(f"Usuario {user.username} já tem {existing_criteria} critérios, pulando...")
                continue

            print(f"Adicionando critérios para usuário: {user.username}")

            # Adicionar critérios padrão
            for i, criteria_text in enumerate(DEFAULT_CRITERIA):
                criteria = GeneralCriteria(
                    user_id=user.id,
                    text=criteria_text,
                    is_active=True,
                    order=i
                )
                db.add(criteria)
                total_criteria_added += 1

            db.commit()
            print(f"{len(DEFAULT_CRITERIA)} critérios adicionados para {user.username}")

        print(f"\nTotal de {total_criteria_added} critérios adicionados com sucesso!")

    except Exception as e:
        print(f"Erro ao popular critérios: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando seed de critérios padrão...")
    seed_criteria()
    print("Seed de critérios concluído!")