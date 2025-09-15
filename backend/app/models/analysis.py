"""
Analysis model for VerificAI Backend
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, AuditMixin


class AnalysisStatus(str, Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisResult(BaseModel):
    """Analysis result model for storing detailed results"""

    __tablename__ = "analysis_results"

    # Relationship
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)
    analysis = relationship("Analysis", back_populates="result")

    # Results data
    summary = Column(Text, nullable=False)
    detailed_findings = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)  # 0-100 quality score
    confidence = Column(String(10), nullable=True)  # 0.0-1.0 confidence score

    # Detailed analysis data (JSON)
    issues = Column(JSON, nullable=True)  # List of issues found
    metrics = Column(JSON, nullable=True)  # Performance, security, etc. metrics
    code_snippets = Column(JSON, nullable=True)  # Relevant code snippets
    file_analysis = Column(JSON, nullable=True)  # Per-file analysis results

    # AI model information
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(String(20), nullable=True)  # Processing time in seconds

    # Quality indicators
    quality_score = Column(Integer, nullable=True)  # 0-100
    security_score = Column(Integer, nullable=True)  # 0-100
    performance_score = Column(Integer, nullable=True)  # 0-100
    maintainability_score = Column(Integer, nullable=True)  # 0-100

    def get_issues(self) -> list[dict]:
        """Get issues as list"""
        if not self.issues:
            return []
        return self.issues

    def get_metrics(self) -> dict:
        """Get metrics as dictionary"""
        if not self.metrics:
            return {}
        return self.metrics

    def get_code_snippets(self) -> list[dict]:
        """Get code snippets as list"""
        if not self.code_snippets:
            return []
        return self.code_snippets

    def get_file_analysis(self) -> dict:
        """Get file analysis as dictionary"""
        if not self.file_analysis:
            return {}
        return self.file_analysis

    def add_issue(self, issue: dict) -> None:
        """Add an issue to the analysis"""
        if not self.issues:
            self.issues = []
        self.issues.append(issue)

    def add_metric(self, name: str, value: any) -> None:
        """Add a metric to the analysis"""
        if not self.metrics:
            self.metrics = {}
        self.metrics[name] = value

    def add_code_snippet(self, snippet: dict) -> None:
        """Add a code snippet to the analysis"""
        if not self.code_snippets:
            self.code_snippets = []
        self.code_snippets.append(snippet)

    def to_dict(self) -> dict:
        """Convert analysis result to dictionary"""
        data = super().to_dict()

        # Add computed fields
        data['issues'] = self.get_issues()
        data['metrics'] = self.get_metrics()
        data['code_snippets'] = self.get_code_snippets()
        data['file_analysis'] = self.get_file_analysis()

        return data


class Analysis(BaseModel, AuditMixin):
    """Analysis model for tracking code analysis jobs"""

    __tablename__ = "analyses"

    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="analyses")
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    prompt = relationship("Prompt", back_populates="analyses")
    result = relationship("AnalysisResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

    # Input data
    repository_url = Column(String(500), nullable=True)
    file_paths = Column(Text, nullable=True)  # JSON array of file paths
    code_content = Column(Text, nullable=True)  # Raw code content
    configuration = Column(JSON, nullable=True)  # Analysis configuration

    # Processing information
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    progress_percentage = Column(Integer, default=0, nullable=False)

    # Metadata
    language = Column(String(50), nullable=True)
    total_files = Column(Integer, default=0, nullable=False)
    total_lines = Column(Integer, default=0, nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)

    # Results summary
    total_issues = Column(Integer, default=0, nullable=False)
    critical_issues = Column(Integer, default=0, nullable=False)
    warning_issues = Column(Integer, default=0, nullable=False)
    info_issues = Column(Integer, default=0, nullable=False)

    # Quality scores
    overall_score = Column(Integer, nullable=True)  # 0-100
    security_score = Column(Integer, nullable=True)  # 0-100
    performance_score = Column(Integer, nullable=True)  # 0-100
    maintainability_score = Column(Integer, nullable=True)  # 0-100

    # AI model information
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(String(20), nullable=True)  # Processing time in seconds

    # Cost tracking
    estimated_cost = Column(String(20), nullable=True)
    actual_cost = Column(String(20), nullable=True)

    def get_file_paths(self) -> list[str]:
        """Get file paths as list"""
        if not self.file_paths:
            return []
        import json
        return json.loads(self.file_paths)

    def set_file_paths(self, paths: list[str]) -> None:
        """Set file paths from list"""
        import json
        self.file_paths = json.dumps(paths)

    def get_configuration(self) -> dict:
        """Get configuration as dictionary"""
        if not self.configuration:
            return {}
        return self.configuration

    def set_configuration(self, config: dict) -> None:
        """Set configuration from dictionary"""
        self.configuration = config

    def start_processing(self) -> None:
        """Start analysis processing"""
        self.status = AnalysisStatus.PROCESSING
        self.started_at = datetime.utcnow()
        self.progress_percentage = 0

    def complete_processing(self) -> None:
        """Complete analysis processing"""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100

    def fail_processing(self, error_message: str) -> None:
        """Mark analysis as failed"""
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message

    def cancel_processing(self) -> None:
        """Cancel analysis processing"""
        self.status = AnalysisStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def update_progress(self, percentage: int) -> None:
        """Update processing progress"""
        self.progress_percentage = max(0, min(100, percentage))

    def get_processing_duration(self) -> Optional[str]:
        """Get processing duration in seconds"""
        if not self.started_at or not self.completed_at:
            return None

        duration = (self.completed_at - self.started_at).total_seconds()
        return str(duration)

    def calculate_scores(self) -> None:
        """Calculate overall scores from result"""
        if self.result:
            self.overall_score = self.result.quality_score
            self.security_score = self.result.security_score
            self.performance_score = self.result.performance_score
            self.maintainability_score = self.result.maintainability_score

            # Count issues
            issues = self.result.get_issues()
            self.total_issues = len(issues)
            self.critical_issues = len([i for i in issues if i.get('severity') == 'critical'])
            self.warning_issues = len([i for i in issues if i.get('severity') == 'warning'])
            self.info_issues = len([i for i in issues if i.get('severity') == 'info'])

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert analysis to dictionary"""
        data = super().to_dict()

        # Add computed fields
        data['file_paths'] = self.get_file_paths()
        data['configuration'] = self.get_configuration()
        data['processing_duration'] = self.get_processing_duration()

        # Add user info
        if hasattr(self, 'user') and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            }

        # Add prompt info
        if hasattr(self, 'prompt') and self.prompt:
            data['prompt'] = {
                'id': self.prompt.id,
                'name': self.prompt.name,
                'category': self.prompt.category.value
            }

        # Add result if exists
        if hasattr(self, 'result') and self.result:
            data['result'] = self.result.to_dict()

        return data

    def __repr__(self) -> str:
        """String representation of analysis"""
        return f"<Analysis(id={self.id}, name='{self.name}', status='{self.status}', user_id={self.user_id})>"