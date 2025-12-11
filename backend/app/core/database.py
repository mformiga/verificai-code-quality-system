"""
Database configuration and connection management for VerificAI Backend
Supports both local PostgreSQL and Supabase (for Vercel deployment)
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from typing import Generator, Optional
import logging
import os

from app.core.config import settings
from app.models.base import Base

# Import all models to ensure they are registered with SQLAlchemy
# This must happen BEFORE creating the engine
from app.models.user import User
from app.models.prompt import Prompt, PromptConfiguration
from app.models.analysis import Analysis, AnalysisResult
from app.models.uploaded_file import UploadedFile
from app.models.file_path import FilePath

logger = logging.getLogger(__name__)

# Environment detection
IS_VERCEL = os.getenv('VERCEL', 'false').lower() == 'true'
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

# Determine database type and environment
if IS_VERCEL:
    DATABASE_TYPE = "supabase"
    ENVIRONMENT_NAME = "Vercel"
elif IS_RENDER:
    DATABASE_TYPE = "supabase"
    ENVIRONMENT_NAME = "Render"
elif IS_PRODUCTION:
    DATABASE_TYPE = "supabase"
    ENVIRONMENT_NAME = "Production"
else:
    DATABASE_TYPE = "postgresql"
    ENVIRONMENT_NAME = "Local"

# Database-specific configuration
def get_database_config():
    """Get database configuration based on environment"""
    if DATABASE_TYPE == "supabase":
        logger.info(f"Initializing Supabase database connection for {ENVIRONMENT_NAME} deployment")
        return {
            "pool_size": min(settings.DATABASE_POOL_SIZE, 5),  # Reduce pool size for serverless
            "max_overflow": 0,  # Disable overflow for serverless
            "pool_timeout": 10,  # Reduce timeout for serverless
            "pool_recycle": 300,  # Reduce recycle time for serverless
            "pool_pre_ping": True,
            "echo": settings.DEBUG,
            "connect_args": {
                "sslmode": "require",
                "connect_timeout": 10,
            }
        }
    else:
        logger.info(f"Initializing local PostgreSQL database connection for {ENVIRONMENT_NAME}")
        return {
            "poolclass": QueuePool,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
            "pool_recycle": settings.DATABASE_POOL_RECYCLE,
            "pool_pre_ping": True,
            "echo": settings.DEBUG,
        }

# Debug environment detection BEFORE creating engine
logger.info(f"Environment detection: {ENVIRONMENT_NAME}")
logger.info(f"Database type: {DATABASE_TYPE}")
logger.info(f"Database URL preview: {settings.DATABASE_URL.split('@')[0] + '@***' if '@' in settings.DATABASE_URL else '***'}")

# Initialize database engine and session factory (lazy initialization)
engine = None
SessionLocal = None

def get_database_engine():
    """Get or create database engine with lazy initialization"""
    global engine, SessionLocal
    if engine is None:
        print(f"DEBUG: Creating database engine with URL: {settings.DATABASE_URL.split('@')[0] + '@***'}")
        db_config = get_database_config()
        engine = create_engine(settings.DATABASE_URL, **db_config)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print(f"DEBUG: Database engine created successfully")
    return engine

def get_database_session():
    """Get database session factory"""
    global SessionLocal
    if SessionLocal is None:
        get_database_engine()
    return SessionLocal

# Log database connection info
logger.info(f"Database type: {DATABASE_TYPE}")
logger.info(f"Database URL configured: {'***' if settings.SUPABASE_SERVICE_ROLE_KEY else settings.DATABASE_URL.split('@')[0] + '@***'}")


# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Apply naming convention to existing metadata
Base.metadata.naming_convention = convention


def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI routes with environment-aware error handling"""
    SessionLocal = get_database_session()
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error [{DATABASE_TYPE}]: {e}")
        if IS_VERCEL:
            logger.error("Supabase connection failed - check Vercel environment variables")
        else:
            logger.error("PostgreSQL connection failed - check local database configuration")
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
        db_engine = get_database_engine()
        Base.metadata.create_all(bind=db_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop database tables (use with caution)"""
    try:
        db_engine = get_database_engine()
        Base.metadata.drop_all(bind=db_engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


class DatabaseManager:
    """Database connection and transaction manager"""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    def get_engine(self):
        """Get database engine (lazy initialization)"""
        if self.engine is None:
            self.engine = get_database_engine()
            self.session_factory = get_database_session()
        return self.engine

    def get_session(self) -> Session:
        """Get a new database session"""
        if self.session_factory is None:
            self.get_engine()
        return self.session_factory()

    def execute_raw_sql(self, sql: str, params: dict = None) -> any:
        """Execute raw SQL with parameters"""
        with self.get_session() as session:
            result = session.execute(sql, params or {})
            session.commit()
            return result

    def health_check(self) -> bool:
        """Check database connectivity with environment-specific feedback"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                logger.info(f"Database health check passed for {DATABASE_TYPE}")
                return True
        except Exception as e:
            logger.error(f"Database health check failed [{DATABASE_TYPE}]: {e}")
            if IS_VERCEL:
                logger.error("Supabase health check failed - verify project configuration and credentials")
            else:
                logger.error("PostgreSQL health check failed - verify local database is running")
            return False


# Global database manager instance
db_manager = DatabaseManager()# Force reload 2
