# 11. Security Requirements

### 11.1 Authentication and Authorization

#### 11.1.1 JWT Implementation

```python
# backend/app/core/security/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

#### 11.1.2 Authorization Middleware

```python
# backend/app/middleware/auth.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..core.security.jwt import verify_token
from ..repositories.user_repository import UserRepository
from ..database.connection import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Role-based access control decorator"""
    def role_checker(current_user = Depends(get_current_active_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
```

### 11.2 Input Validation and Sanitization

#### 11.2.1 File Upload Security

```python
# backend/app/core/security/file_security.py
import os
import magic
from typing import List, Set
from pathlib import Path

class FileSecurity:
    ALLOWED_MIME_TYPES: Set[str] = {
        'text/plain',
        'text/x-python',
        'text/x-java-source',
        'text/javascript',
        'application/javascript',
        'text/typescript',
        'application/x-typescript',
        'text/x-csrc',
        'text/x-c++src',
        'application/json',
        'text/markdown',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    DANGEROUS_EXTENSIONS: Set[str] = {
        '.exe', '.bat', '.cmd', '.sh', '.php', '.asp', '.aspx', '.jsp'
    }

    @classmethod
    def validate_file(cls, file_path: str) -> List[str]:
        """Validate uploaded file for security"""
        errors = []

        # Check file size
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > cls.MAX_FILE_SIZE:
                errors.append(f"File size exceeds maximum limit of {cls.MAX_FILE_SIZE} bytes")

        # Check file extension
        path = Path(file_path)
        if path.suffix.lower() in cls.DANGEROUS_EXTENSIONS:
            errors.append(f"Dangerous file extension: {path.suffix}")

        # Check MIME type
        try:
            mime_type = magic.from_file(file_path, mime=True)
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                errors.append(f"Unsupported file type: {mime_type}")
        except Exception as e:
            errors.append(f"Could not determine file type: {str(e)}")

        # Check for potential malicious content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if cls._contains_malicious_content(content):
                    errors.append("File contains potentially malicious content")
        except Exception:
            # If we can't read as text, it might be binary - already handled by MIME type
            pass

        return errors

    @classmethod
    def _contains_malicious_content(cls, content: str) -> bool:
        """Check for potentially malicious content patterns"""
        malicious_patterns = [
            'eval(',
            'exec(',
            'system(',
            'subprocess.',
            'os.system',
            '__import__',
            'base64.decode',
            'pickle.loads',
            'marshal.loads'
        ]

        content_lower = content.lower()
        for pattern in malicious_patterns:
            if pattern in content_lower:
                return True

        return False

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove potentially dangerous characters
        dangerous_chars = ['..', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit filename length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext

        return filename
```

#### 11.2.2 XSS Prevention

```python
# backend/app/core/security/xss_prevention.py
import re
import html
from typing import Optional
import bleach

class XSSPrevention:
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'code', 'pre', 'blockquote',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img', 'div', 'span'
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class']
    }

    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        return bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitize plain text content"""
        # HTML escape
        sanitized = html.escape(text)

        # Remove potentially dangerous Unicode characters
        sanitized = cls._remove_dangerous_unicode(sanitized)

        # Remove control characters except basic whitespace
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)

        return sanitized

    @classmethod
    def _remove_dangerous_unicode(cls, text: str) -> str:
        """Remove potentially dangerous Unicode characters"""
        dangerous_ranges = [
            (0x2028, 0x2029),  # Line separator and paragraph separator
            (0x200B, 0x200D),  # Zero-width characters
            (0x2060, 0x206F),  # Invisible characters
        ]

        result = []
        for char in text:
            code_point = ord(char)
            dangerous = False

            for start, end in dangerous_ranges:
                if start <= code_point <= end:
                    dangerous = True
                    break

            if not dangerous:
                result.append(char)

        return ''.join(result)
```

### 11.3 Security Headers

```python
# backend/app/middleware/security_headers.py
from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                # Add security headers
                headers[b"content-security-policy"] = b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; frame-ancestors 'none';"
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                headers[b"permissions-policy"] = b"camera=(), microphone=(), geolocation=()"

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)

def create_cors_middleware():
    """Create CORS middleware configuration"""
    return CORSMiddleware(
        allow_origins=[
            "http://localhost:3000",
            "https://localhost:3000",
            "https://verificai.example.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-CSRF-Token"
        ],
        max_age=600
    )
```

---
