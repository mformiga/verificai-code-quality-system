#!/usr/bin/env python3
"""
Script para resetar a senha do usuário admin
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_admin_password():
    """Resetar senha do usuário admin para 'admin'"""
    session = SessionLocal()

    try:
        # Encontrar usuário admin
        admin_user = session.query(User).filter(User.username == "admin").first()

        if not admin_user:
            print("Usuário admin não encontrado!")
            return

        # Resetar senha para 'admin'
        admin_user.hashed_password = get_password_hash("admin")
        session.commit()

        print("Senha do usuário admin resetada com sucesso!")
        print("Username: admin")
        print("Password: admin")

    except Exception as e:
        print(f"Erro ao resetar senha: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_admin_password()