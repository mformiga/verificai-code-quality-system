"""
Pydantic schemas for VerificAI Backend
"""

from .user import UserCreate, UserUpdate, UserResponse, UserLogin
from .prompt import PromptCreate, PromptUpdate, PromptResponse, PromptListResponse
from .analysis import (
    AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisListResponse,
    AnalysisResultResponse
)
from .code_entry import (
    CodeEntryCreate, CodeEntryUpdate, CodeEntryResponse, CodeEntryList,
    CodeEntryDeleteResponse, CodeLanguageDetection, CodeEntryStats
)
from .common import PaginationParams, PaginatedResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "PromptCreate", "PromptUpdate", "PromptResponse", "PromptListResponse",
    "AnalysisCreate", "AnalysisUpdate", "AnalysisResponse", "AnalysisListResponse",
    "AnalysisResultResponse",
    "CodeEntryCreate", "CodeEntryUpdate", "CodeEntryResponse", "CodeEntryList",
    "CodeEntryDeleteResponse", "CodeLanguageDetection", "CodeEntryStats",
    "PaginationParams", "PaginatedResponse"
]