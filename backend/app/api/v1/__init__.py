"""
API v1 endpoints for VerificAI Backend
"""

from . import auth, users, prompts, analysis, upload, file_paths, general_analysis

__all__ = ["auth", "users", "prompts", "analysis", "upload", "file_paths", "general_analysis"]

# Reload trigger - touched at 2025-09-18 19:05