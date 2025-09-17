"""
Database models for VerificAI Backend
"""

from .user import User, UserRole
from .prompt import Prompt, PromptType, PromptConfiguration, PromptCategory, PromptStatus
from .analysis import Analysis, AnalysisStatus, AnalysisResult
from .uploaded_file import UploadedFile
from .file_path import FilePath
from .base import BaseModel, TimestampMixin

__all__ = [
    "User",
    "UserRole",
    "Prompt",
    "PromptType",
    "PromptConfiguration",
    "PromptCategory",
    "PromptStatus",
    "Analysis",
    "AnalysisStatus",
    "AnalysisResult",
    "UploadedFile",
    "FilePath",
    "BaseModel",
    "TimestampMixin"
]