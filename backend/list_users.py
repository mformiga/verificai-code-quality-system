from app.core.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

session = SessionLocal()
try:
    result = session.execute(text('SELECT id, email, full_name, is_active, created_at FROM users'))
    print('Usuários no banco:')
    for row in result:
        print(f'ID: {row.id}, Email: {row.email}, Nome: {row.full_name}, Ativo: {row.is_active}, Criado: {row.created_at}')
finally:
    session.close()