"""
File path model for VerificAI Backend
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, LargeBinary, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class FilePath(Base, BaseModel):
    """Model for storing file path information"""

    __tablename__ = "file_paths"

    # File identification
    file_id = Column(String(255), unique=True, nullable=False, index=True)

    # Path information
    full_path = Column(Text, nullable=False, index=True)  # Complete file path
    file_name = Column(String(500), nullable=False, index=True)  # File name with extension
    file_extension = Column(String(50), nullable=True, index=True)  # File extension
    folder_path = Column(Text, nullable=False, index=True)  # Directory path

    # File metadata
    file_size = Column(Integer, nullable=True)  # Size in bytes
    last_modified = Column(DateTime, nullable=True)  # Last modified timestamp

    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(50), nullable=True)  # pending, processing, completed, error
    processing_error = Column(Text, nullable=True)

    # Additional metadata
    file_metadata = Column(JSON, nullable=True)  # Additional file metadata

    # Ownership and access
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(20), default="private", nullable=False)  # private, team, public

    # Relationships
    user = relationship("User", backref="file_paths")

    def __init__(self, **kwargs):
        """Initialize with file_id if not provided"""
        if 'file_id' not in kwargs:
            kwargs['file_id'] = f"path_{uuid.uuid4().hex}"
        super().__init__(**kwargs)

    def get_file_extension(self) -> str:
        """Get file extension from filename"""
        if self.file_extension:
            return self.file_extension
        _, ext = os.path.splitext(self.file_name)
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

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert file path to dictionary"""
        data = super().to_dict()

        # Rename metadata field for JSON serialization
        if 'file_metadata' in data:
            data['metadata'] = data.pop('file_metadata')

        # Add computed fields
        data['human_readable_size'] = self.get_human_readable_size()
        data['detected_extension'] = self.get_file_extension()

        # Add user info if available
        if hasattr(self, 'user') and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            }

        # Exclude sensitive fields
        if not include_sensitive:
            sensitive_fields = []
            for field in sensitive_fields:
                data.pop(field, None)

        return data

    def __repr__(self) -> str:
        """String representation of file path"""
        return f"<FilePath(file_id='{self.file_id}', name='{self.file_name}', path='{self.full_path[:50]}...')>"