#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User

def check_users():
    """Verifica todos os usuários no banco de dados"""
    db = SessionLocal()

    try:
        users = db.query(User).all()

        print(f"Total de usuários: {len(users)}")
        print()

        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Role: {user.role}")
            print(f"Is Active: {user.is_active}")
            print(f"Created At: {user.created_at}")
            print(f"Last Login: {user.last_login}")
            print("-" * 50)

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()