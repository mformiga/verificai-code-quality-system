#!/usr/bin/env python3
"""
Script para testar dados de login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

def test_logins():
    db = SessionLocal()

    try:
        users = db.query(User).all()

        print("DADOS DE LOGIN DISPONÍVEIS:")
        print("=" * 50)

        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Full Name: {user.full_name}")

            # Testar algumas senhas comuns
            test_passwords = ['123456', 'admin', 'superadmin', 'test', 'password']

            for pwd in test_passwords:
                try:
                    if verify_password(pwd, user.hashed_password):
                        print(f"SENHA: {pwd}")
                        break
                except Exception as e:
                    continue
            else:
                print("SENHA: (nao testada - bcrypt error)")

            print("-" * 50)

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_logins()