# 7. Database Schema Implementation

### 7.1 SQLAlchemy Models

```python
# backend/app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

# backend/app/models/session.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel

class AnalysisSession(BaseModel):
    __tablename__ = "analysis_sessions"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_name = Column(String(255), nullable=False)
    status = Column(String(50), default="created")
    completed_at = Column(DateTime, nullable=True)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="sessions")
    files = relationship("FileUpload", back_populates="session", cascade="all, delete-orphan")
    results = relationship("AnalysisResult", back_populates="session", cascade="all, delete-orphan")
    tasks = relationship("AnalysisTask", back_populates="session", cascade="all, delete-orphan")

# backend/app/models/configuration.py
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Configuration(BaseModel):
    __tablename__ = "configurations"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    config_type = Column(String(50), nullable=False)
    prompt_content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    version = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="configurations")
    results = relationship("AnalysisResult", back_populates="configuration")

# backend/app/models/upload.py
from sqlalchemy import Column, String, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class FileUpload(BaseModel):
    __tablename__ = "file_uploads"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100), nullable=False)
    upload_status = Column(String(50), default="uploaded")

    # Relationships
    session = relationship("AnalysisSession", back_populates="files")

# backend/app/models/analysis.py
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from .base import BaseModel

class AnalysisResult(BaseModel):
    __tablename__ = "analysis_results"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    configuration_id = Column(String, ForeignKey("configurations.id"), nullable=True)
    analysis_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=True)
    result_content = Column(Text, nullable=False)
    score = Column(Numeric(5, 2), nullable=True)
    status = Column(String(50), default="pending")

    # Relationships
    session = relationship("AnalysisSession", back_populates="results")
    configuration = relationship("Configuration", back_populates="results")

class AnalysisTask(BaseModel):
    __tablename__ = "analysis_tasks"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    task_id = Column(String(255), unique=True, nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("AnalysisSession", back_populates="tasks")
```

### 7.2 Database Migrations

```python
# backend/app/database/migrations/versions/001_initial_tables.py
"""Initial tables migration

Revision ID: 001
Revises:
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create analysis_sessions table
    op.create_table('analysis_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_files', sa.Integer(), nullable=True),
        sa.Column('processed_files', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create other tables...
    # (Similar structure for configurations, file_uploads, analysis_results, analysis_tasks)

def downgrade():
    # Drop tables in reverse order
    op.drop_table('analysis_tasks')
    op.drop_table('analysis_results')
    op.drop_table('file_uploads')
    op.drop_table('configurations')
    op.drop_table('analysis_sessions')
    op.drop_table('users')
```

### 7.3 Database Connection and Session Management

```python
# backend/app/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://verificai:verificai123@localhost:5432/verificai")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---
