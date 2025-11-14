from app.core.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

session = SessionLocal()
try:
    result = session.execute(text('SELECT id, username, email, full_name FROM users'))
    print('Usuários e seus usernames para login:')
    for row in result:
        print(f'ID: {row.id}, Username: {row.username}, Email: {row.email}, Nome: {row.full_name}')
finally:
    session.close()