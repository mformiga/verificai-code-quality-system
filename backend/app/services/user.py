"""
User service for VerificAI Backend
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User, UserRole
from app.core.security import generate_secure_token, hash_api_key
from app.core.exceptions import (
    NotFoundError, ValidationError, BusinessRuleError,
    DuplicateResourceError
)


class UserService:
    """Service for user management operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        # Check if username already exists
        if self.db.query(User).filter(User.username == user_data['username']).first():
            raise DuplicateResourceError("User", user_data['username'])

        # Check if email already exists
        if self.db.query(User).filter(User.email == user_data['email']).first():
            raise DuplicateResourceError("User", user_data['email'])

        # Validate password strength
        password = user_data.pop('password', None)
        if password:
            from app.core.security import validate_password_strength
            is_valid, message = validate_password_strength(password)
            if not is_valid:
                raise ValidationError(message)

        # Create user
        user = User(**user_data)
        if password:
            user.set_password(password)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get users with filtering and pagination"""
        query = self.db.query(User)

        # Apply filters
        if filters:
            if filters.get('role'):
                query = query.filter(User.role == filters['role'])
            if filters.get('is_active') is not None:
                query = query.filter(User.is_active == filters['is_active'])
            if filters.get('is_verified') is not None:
                query = query.filter(User.is_verified == filters['is_verified'])

        # Apply search
        if search:
            query = query.filter(
                or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    User.full_name.contains(search)
                )
            )

        return query.offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Check email uniqueness if updating email
        if 'email' in user_data and user_data['email'] != user.email:
            if self.db.query(User).filter(User.email == user_data['email']).first():
                raise DuplicateResourceError("User", user_data['email'])

        # Update fields
        for field, value in user_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        self.db.delete(user)
        self.db.commit()

        return True

    def activate_user(self, user_id: int) -> User:
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.is_active = True
        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)

        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Verify current password
        if not user.verify_password(current_password):
            raise ValidationError("Current password is incorrect")

        # Validate new password
        from app.core.security import validate_password_strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(message)

        # Change password
        user.set_password(new_password)
        self.db.commit()

        return True

    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (admin only)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Validate new password
        from app.core.security import validate_password_strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(message)

        # Reset password
        user.set_password(new_password)
        user.reset_failed_attempts()
        user.unlock_account()
        self.db.commit()

        return True

    def create_api_key(self, user_id: int, name: str, expires_in_days: Optional[int] = None) -> Dict[str, Any]:
        """Create API key for user"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        api_key, api_key_hash = hash_api_key(generate_secure_token(64))

        user.api_key_hash = api_key_hash
        user.api_key_created_at = datetime.utcnow()

        self.db.commit()

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        return {
            "api_key": api_key,
            "api_key_hash": api_key_hash,
            "created_at": user.api_key_created_at,
            "expires_at": expires_at
        }

    def revoke_api_key(self, user_id: int) -> bool:
        """Revoke user's API key"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.api_key_hash = None
        user.api_key_created_at = None
        self.db.commit()

        return True

    def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify API key and return user"""
        api_key_hash = hash_api_key(api_key)
        user = self.db.query(User).filter(User.api_key_hash == api_key_hash).first()

        if user and user.is_active:
            return user

        return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if not user:
            return None

        # Check if account is locked
        if user.is_locked():
            return None

        # Verify password
        if not user.verify_password(password):
            user.increment_failed_attempts()
            self.db.commit()
            return None

        # Check if user is active
        if not user.is_active:
            return None

        # Reset failed attempts and update last login
        user.reset_failed_attempts()
        user.update_last_login()
        self.db.commit()

        return user

    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()

        # Users by role
        users_by_role = {}
        for role in UserRole:
            count = self.db.query(User).filter(User.role == role).count()
            users_by_role[role.value] = count

        # Recent users
        today = datetime.utcnow().date()
        new_users_today = self.db.query(User).filter(User.created_at >= today).count()

        week_ago = today - timedelta(days=7)
        new_users_week = self.db.query(User).filter(User.created_at >= week_ago).count()

        month_ago = today - timedelta(days=30)
        new_users_month = self.db.query(User).filter(User.created_at >= month_ago).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "users_by_role": users_by_role,
            "new_users_today": new_users_today,
            "new_users_week": new_users_week,
            "new_users_month": new_users_month
        }

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> User:
        """Update user preferences"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Update preference fields
        if 'preferred_language' in preferences:
            user.preferred_language = preferences['preferred_language']
        if 'timezone' in preferences:
            user.timezone = preferences['timezone']
        if 'email_notifications' in preferences:
            user.email_notifications = preferences['email_notifications']
        if 'email_analysis_reports' in preferences:
            user.email_analysis_reports = preferences['email_analysis_reports']
        if 'email_security_alerts' in preferences:
            user.email_security_alerts = preferences['email_security_alerts']

        self.db.commit()
        self.db.refresh(user)

        return user

    def lock_user_account(self, user_id: int, minutes: int = 30) -> User:
        """Lock user account for specified minutes"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.lock_account(minutes)
        self.db.commit()
        self.db.refresh(user)

        return user

    def unlock_user_account(self, user_id: int) -> User:
        """Unlock user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.unlock_account()
        self.db.commit()
        self.db.refresh(user)

        return user