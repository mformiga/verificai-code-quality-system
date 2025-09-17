"""
Security utilities and password management for VerificAI Backend
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import hashlib
import secrets
import re
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password context for hashing and verification
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return subject"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, "Password meets strength requirements"


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(input_string: str) -> str:
    """Basic input sanitization"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    return sanitized.strip()


class PasswordValidator:
    """Password validation and management"""

    @staticmethod
    def is_common_password(password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = {
            'password', '123456', '12345678', '123456789', '12345',
            'qwerty', 'abc123', 'password1', 'admin', 'welcome'
        }
        return password.lower() in common_passwords

    @staticmethod
    def check_password_reuse(
        password: str,
        previous_passwords: list[str]
    ) -> bool:
        """Check if password has been used before"""
        for prev_password in previous_passwords:
            if verify_password(password, prev_password):
                return True
        return False


class APIKeyManager:
    """API key generation and management"""

    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """Generate API key and its hash"""
        api_key = generate_secure_token(64)
        api_key_hash = hash_api_key(api_key)
        return api_key, api_key_hash

    @staticmethod
    def verify_api_key(api_key: str, stored_hash: str) -> bool:
        """Verify API key against stored hash"""
        return hash_api_key(api_key) == stored_hash


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # This would need database access to get user by ID
    # For now, we'll return a placeholder
    from app.core.database import get_db
    from app.models.user import User

    db = next(get_db())
    user = db.query(User).filter(User.username == user_id).first()
    if user is None:
        raise credentials_exception

    return user


class SecurityHeaders:
    """Security headers configuration"""

    @staticmethod
    def get_security_headers() -> dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }