from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

session = SessionLocal()
try:
    user = session.query(User).filter(User.username == 'admin').first()
    print(f'User found: {user is not None}')
    if user:
        print(f'Hashed password: {user.hashed_password[:50]}...')
        test_passwords = ['admin', '123456', 'password', 'admin123']
        for pwd in test_passwords:
            result = verify_password(pwd, user.hashed_password)
            print(f'Testing {pwd}: {result}')
finally:
    session.close()