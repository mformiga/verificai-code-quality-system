"""
FastAPI application entry point for VerificAI Code Quality System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
from app.api.v1 import auth, users, prompts, analysis, upload, file_paths, general_analysis
import uvicorn

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
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware stack
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(file_paths.router, prefix=settings.API_V1_STR + "/file-paths", tags=["file_paths"])
app.include_router(prompts.router, prefix=settings.API_V1_STR, tags=["prompts"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])
app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["upload"])
app.include_router(general_analysis.router, prefix=settings.API_V1_STR, tags=["general_analysis"])
# Force reload - changed to trigger restart

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )# Reload trigger
