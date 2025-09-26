"""
FastAPI application entry point for VerificAI Code Quality System
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.database import create_tables, db_manager
from app.core.logging import setup_logging
from app.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    ErrorHandlerMiddleware,
    RateLimitMiddleware
)
from app.api.v1 import auth, users, prompts, analysis, upload, file_paths, general_analysis, simple_analysis
import uvicorn

# Custom CORS middleware to handle OPTIONS requests
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3012"
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        response = await call_next(request)
        return response

# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered code quality analysis system for QA teams",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS middleware first (before other middlewares)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3012"],  # Especificar a origem do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Add middleware stack - Order matters!
app.add_middleware(CustomCORSMiddleware)  # Adicionar middleware CORS personalizado
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(file_paths.router, prefix=settings.API_V1_STR + "/file-paths", tags=["file_paths"])
app.include_router(prompts.router, prefix=settings.API_V1_STR, tags=["prompts"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])
app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["upload"])
app.include_router(general_analysis.router, prefix=settings.API_V1_STR + "/general-analysis", tags=["general_analysis"])
app.include_router(simple_analysis.router, prefix=settings.API_V1_STR + "/simple-analysis", tags=["simple_analysis"])
# Reload trigger - touched at 2025-09-18 19:32 - FORCE RELOAD

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    # Create database tables
    create_tables()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VerificAI Code Quality System API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    db_health = db_manager.health_check()
    return {
        "status": "healthy" if db_health else "unhealthy",
        "service": "verificai-backend",
        "database": "connected" if db_health else "disconnected"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    db_health = db_manager.health_check()
    return {
        "status": "ready" if db_health else "not_ready",
        "service": "verificai-backend",
        "database": "connected" if db_health else "disconnected"
    }

@app.get("/public/file-paths")
async def get_public_file_paths():
    """Get file paths for public access - no authentication required"""
    from app.core.database import get_db
    from app.models.file_path import FilePath
    from sqlalchemy.orm import Session
    from sqlalchemy import desc

    try:
        db = next(get_db())
        # Get all file paths without user filtering
        file_paths = db.query(FilePath).order_by(desc(FilePath.created_at)).limit(50).all()

        # Extract just the full paths for simplicity
        paths = [fp.full_path for fp in file_paths if fp.full_path]

        print(f"Public endpoint returning {len(paths)} file paths")

        return {
            "file_paths": paths,
            "total_count": len(paths),
            "message": f"Found {len(paths)} file paths"
        }

    except Exception as e:
        print(f"Error in public endpoint: {str(e)}")
        return {"file_paths": [], "total_count": 0, "message": "Error occurred"}


@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """Global OPTIONS handler for CORS preflight requests"""
    return {
        "message": "CORS preflight handled",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "headers": ["Content-Type", "Authorization"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
 reload=True,  # Force reload for development
        log_level=settings.LOG_LEVEL.lower()
    )# Reload trigger - touched at 2025-09-18 19:06
