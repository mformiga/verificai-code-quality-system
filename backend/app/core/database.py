"""
Database configuration and connection management for VerificAI Backend
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from typing import Generator
import logging

from app.core.config import settings
from app.models.base import BaseModel as Base

# Import all models to ensure they are registered with SQLAlchemy
# This must happen BEFORE creating the engine
from app.models.user import User
from app.models.prompt import Prompt, PromptConfiguration
from app.models.analysis import Analysis, AnalysisResult
from app.models.uploaded_file import UploadedFile

logger = logging.getLogger(__name__)

# SQLAlchemy configuration
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)


def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_redis() -> redis.Redis:
    """Redis dependency for FastAPI routes"""
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            encoding="utf-8",
            decode_responses=True
        )
        # Test connection
        await redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        raise


def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop database tables (use with caution)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


class DatabaseManager:
    """Database connection and transaction manager"""

    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.session_factory()

    def execute_raw_sql(self, sql: str, params: dict = None) -> any:
        """Execute raw SQL with parameters"""
        with self.get_session() as session:
            result = session.execute(sql, params or {})
            session.commit()
            return result

    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()# Force reload 2
