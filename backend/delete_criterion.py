#!/usr/bin/env python3
"""
Script para deletar critérios manualmente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prompt import GeneralCriteria

def delete_criterion(criterion_id: int):
    """Deleta um critério pelo ID"""
    db = SessionLocal()
    try:
        criterion = db.query(GeneralCriteria).filter(GeneralCriteria.id == criterion_id).first()

        if criterion:
            print(f"Deletando critério ID {criterion_id}: '{criterion.text}'")
            db.delete(criterion)
            db.commit()
            print(f"✅ Critério ID {criterion_id} deletado com sucesso!")
        else:
            print(f"❌ Critério ID {criterion_id} não encontrado")

    except Exception as e:
        print(f"❌ Erro ao deletar critério: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def list_all_criteria():
    """Lista todos os critérios disponíveis"""
    db = SessionLocal()
    try:
        criteria = db.query(GeneralCriteria).all()
        print("\n=== CRITÉRIOS DISPONÍVEIS ===")
        for criterion in criteria:
            print(f"ID: {criterion.id} | critérios_{criterion.id} | {criterion.text[:50]}...")
        print(f"Total: {len(criteria)} critérios\n")
    finally:
        db.close()

if __name__ == "__main__":
    print("=== FERRAMENTA DE DELEÇÃO DE CRITÉRIOS ===\n")

    list_all_criteria()

    try:
        criterion_id = int(input("Digite o ID do critério para deletar: "))
        delete_criterion(criterion_id)

        print("\n=== ATUALIZADO ===")
        list_all_criteria()

    except ValueError:
        print("❌ ID inválido. Digite um número inteiro.")
    except KeyboardInterrupt:
        print("\nOperação cancelada.")