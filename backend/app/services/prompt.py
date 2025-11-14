"""
Prompt service for VerificAI Backend
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.prompt import Prompt, PromptCategory, PromptStatus
from app.models.user import User
from app.core.exceptions import (
    NotFoundError, ValidationError, BusinessRuleError,
    DuplicateResourceError
)


class PromptService:
    """Service for prompt management operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_prompt(self, user_id: int, prompt_data: Dict[str, Any]) -> Prompt:
        """Create a new prompt"""
        # Validate prompt data
        self._validate_prompt_data(prompt_data)

        # Create prompt
        prompt = Prompt(
            **prompt_data,
            author_id=user_id
        )

        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)

        return prompt

    def get_prompt_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """Get prompt by ID"""
        return self.db.query(Prompt).filter(Prompt.id == prompt_id).first()

    def get_prompts(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc"
    ) -> List[Prompt]:
        """Get prompts with filtering, sorting, and pagination"""
        query = self.db.query(Prompt)

        # Apply visibility filter
        if user_id:
            # Users can see their own prompts + public prompts
            query = query.filter(
                or_(
                    Prompt.author_id == user_id,
                    Prompt.is_public == True
                )
            )

        # Apply filters
        if filters:
            if filters.get('category'):
                query = query.filter(Prompt.category == filters['category'])
            if filters.get('status'):
                query = query.filter(Prompt.status == filters['status'])
            if filters.get('is_public') is not None:
                query = query.filter(Prompt.is_public == filters['is_public'])
            if filters.get('is_featured') is not None:
                query = query.filter(Prompt.is_featured == filters['is_featured'])
            if filters.get('author_id'):
                query = query.filter(Prompt.author_id == filters['author_id'])
            if filters.get('supported_language'):
                # Simple contains check - in production, use JSON operations
                query = query.filter(Prompt.supported_languages.contains(filters['supported_language']))
            if filters.get('supported_file_type'):
                query = query.filter(Prompt.supported_file_types.contains(filters['supported_file_type']))

        # Apply search
        if search:
            query = query.filter(
                or_(
                    Prompt.name.contains(search),
                    Prompt.description.contains(search)
                )
            )

        # Apply sorting
        if sort_by:
            sort_column = getattr(Prompt, sort_by, None)
            if sort_column:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(Prompt.created_at))

        return query.offset(skip).limit(limit).all()

    def update_prompt(self, prompt_id: int, user_id: int, prompt_data: Dict[str, Any]) -> Prompt:
        """Update prompt"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if prompt.author_id != user_id:
            raise BusinessRuleError("You can only update your own prompts")

        # Validate prompt data
        self._validate_prompt_data(prompt_data, is_update=True)

        # Update fields
        for field, value in prompt_data.items():
            if hasattr(prompt, field):
                setattr(prompt, field, value)

        self.db.commit()
        self.db.refresh(prompt)

        return prompt

    def delete_prompt(self, prompt_id: int, user_id: int) -> bool:
        """Delete prompt"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if prompt.author_id != user_id:
            raise BusinessRuleError("You can only delete your own prompts")

        self.db.delete(prompt)
        self.db.commit()

        return True

    def test_prompt(self, prompt_id: int, user_id: int, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test prompt with sample code"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if not prompt.is_public and prompt.author_id != user_id:
            raise BusinessRuleError("Access denied")

        # TODO: Implement actual prompt testing logic
        # This is a placeholder implementation
        return {
            "success": True,
            "response": "Test response - this is a placeholder",
            "tokens_used": 100,
            "processing_time": 2.5,
            "cost_estimate": 0.01
        }

    def clone_prompt(self, prompt_id: int, user_id: int, clone_data: Dict[str, Any]) -> Prompt:
        """Clone prompt"""
        original_prompt = self.get_prompt_by_id(prompt_id)
        if not original_prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if not original_prompt.is_public and original_prompt.author_id != user_id:
            raise BusinessRuleError("Access denied")

        # Create clone
        clone = Prompt(
            name=clone_data.get('new_name', f"{original_prompt.name} (Clone)"),
            description=clone_data.get('new_description', original_prompt.description),
            category=original_prompt.category,
            system_prompt=original_prompt.system_prompt,
            user_prompt_template=original_prompt.user_prompt_template,
            output_format_instructions=original_prompt.output_format_instructions,
            temperature=original_prompt.temperature,
            max_tokens=original_prompt.max_tokens,
            model_name=original_prompt.model_name,
            tags=original_prompt.tags,
            supported_languages=original_prompt.supported_languages,
            supported_file_types=original_prompt.supported_file_types,
            author_id=user_id
        )

        self.db.add(clone)
        self.db.commit()
        self.db.refresh(clone)

        return clone

    def validate_prompt(self, prompt_id: int, user_id: int) -> Dict[str, Any]:
        """Validate prompt"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if prompt.author_id != user_id:
            raise BusinessRuleError("Access denied")

        # TODO: Implement actual validation logic
        # This is a placeholder implementation
        return {
            "is_valid": True,
            "errors": [],
            "warnings": ["This is a placeholder validation"],
            "suggestions": ["Consider adding more specific tags"]
        }

    def publish_prompt(self, prompt_id: int, user_id: int) -> Prompt:
        """Publish prompt (make public)"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if prompt.author_id != user_id:
            raise BusinessRuleError("Access denied")

        prompt.is_public = True
        prompt.status = PromptStatus.ACTIVE
        self.db.commit()
        self.db.refresh(prompt)

        return prompt

    def unpublish_prompt(self, prompt_id: int, user_id: int) -> Prompt:
        """Unpublish prompt (make private)"""
        prompt = self.get_prompt_by_id(prompt_id)
        if not prompt:
            raise NotFoundError("Prompt", str(prompt_id))

        # Check permissions
        if prompt.author_id != user_id:
            raise BusinessRuleError("Access denied")

        prompt.is_public = False
        self.db.commit()
        self.db.refresh(prompt)

        return prompt

    def get_prompt_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get prompt statistics"""
        query = self.db.query(Prompt)

        if user_id:
            query = query.filter(Prompt.author_id == user_id)

        total_prompts = query.count()
        active_prompts = query.filter(Prompt.status == PromptStatus.ACTIVE).count()
        public_prompts = query.filter(Prompt.is_public == True).count()

        # Prompts by category
        prompts_by_category = {}
        for category in PromptCategory:
            count = query.filter(Prompt.category == category).count()
            prompts_by_category[category.value] = count

        # Prompts by status
        prompts_by_status = {}
        for status in PromptStatus:
            count = query.filter(Prompt.status == status).count()
            prompts_by_status[status.value] = count

        # Total usage
        total_usage = sum([p.usage_count for p in query.all()])

        return {
            "total_prompts": total_prompts,
            "active_prompts": active_prompts,
            "public_prompts": public_prompts,
            "prompts_by_category": prompts_by_category,
            "prompts_by_status": prompts_by_status,
            "total_usage": total_usage
        }

    def increment_usage(self, prompt_id: int, success: bool = True) -> None:
        """Increment prompt usage count"""
        prompt = self.get_prompt_by_id(prompt_id)
        if prompt:
            prompt.increment_usage()
            if success:
                prompt.update_success_rate(True)
            self.db.commit()

    def get_featured_prompts(self, limit: int = 10) -> List[Prompt]:
        """Get featured prompts"""
        return self.db.query(Prompt)\
            .filter(Prompt.is_featured == True)\
            .filter(Prompt.status == PromptStatus.ACTIVE)\
            .filter(Prompt.is_public == True)\
            .order_by(desc(Prompt.usage_count))\
            .limit(limit)\
            .all()

    def search_prompts_by_language(self, language: str, limit: int = 20) -> List[Prompt]:
        """Search prompts that support a specific language"""
        return self.db.query(Prompt)\
            .filter(Prompt.supported_languages.contains(language))\
            .filter(Prompt.status == PromptStatus.ACTIVE)\
            .filter(Prompt.is_public == True)\
            .order_by(desc(Prompt.usage_count))\
            .limit(limit)\
            .all()

    def get_user_prompts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Prompt]:
        """Get prompts created by a specific user"""
        return self.db.query(Prompt)\
            .filter(Prompt.author_id == user_id)\
            .order_by(desc(Prompt.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def _validate_prompt_data(self, data: Dict[str, Any], is_update: bool = False) -> None:
        """Validate prompt data"""
        required_fields = ['name', 'category', 'system_prompt', 'user_prompt_template']

        if not is_update:
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Field '{field}' is required")

        # Validate temperature range
        if 'temperature' in data:
            temp = data['temperature']
            if not (0.0 <= temp <= 2.0):
                raise ValidationError("Temperature must be between 0.0 and 2.0")

        # Validate max_tokens
        if 'max_tokens' in data:
            tokens = data['max_tokens']
            if not (1 <= tokens <= 100000):
                raise ValidationError("Max tokens must be between 1 and 100000")

        # Validate model name
        if 'model_name' in data:
            valid_models = ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo']
            if data['model_name'] not in valid_models:
                raise ValidationError(f"Invalid model name. Valid models: {valid_models}")