"""
Prompt model for VerificAI Backend
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, AuditMixin


class PromptCategory(str, Enum):
    """Prompt category enumeration"""
    CODE_REVIEW = "code_review"
    BUG_DETECTION = "bug_detection"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"
    ARCHITECTURE = "architecture"
    CUSTOM = "custom"


class PromptStatus(str, Enum):
    """Prompt status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PromptConfiguration(BaseModel, AuditMixin):
    """Model for storing user prompt configurations"""

    __tablename__ = "prompt_configurations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    config_key = Column(String(100), nullable=False, index=True)  # e.g., "general", "architectural", "business"
    config_data = Column(JSON, nullable=False)  # Stores the complete prompt configuration
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="prompt_configurations")

    def __repr__(self) -> str:
        return f"<PromptConfiguration(id={self.id}, user_id={self.user_id}, config_key='{self.config_key}')>"


class Prompt(BaseModel, AuditMixin):
    """Prompt model for storing AI analysis prompts"""

    __tablename__ = "prompts"

    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(PromptCategory), nullable=False)
    status = Column(SQLEnum(PromptStatus), default=PromptStatus.DRAFT, nullable=False)

    # Prompt content
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    output_format_instructions = Column(Text, nullable=True)

    # Configuration
    temperature = Column(String(10), default="0.1", nullable=False)
    max_tokens = Column(Integer, default=4096, nullable=False)
    model_name = Column(String(100), default="gpt-4-turbo-preview", nullable=False)

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(String(10), default="0.0", nullable=False)
    average_response_time = Column(String(10), default="0.0", nullable=False)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON array of tags
    version = Column(String(20), default="1.0", nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    # Language and file type support
    supported_languages = Column(Text, nullable=True)  # JSON array of programming languages
    supported_file_types = Column(Text, nullable=True)  # JSON array of file extensions

    # Relationships
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="prompts")
    analyses = relationship("Analysis", back_populates="prompt", cascade="all, delete-orphan")

    def get_tags(self) -> list[str]:
        """Get tags as list"""
        if not self.tags:
            return []
        import json
        return json.loads(self.tags)

    def set_tags(self, tags: list[str]) -> None:
        """Set tags from list"""
        import json
        self.tags = json.dumps(tags)

    def get_supported_languages(self) -> list[str]:
        """Get supported languages as list"""
        if not self.supported_languages:
            return []
        import json
        return json.loads(self.supported_languages)

    def set_supported_languages(self, languages: list[str]) -> None:
        """Set supported languages from list"""
        import json
        self.supported_languages = json.dumps(languages)

    def get_supported_file_types(self) -> list[str]:
        """Get supported file types as list"""
        if not self.supported_file_types:
            return []
        import json
        return json.loads(self.supported_file_types)

    def set_supported_file_types(self, file_types: list[str]) -> None:
        """Set supported file types from list"""
        import json
        self.supported_file_types = json.dumps(file_types)

    def increment_usage(self) -> None:
        """Increment usage count"""
        self.usage_count += 1

    def update_success_rate(self, success: bool) -> None:
        """Update success rate based on result"""
        total_successes = int(float(self.success_rate or "0") * self.usage_count)
        if success:
            total_successes += 1

        self.usage_count += 1
        self.success_rate = str(total_successes / self.usage_count)

    def supports_language(self, language: str) -> bool:
        """Check if prompt supports specific language"""
        supported = self.get_supported_languages()
        return not supported or language.lower() in [lang.lower() for lang in supported]

    def supports_file_type(self, file_type: str) -> bool:
        """Check if prompt supports specific file type"""
        supported = self.get_supported_file_types()
        return not supported or file_type.lower() in [ft.lower() for ft in supported]

    def create_version(self, new_name: Optional[str] = None) -> "Prompt":
        """Create a new version of this prompt"""
        version_parts = self.version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        new_version = '.'.join(version_parts)

        return Prompt(
            name=new_name or f"{self.name} v{new_version}",
            description=self.description,
            category=self.category,
            system_prompt=self.system_prompt,
            user_prompt_template=self.user_prompt_template,
            output_format_instructions=self.output_format_instructions,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            model_name=self.model_name,
            tags=self.tags,
            version=new_version,
            supported_languages=self.supported_languages,
            supported_file_types=self.supported_file_types,
            author_id=self.author_id
        )

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert prompt to dictionary"""
        data = super().to_dict()

        # Add computed fields
        data['tags'] = self.get_tags()
        data['supported_languages'] = self.get_supported_languages()
        data['supported_file_types'] = self.get_supported_file_types()

        # Add author info
        if hasattr(self, 'author') and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username,
                'full_name': self.author.full_name
            }

        return data

    def __repr__(self) -> str:
        """String representation of prompt"""
        return f"<Prompt(id={self.id}, name='{self.name}', category='{self.category}', status='{self.status}')>"