"""
Configuration management for VerificAI Backend
"""

import os
from typing import List, Optional
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Project Information
    PROJECT_NAME: str = "VerificAI Code Quality System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://verificai:verificai123@localhost:5432/verificai",
        env="DATABASE_URL"
    )

    # Supabase Configuration for Vercel deployment
    SUPABASE_URL: str = Field(
        default="https://mcp.supabase.com/mcp?project_ref=jjxmfidggofuaxcdtkrd",
        env="SUPABASE_URL"
    )
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")

    # Environment Detection
    IS_VERCEL_DEPLOYMENT: bool = Field(default=False, env="VERCEL")
    IS_RENDER_DEPLOYMENT: bool = Field(default=False, env="RENDER")

    # Database Configuration with Environment Detection
    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def validate_database_url(cls, v):
        """Database configuration with environment detection"""
        print(f"DEBUG: Starting database URL validation...")

        # Check if DATABASE_URL is already set in environment
        env_database_url = os.getenv('DATABASE_URL')
        if env_database_url and env_database_url.startswith('postgresql://'):
            print(f"DEBUG: Found DATABASE_URL in environment, using it directly")
            return env_database_url

        # Check if we're in Vercel or Render deployment
        is_vercel = os.getenv('VERCEL', 'false').lower() == 'true'
        is_render = os.getenv('RENDER', 'false').lower() == 'true'
        is_production = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

        print(f"DEBUG: Environment - Vercel: {is_vercel}, Render: {is_render}, Production: {is_production}")

        if is_vercel or is_render or is_production:
            # Use Supabase for production deployment
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            project_ref = os.getenv('SUPABASE_PROJECT_REF', 'jjxmfidggofuaxcdtkrd')

            print(f"DEBUG: Project ref: {project_ref}")
            print(f"DEBUG: Supabase key found: {'Yes' if supabase_key else 'No'}")

            if supabase_key:
                # Debug information (show first few chars only for security)
                key_preview = supabase_key[:10] + "..." if len(supabase_key) > 10 else supabase_key
                print(f"DEBUG: Found SUPABASE_SERVICE_ROLE_KEY: {key_preview}")

                # Try direct connection format (not pooler) with just 'postgres' as user
                # This is the standard Supabase format for direct connections
                db_url = f"postgresql://postgres:{supabase_key}@db.{project_ref}.supabase.co:5432/postgres"

                deployment_type = "Vercel" if is_vercel else "Render" if is_render else "Production"
                print(f"DEBUG: Using Supabase database for {deployment_type} deployment (direct connection)")
                print(f"DEBUG: Generated DB URL: postgresql://postgres:***@db.{project_ref}.supabase.co:5432/postgres")

                return db_url
            else:
                print(f"DEBUG: WARNING: SUPABASE_SERVICE_ROLE_KEY not found in production environment")
                # Return a fallback that will fail gracefully
                return "postgresql://localhost:5432/verificai"

        # Local development - use PostgreSQL
        if not v:
            print(f"DEBUG: No DATABASE_URL provided, using local default")
            return "postgresql://verificai:verificai123@localhost:5432/verificai"

        # Ensure it's PostgreSQL
        if not v.startswith('postgresql'):
            print(f"DEBUG: WARNING: Non-PostgreSQL database detected: {v}")
            return "postgresql://verificai:verificai123@localhost:5432/verificai"

        print(f"DEBUG: Using provided PostgreSQL database")
        return v

    # Database Connection Pool Settings
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")

    # Security Configuration
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        env="SECRET_KEY"
    )
    JWT_SECRET_KEY: str = Field(
        default="your-jwt-secret-key-here",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3011",
            "http://localhost:3012",
            "http://localhost:3013",
            "http://localhost:3014",
            "http://localhost:3015",
            "http://localhost:3026",
            "http://localhost:5173",
            "https://verificai-frontend.vercel.app",
            "https://verificai-frontend-*.vercel.app"
        ],
        env="BACKEND_CORS_ORIGINS"
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from environment variable"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # LLM API Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # LLM Configuration
    MAX_TOKENS: int = Field(default=16000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.1, env="TEMPERATURE")
    TOP_P: float = Field(default=0.9, env="TOP_P")
    MODEL: str = Field(default="claude-3-5-sonnet-20241022", env="MODEL")

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=10, env="RATE_LIMIT_BURST")

    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=104857600, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs"],
        env="ALLOWED_EXTENSIONS"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Allow extra environment variables
    }


# Global settings instance
settings = Settings()