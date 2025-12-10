"""
Code entry model for storing pasted code snippets
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class CodeEntry(Base):
    """Model for storing code entries pasted by users"""

    __tablename__ = "code_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_content = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    lines_count = Column(Integer, nullable=False)
    characters_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="code_entries")

    @property
    def id_str(self) -> str:
        """Return UUID as string for serialization"""
        return str(self.id)

    def __repr__(self):
        return f"<CodeEntry(id={self.id}, title='{self.title}', language='{self.language}')>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "code_content": self.code_content,
            "title": self.title,
            "description": self.description,
            "language": self.language,
            "lines_count": self.lines_count,
            "characters_count": self.characters_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": str(self.user_id),
            "is_active": self.is_active
        }