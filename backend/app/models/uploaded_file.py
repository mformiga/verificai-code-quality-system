"""
Uploaded file model for VerificAI Backend
"""

import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, LargeBinary, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class FileStatus(str, Enum):
    """File upload status enumeration"""
    UPLOADING = "uploading"
    COMPLETED = "completed"
    ERROR = "error"
    DELETED = "deleted"


class ProcessingStatus(str, Enum):
    """File processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class UploadedFile(Base, BaseModel):
    """Model for storing uploaded file information"""

    __tablename__ = "uploaded_files"

    # Basic information
    file_id = Column(String(255), unique=True, nullable=False, index=True)
    original_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)  # Relative path from upload
    relative_path = Column(String(1000), nullable=True)  # Original relative path if from folder
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    file_extension = Column(String(10), nullable=True)

    # Storage information
    storage_path = Column(String(1000), nullable=False)  # Full path on disk
    checksum = Column(String(64), nullable=True)  # SHA-256 checksum
    is_compressed = Column(Boolean, default=False, nullable=False)

    # Upload status
    status = Column(String(20), default=FileStatus.UPLOADING, nullable=False)
    upload_progress = Column(Integer, default=0, nullable=False)  # 0-100
    error_message = Column(Text, nullable=True)

    # File processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(50), nullable=True)  # pending, processing, completed, error
    processing_error = Column(Text, nullable=True)

    # Analysis information
    analysis_id = Column(String(255), nullable=True)  # Link to analysis if any
    language_detected = Column(String(50), nullable=True)  # Detected programming language
    line_count = Column(Integer, nullable=True)
    complexity_score = Column(String(10), nullable=True)  # e.g., "7.5"

    # Metadata
    file_metadata = Column(JSON, nullable=True)  # Additional file metadata
    tags = Column(Text, nullable=True)  # JSON array of tags

    # Ownership and access
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(20), default="private", nullable=False)  # private, team, public

    # Relationships
    user = relationship("User", backref="uploaded_files")

    def __init__(self, **kwargs):
        """Initialize with file_id if not provided"""
        if 'file_id' not in kwargs:
            kwargs['file_id'] = f"file_{uuid.uuid4().hex}"
        super().__init__(**kwargs)

    def get_file_extension(self) -> str:
        """Get file extension from filename"""
        if self.file_extension:
            return self.file_extension
        _, ext = os.path.splitext(self.original_name)
        return ext.lstrip('.') if ext else ''

    def get_human_readable_size(self) -> str:
        """Get human readable file size"""
        size = self.file_size
        if size == 0:
            return "0 Bytes"

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_language_from_extension(self) -> Optional[str]:
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
            'txt': 'Plain Text',
            'log': 'Log'
        }

        return language_map.get(extension)

    def get_tags_list(self) -> list[str]:
        """Get tags as list"""
        if not self.tags:
            return []
        import json
        return json.loads(self.tags)

    def set_tags_list(self, tags: list[str]) -> None:
        """Set tags from list"""
        import json
        self.tags = json.dumps(tags)

    def is_valid_file_type(self) -> bool:
        """Check if file type is supported for analysis"""
        supported_extensions = {
            'js', 'jsx', 'ts', 'tsx', 'py', 'java', 'c', 'cpp', 'cxx', 'cc',
            'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala',
            'm', 'sh', 'bash', 'zsh', 'sql', 'html', 'css', 'scss', 'sass', 'less',
            'json', 'xml', 'yaml', 'yml', 'toml', 'ini', 'conf', 'config', 'md', 'txt'
        }
        return self.get_file_extension().lower() in supported_extensions

    def get_safe_filename(self) -> str:
        """Get safe filename for storage"""
        # Remove or replace unsafe characters
        import re
        safe_name = re.sub(r'[^\w\-_\.]', '_', self.original_name)
        return safe_name

    def calculate_checksum(self, file_content: bytes) -> str:
        """Calculate SHA-256 checksum of file content"""
        import hashlib
        return hashlib.sha256(file_content).hexdigest()

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert uploaded file to dictionary"""
        data = super().to_dict()

        # Rename metadata field for JSON serialization
        if 'file_metadata' in data:
            data['metadata'] = data.pop('file_metadata')

        # Add computed fields
        data['human_readable_size'] = self.get_human_readable_size()
        data['detected_language'] = self.get_language_from_extension() or self.language_detected
        data['is_supported_type'] = self.is_valid_file_type()
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
            sensitive_fields = ['storage_path', 'checksum']
            for field in sensitive_fields:
                data.pop(field, None)

        return data

    def __repr__(self) -> str:
        """String representation of uploaded file"""
        return f"<UploadedFile(file_id='{self.file_id}', name='{self.original_name}', status='{self.status}')>"