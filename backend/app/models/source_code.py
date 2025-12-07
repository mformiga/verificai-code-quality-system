"""
Source code content model for VerificAI Backend
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TEXT

from app.models.base import Base


class SourceCodeStatus(str, Enum):
    """Source code status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class SourceCode(Base):
    """Model for storing source code content directly as text"""

    __tablename__ = "source_codes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    code_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)  # User-defined title for the code
    description = Column(Text, nullable=True)  # Optional description

    # Source code content (main field)
    content = Column(Text, nullable=False)  # PostgreSQL TEXT field - up to 1GB limit

    # File information (simulating file properties)
    file_name = Column(String(500), nullable=False)  # Simulated filename
    file_extension = Column(String(10), nullable=False)  # File extension for language detection
    programming_language = Column(String(50), nullable=True)  # Auto-detected or user-specified

    # Code metrics
    line_count = Column(Integer, nullable=True)  # Number of lines in the code
    character_count = Column(Integer, nullable=True)  # Total characters
    size_bytes = Column(Integer, nullable=True)  # Size in bytes (content length)

    # Content analysis
    language_detected = Column(String(50), nullable=True)  # Auto-detected language
    complexity_score = Column(String(10), nullable=True)  # e.g., "7.5"

    # Classification and tagging
    category = Column(String(100), nullable=True)  # e.g., "function", "class", "module", "script"
    tags = Column(Text, nullable=True)  # JSON array of tags
    code_metadata = Column(JSON, nullable=True)  # Additional metadata

    # Status and visibility
    status = Column(String(20), default=SourceCodeStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)  # If it's a template/example

    # Processing information
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(50), default="pending", nullable=False)
    processing_error = Column(Text, nullable=True)

    # Analysis information
    analysis_id = Column(String(255), nullable=True)  # Link to analysis if any
    last_analyzed_at = Column(DateTime, nullable=True)

    # Ownership and access
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Temporarily nullable
    access_level = Column(String(20), default="private", nullable=False)  # private, team, public

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="source_codes")

    def __init__(self, **kwargs):
        """Initialize with code_id if not provided"""
        if 'code_id' not in kwargs:
            kwargs['code_id'] = f"code_{uuid.uuid4().hex}"
        super().__init__(**kwargs)

    def get_file_extension(self) -> str:
        """Get file extension from filename"""
        if self.file_extension:
            return self.file_extension
        _, ext = self.file_name.split('.') if '.' in self.file_name else (self.file_name, '')
        return ext.lstrip('.') if ext else ''

    def get_programming_language(self) -> str:
        """Get the programming language for this source code"""
        if self.programming_language:
            return self.programming_language
        if self.language_detected:
            return self.language_detected
        return self.detect_language_from_extension()

    def detect_language_from_extension(self) -> str:
        """Detect programming language from file extension"""
        extension = self.get_file_extension().lower()

        language_map = {
            'js': 'JavaScript',
            'jsx': 'JavaScript',
            'ts': 'TypeScript',
            'tsx': 'TypeScript',
            'py': 'Python',
            'java': 'Java',
            'c': 'C',
            'cpp': 'C++',
            'cxx': 'C++',
            'cc': 'C++',
            'h': 'C/C++ Header',
            'hpp': 'C++ Header',
            'cs': 'C#',
            'go': 'Go',
            'rs': 'Rust',
            'rb': 'Ruby',
            'php': 'PHP',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'scala': 'Scala',
            'm': 'Objective-C',
            'sh': 'Shell',
            'bash': 'Shell',
            'zsh': 'Shell',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'sass': 'Sass',
            'less': 'Less',
            'json': 'JSON',
            'xml': 'XML',
            'yaml': 'YAML',
            'yml': 'YAML',
            'toml': 'TOML',
            'ini': 'INI',
            'conf': 'Configuration',
            'config': 'Configuration',
            'md': 'Markdown',
            'txt': 'Plain Text'
        }

        return language_map.get(extension, 'Unknown')

    def calculate_metrics(self) -> None:
        """Calculate and update code metrics"""
        if self.content:
            self.line_count = len(self.content.splitlines())
            self.character_count = len(self.content)
            self.size_bytes = len(self.content.encode('utf-8'))

    def get_content_preview(self, lines: int = 10) -> str:
        """Get a preview of the content (first N lines)"""
        if not self.content:
            return ""

        content_lines = self.content.splitlines()
        preview_lines = content_lines[:lines]

        if len(content_lines) > lines:
            preview_lines.append("... (truncated)")

        return '\n'.join(preview_lines)

    def get_tags_list(self) -> list[str]:
        """Get tags as list"""
        if not self.tags:
            return []
        import json
        try:
            return json.loads(self.tags)
        except:
            return []

    def set_tags_list(self, tags: list[str]) -> None:
        """Set tags from list"""
        import json
        self.tags = json.dumps(tags)

    def is_valid_language(self) -> bool:
        """Check if the programming language is supported for analysis"""
        supported_languages = {
            'JavaScript', 'TypeScript', 'Python', 'Java', 'C', 'C++',
            'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala',
            'Shell', 'SQL', 'HTML', 'CSS', 'SCSS', 'Sass', 'Less',
            'JSON', 'XML', 'YAML', 'Markdown', 'Plain Text'
        }
        return self.get_programming_language() in supported_languages

    def get_size_info(self) -> dict:
        """Get size information for the content"""
        if not self.content:
            return {
                'size_bytes': 0,
                'size_kb': 0,
                'size_mb': 0,
                'size_percentage_of_limit': 0.0,
                'within_limits': True
            }

        size_bytes = len(self.content.encode('utf-8'))
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024

        # PostgreSQL TEXT field limit is 1GB
        limit_bytes = 1024 * 1024 * 1024  # 1GB
        percentage = (size_bytes / limit_bytes) * 100

        return {
            'size_bytes': size_bytes,
            'size_kb': round(size_kb, 2),
            'size_mb': round(size_mb, 2),
            'size_percentage_of_limit': round(percentage, 4),
            'within_limits': size_bytes < limit_bytes
        }

    def to_dict(self, include_content: bool = False, include_sensitive: bool = False) -> dict:
        """Convert source code to dictionary"""
        data = super().to_dict()

        # Add content if requested
        if include_content:
            data['content'] = self.content
            data['content_preview'] = self.get_content_preview()
        else:
            # Only include preview by default
            data.pop('content', None)
            data['content_preview'] = self.get_content_preview()

        # Add computed fields
        data['programming_language'] = self.get_programming_language()
        data['size_info'] = self.get_size_info()
        data['tags'] = self.get_tags_list()

        # Add user info if available
        if hasattr(self, 'user') and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            }

        # Exclude sensitive fields
        if not include_sensitive:
            # For now, no specific sensitive fields to exclude
            pass

        return data

    def __repr__(self) -> str:
        """String representation of source code"""
        return f"<SourceCode(code_id='{self.code_id}', title='{self.title}', language='{self.get_programming_language()}')>"