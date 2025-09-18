"""
Service layer tests for VerificAI Backend
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.user import UserService
from app.services.prompt import PromptService
from app.services.analysis import AnalysisService
from app.models.user import User, UserRole
from app.models.prompt import Prompt, PromptCategory, PromptStatus


@pytest.fixture(scope="function")
def test_db():
    """Test database fixture"""
    engine = create_engine("postgresql://verificai:verificai123@localhost:5432/verificai_test_services")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestUserService:
    """User service test suite"""

    def test_create_user(self, test_db):
        """Test creating a user"""
        user_service = UserService(test_db)
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }

        user = user_service.create_user(user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.is_active is True
        assert user.role == UserRole.QA_ENGINEER
        assert user.verify_password(user_data["password"])

    def test_create_user_duplicate_username(self, test_db):
        """Test creating user with duplicate username"""
        user_service = UserService(test_db)

        # Create first user
        user_data = {
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "Password123!"
        }
        user_service.create_user(user_data)

        # Try to create second user with same username
        user_data["email"] = "user2@example.com"
        with pytest.raises(Exception):  # Should raise DuplicateResourceError
            user_service.create_user(user_data)

    def test_get_user_by_id(self, test_db):
        """Test getting user by ID"""
        user_service = UserService(test_db)
        user_data = {
            "username": "getuser",
            "email": "get@example.com",
            "password": "Password123!"
        }

        created_user = user_service.create_user(user_data)
        retrieved_user = user_service.get_user_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username

    def test_authenticate_user(self, test_db):
        """Test user authentication"""
        user_service = UserService(test_db)
        user_data = {
            "username": "authuser",
            "email": "auth@example.com",
            "password": "AuthPassword123!"
        }

        user_service.create_user(user_data)

        # Test successful authentication
        user = user_service.authenticate_user("authuser", "AuthPassword123!")
        assert user is not None
        assert user.username == "authuser"

        # Test failed authentication
        user = user_service.authenticate_user("authuser", "wrongpassword")
        assert user is None

    def test_change_password(self, test_db):
        """Test changing user password"""
        user_service = UserService(test_db)
        user_data = {
            "username": "passuser",
            "email": "pass@example.com",
            "password": "OldPassword123!"
        }

        user = user_service.create_user(user_data)

        # Change password
        success = user_service.change_password(
            user.id, "OldPassword123!", "NewPassword456!"
        )
        assert success is True

        # Verify new password works
        updated_user = user_service.get_user_by_id(user.id)
        assert updated_user.verify_password("NewPassword456!")

    def test_get_user_stats(self, test_db):
        """Test getting user statistics"""
        user_service = UserService(test_db)

        # Create some users
        users_data = [
            {"username": "user1", "email": "user1@example.com", "password": "Password123!"},
            {"username": "user2", "email": "user2@example.com", "password": "Password123!"},
            {"username": "admin", "email": "admin@example.com", "password": "AdminPassword123!", "role": UserRole.ADMIN}
        ]

        for user_data in users_data:
            user_service.create_user(user_data)

        stats = user_service.get_user_stats()
        assert stats["total_users"] == 3
        assert stats["active_users"] == 3
        assert "users_by_role" in stats
        assert stats["users_by_role"]["admin"] == 1


class TestPromptService:
    """Prompt service test suite"""

    @pytest.fixture
    def test_user(self, test_db):
        """Create a test user"""
        user_service = UserService(test_db)
        user_data = {
            "username": "promptuser",
            "email": "prompt@example.com",
            "password": "Password123!"
        }
        return user_service.create_user(user_data)

    def test_create_prompt(self, test_db, test_user):
        """Test creating a prompt"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Test Prompt",
            "description": "A test prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "You are a code reviewer.",
            "user_prompt_template": "Review this code: {code}",
            "temperature": 0.1,
            "max_tokens": 1000
        }

        prompt = prompt_service.create_prompt(test_user.id, prompt_data)
        assert prompt.name == prompt_data["name"]
        assert prompt.category == prompt_data["category"]
        assert prompt.author_id == test_user.id
        assert prompt.status == PromptStatus.DRAFT

    def test_get_prompt_by_id(self, test_db, test_user):
        """Test getting prompt by ID"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Get Prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }

        created_prompt = prompt_service.create_prompt(test_user.id, prompt_data)
        retrieved_prompt = prompt_service.get_prompt_by_id(created_prompt.id)

        assert retrieved_prompt is not None
        assert retrieved_prompt.id == created_prompt.id
        assert retrieved_prompt.name == created_prompt.name

    def test_update_prompt(self, test_db, test_user):
        """Test updating prompt"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Update Prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "Original",
            "user_prompt_template": "Original: {code}"
        }

        created_prompt = prompt_service.create_prompt(test_user.id, prompt_data)

        # Update prompt
        update_data = {"name": "Updated Prompt", "description": "Updated description"}
        updated_prompt = prompt_service.update_prompt(created_prompt.id, test_user.id, update_data)

        assert updated_prompt.name == update_data["name"]
        assert updated_prompt.description == update_data["description"]

    def test_clone_prompt(self, test_db, test_user):
        """Test cloning prompt"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Original Prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "Original",
            "user_prompt_template": "Original: {code}",
            "tags": ["original"]
        }

        created_prompt = prompt_service.create_prompt(test_user.id, prompt_data)

        # Clone prompt
        clone_data = {"new_name": "Cloned Prompt"}
        cloned_prompt = prompt_service.clone_prompt(created_prompt.id, test_user.id, clone_data)

        assert cloned_prompt.name == clone_data["new_name"]
        assert cloned_prompt.category == created_prompt.category
        assert cloned_prompt.author_id == test_user.id
        assert cloned_prompt.tags == created_prompt.tags

    def test_publish_prompt(self, test_db, test_user):
        """Test publishing prompt"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Publish Prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }

        created_prompt = prompt_service.create_prompt(test_user.id, prompt_data)

        # Publish prompt
        published_prompt = prompt_service.publish_prompt(created_prompt.id, test_user.id)

        assert published_prompt.is_public is True
        assert published_prompt.status == PromptStatus.ACTIVE

    def test_get_prompt_stats(self, test_db, test_user):
        """Test getting prompt statistics"""
        prompt_service = PromptService(test_db)

        # Create some prompts
        prompts_data = [
            {
                "name": "Prompt 1",
                "category": PromptCategory.CODE_REVIEW,
                "system_prompt": "Test 1",
                "user_prompt_template": "Test 1: {code}"
            },
            {
                "name": "Prompt 2",
                "category": PromptCategory.SECURITY,
                "system_prompt": "Test 2",
                "user_prompt_template": "Test 2: {code}"
            }
        ]

        for prompt_data in prompts_data:
            prompt_service.create_prompt(test_user.id, prompt_data)

        stats = prompt_service.get_prompt_stats(test_user.id)
        assert stats["total_prompts"] == 2
        assert "prompts_by_category" in stats
        assert "prompts_by_status" in stats


