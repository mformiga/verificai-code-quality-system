"""
Prompt models for VerificAI Backend.
These models store the configuration for the three main prompt types
and their version history.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, BaseModel, AuditMixin


class PromptType(str, enum.Enum):
    """Enumeration for the three types of prompts."""
    GENERAL = "general"
    ARCHITECTURAL = "architectural"
    BUSINESS = "business"


class PromptCategory(str, enum.Enum):
    """Enumeration for prompt categories."""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE = "architecture"
    BUSINESS = "business"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


class PromptStatus(str, enum.Enum):
    """Enumeration for prompt status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class Prompt(Base, BaseModel, AuditMixin):
    """
    Stores the current version of a configurable prompt.
    There will be exactly one row for each PromptType.
    """
    __tablename__ = "prompts"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(
        SQLEnum(PromptType, name="prompt_type_enum"),
        nullable=False,
        unique=True,
        index=True,
    )
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    history = relationship(
        "PromptHistory",
        back_populates="prompt",
        cascade="all, delete-orphan",
        order_by="desc(PromptHistory.version)",
    )
    author = relationship("User", back_populates="prompts")
    analyses = relationship("Analysis", back_populates="prompt")

    def __repr__(self) -> str:
        return f"<Prompt(type='{self.type}', version={self.version})>"


class PromptHistory(Base, BaseModel):
    """
    Stores a historical version of a prompt.
    """
    __tablename__ = "prompt_history"

    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    # Relationships
    prompt = relationship("Prompt", back_populates="history")

    __table_args__ = (
        UniqueConstraint("prompt_id", "version", name="uq_prompt_version"),
    )

    def __repr__(self) -> str:
        return f"<PromptHistory(prompt_id={self.prompt_id}, version={self.version})>"


class GeneralCriteria(Base, BaseModel, AuditMixin):
    """
    Stores user-specific criteria for general analysis.
    """
    __tablename__ = "general_criteria"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="general_criteria")

    __table_args__ = (
        UniqueConstraint("user_id", "text", name="uq_user_criteria_text"),
    )

    def __repr__(self) -> str:
        return f"<GeneralCriteria(user_id={self.user_id}, text='{self.text[:50]}...', active={self.is_active})>"


class PromptConfiguration(Base, BaseModel, AuditMixin):
    """
    Stores user-specific prompt configurations and settings.
    """
    __tablename__ = "prompt_configurations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt_type = Column(SQLEnum(PromptType, name="prompt_type_enum"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    settings = Column(JSON, nullable=True)  # Additional configuration settings

    # Relationships
    user = relationship("User", back_populates="prompt_configurations")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_prompt_name"),
        UniqueConstraint("user_id", "prompt_type", name="uq_user_prompt_type"),
    )

    def __repr__(self) -> str:
        return f"<PromptConfiguration(user_id={self.user_id}, prompt_type='{self.prompt_type}', name='{self.name}')>"