class TestAnalysisService:
    """Analysis service test suite"""

    @pytest.fixture
    def test_user(self, test_db):
        """Create a test user"""
        user_service = UserService(test_db)
        user_data = {
            "username": "analysisuser",
            "email": "analysis@example.com",
            "password": "Password123!"
        }
        return user_service.create_user(user_data)

    @pytest.fixture
    def test_prompt(self, test_db, test_user):
        """Create a test prompt"""
        prompt_service = PromptService(test_db)
        prompt_data = {
            "name": "Test Analysis Prompt",
            "category": PromptCategory.CODE_REVIEW,
            "system_prompt": "You are a code analysis assistant.",
            "user_prompt_template": "Analyze this code: {code}"
        }
        return prompt_service.create_prompt(test_user.id, prompt_data)

    def test_create_analysis(self, test_db, test_user, test_prompt):
        """Test creating an analysis"""
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Test Analysis",
            "description": "A test analysis",
            "prompt_id": test_prompt.id,
            "code_content": "def hello():\n    print('Hello, World!')",
            "language": "python"
        }

        analysis = analysis_service.create_analysis(test_user.id, analysis_data)
        assert analysis.name == analysis_data["name"]
        assert analysis.user_id == test_user.id
        assert analysis.prompt_id == test_prompt.id
        assert analysis.status.value == "pending"

    def test_get_analysis_by_id(self, test_db, test_user, test_prompt):
        """Test getting analysis by ID"""
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Get Analysis",
            "prompt_id": test_prompt.id,
            "code_content": "print('test')"
        }

        created_analysis = analysis_service.create_analysis(test_user.id, analysis_data)
        retrieved_analysis = analysis_service.get_analysis_by_id(created_analysis.id)

        assert retrieved_analysis is not None
        assert retrieved_analysis.id == created_analysis.id
        assert retrieved_analysis.name == created_analysis.name

    def test_start_analysis(self, test_db, test_user, test_prompt):
        """Test starting analysis"""
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Start Analysis",
            "prompt_id": test_prompt.id,
            "code_content": "print('start')"
        }

        created_analysis = analysis_service.create_analysis(test_user.id, analysis_data)

        # Start analysis
        started_analysis = analysis_service.start_analysis(created_analysis.id)

        assert started_analysis.status.value == "processing"
        assert started_analysis.started_at is not None

    def test_complete_analysis(self, test_db, test_user, test_prompt):
        """Test completing analysis"""
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Complete Analysis",
            "prompt_id": test_prompt.id,
            "code_content": "print('complete')"
        }

        created_analysis = analysis_service.create_analysis(test_user.id, analysis_data)
        analysis_service.start_analysis(created_analysis.id)

        # Complete analysis
        result_data = {
            "summary": "Analysis complete",
            "detailed_findings": "No issues found",
            "score": 90,
            "confidence": 0.95
        }
        completed_analysis = analysis_service.complete_analysis(created_analysis.id, result_data)

        assert completed_analysis.status.value == "completed"
        assert completed_analysis.completed_at is not None
        assert completed_analysis.result is not None
        assert completed_analysis.result.summary == result_data["summary"]

    def test_fail_analysis(self, test_db, test_user, test_prompt):
        """Test failing analysis"""
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Fail Analysis",
            "prompt_id": test_prompt.id,
            "code_content": "print('fail')"
        }

        created_analysis = analysis_service.create_analysis(test_user.id, analysis_data)
        analysis_service.start_analysis(created_analysis.id)

        # Fail analysis
        error_message = "Analysis failed due to error"
        failed_analysis = analysis_service.fail_analysis(created_analysis.id, error_message)

        assert failed_analysis.status.value == "failed"
        assert failed_analysis.error_message == error_message
        assert failed_analysis.completed_at is not None

    def test_get_analysis_stats(self, test_db, test_user, test_prompt):
        """Test getting analysis statistics"""
        analysis_service = AnalysisService(test_db)

        # Create some analyses
        analyses_data = [
            {
                "name": "Analysis 1",
                "prompt_id": test_prompt.id,
                "code_content": "print('test1')"
            },
            {
                "name": "Analysis 2",
                "prompt_id": test_prompt.id,
                "code_content": "print('test2')"
            }
        ]

        for analysis_data in analyses_data:
            analysis_service.create_analysis(test_user.id, analysis_data)

        stats = analysis_service.get_analysis_stats(test_user.id)
        assert stats["total_analyses"] == 2
        assert "analyses_by_status" in stats
        assert "average_scores" in stats

    @pytest.mark.unit
    def test_service_validation(self, test_db, test_user):
        """Test service validation"""
        # Test with invalid prompt ID
        analysis_service = AnalysisService(test_db)
        analysis_data = {
            "name": "Invalid Analysis",
            "prompt_id": 99999,
            "code_content": "print('test')"
        }

        with pytest.raises(Exception):  # Should raise NotFoundError
            analysis_service.create_analysis(test_user.id, analysis_data)