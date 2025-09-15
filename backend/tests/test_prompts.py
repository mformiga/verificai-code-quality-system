"""
Prompt management tests for VerificAI Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestPrompts:
    """Prompt management test suite"""

    def test_create_prompt(self, client: TestClient, auth_headers):
        """Test creating a new prompt"""
        prompt_data = {
            "name": "Test Prompt",
            "description": "A test prompt",
            "category": "code_review",
            "system_prompt": "You are a code review assistant.",
            "user_prompt_template": "Review this code: {code}",
            "temperature": 0.1,
            "max_tokens": 1000,
            "tags": ["test", "code-review"],
            "supported_languages": ["python", "javascript"],
            "supported_file_types": [".py", ".js"]
        }

        response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == prompt_data["name"]
        assert data["category"] == prompt_data["category"]
        assert data["author_id"] > 0
        assert data["status"] == "draft"

    def test_create_prompt_minimal(self, client: TestClient, auth_headers):
        """Test creating a prompt with minimal data"""
        prompt_data = {
            "name": "Minimal Prompt",
            "category": "code_review",
            "system_prompt": "You are a code reviewer.",
            "user_prompt_template": "Review: {code}"
        }

        response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == prompt_data["name"]
        assert data["temperature"] == 0.1  # Default value

    def test_create_prompt_unauthorized(self, client: TestClient):
        """Test creating prompt without authentication"""
        prompt_data = {
            "name": "Unauthorized Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }

        response = client.post("/api/v1/prompts/", json=prompt_data)
        assert response.status_code == 403

    def test_list_prompts(self, client: TestClient, auth_headers):
        """Test listing prompts"""
        # Create a prompt first
        prompt_data = {
            "name": "List Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)

        # List prompts
        response = client.get("/api/v1/prompts/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    def test_list_prompts_with_filters(self, client: TestClient, auth_headers):
        """Test listing prompts with filters"""
        # Create prompts with different categories
        prompts = [
            {
                "name": "Code Review Prompt",
                "category": "code_review",
                "system_prompt": "Code review",
                "user_prompt_template": "Review: {code}"
            },
            {
                "name": "Security Prompt",
                "category": "security",
                "system_prompt": "Security",
                "user_prompt_template": "Analyze: {code}"
            }
        ]

        for prompt in prompts:
            client.post("/api/v1/prompts/", json=prompt, headers=auth_headers)

        # Filter by category
        response = client.get("/api/v1/prompts/?category=code_review", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        # All items should have the specified category
        for item in data["items"]:
            assert item["category"] == "code_review"

    def test_get_prompt_by_id(self, client: TestClient, auth_headers):
        """Test getting prompt by ID"""
        # Create a prompt first
        prompt_data = {
            "name": "Get Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Get prompt by ID
        response = client.get(f"/api/v1/prompts/{prompt_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == prompt_data["name"]
        assert data["id"] == prompt_id

    def test_get_nonexistent_prompt(self, client: TestClient, auth_headers):
        """Test getting nonexistent prompt"""
        response = client.get("/api/v1/prompts/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_prompt(self, client: TestClient, auth_headers):
        """Test updating prompt"""
        # Create a prompt first
        prompt_data = {
            "name": "Update Test Prompt",
            "category": "code_review",
            "system_prompt": "Original",
            "user_prompt_template": "Original: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Update prompt
        update_data = {
            "name": "Updated Prompt",
            "description": "Updated description"
        }
        response = client.put(f"/api/v1/prompts/{prompt_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_other_user_prompt(self, client: TestClient, auth_headers):
        """Test updating another user's prompt (should fail)"""
        # Create another user
        other_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "OtherPassword123!",
            "confirm_password": "OtherPassword123!"
        }
        client.post("/api/v1/auth/register", json=other_user_data)

        # Login as other user
        login_data = {"username": "otheruser", "password": "OtherPassword123!"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Create prompt as other user
        prompt_data = {
            "name": "Other User's Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=other_headers)
        prompt_id = create_response.json()["id"]

        # Try to update as original user
        update_data = {"name": "Hacked Prompt"}
        response = client.put(f"/api/v1/prompts/{prompt_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 403

    def test_delete_prompt(self, client: TestClient, auth_headers):
        """Test deleting prompt"""
        # Create a prompt first
        prompt_data = {
            "name": "Delete Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Delete prompt
        response = client.delete(f"/api/v1/prompts/{prompt_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "Prompt deleted successfully" in response.json()["message"]

        # Verify prompt is deleted
        get_response = client.get(f"/api/v1/prompts/{prompt_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_test_prompt(self, client: TestClient, auth_headers):
        """Test testing prompt"""
        # Create a prompt first
        prompt_data = {
            "name": "Test Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Test prompt
        test_data = {
            "code_content": "def hello():\n    print('Hello, World!')",
            "language": "python"
        }
        response = client.post(f"/api/v1/prompts/{prompt_id}/test", json=test_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data

    def test_clone_prompt(self, client: TestClient, auth_headers):
        """Test cloning prompt"""
        # Create a prompt first
        prompt_data = {
            "name": "Original Prompt",
            "category": "code_review",
            "system_prompt": "Original",
            "user_prompt_template": "Original: {code}",
            "tags": ["original"]
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Clone prompt
        clone_data = {"new_name": "Cloned Prompt"}
        response = client.post(f"/api/v1/prompts/{prompt_id}/clone", json=clone_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == clone_data["new_name"]
        assert data["category"] == prompt_data["category"]
        assert data["tags"] == prompt_data["tags"]

    def test_publish_prompt(self, client: TestClient, auth_headers):
        """Test publishing prompt"""
        # Create a prompt first
        prompt_data = {
            "name": "Publish Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Publish prompt
        response = client.post(f"/api/v1/prompts/{prompt_id}/publish", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is True
        assert data["status"] == "active"

    def test_unpublish_prompt(self, client: TestClient, auth_headers):
        """Test unpublishing prompt"""
        # Create and publish a prompt first
        prompt_data = {
            "name": "Unpublish Test Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}"
        }
        create_response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        prompt_id = create_response.json()["id"]

        # Publish first
        client.post(f"/api/v1/prompts/{prompt_id}/publish", headers=auth_headers)

        # Unpublish prompt
        response = client.post(f"/api/v1/prompts/{prompt_id}/unpublish", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is False

    def test_get_prompt_categories(self, client: TestClient, auth_headers):
        """Test getting prompt categories"""
        response = client.get("/api/v1/prompts/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "code_review" in data
        assert "security" in data

    def test_get_prompt_statuses(self, client: TestClient, auth_headers):
        """Test getting prompt statuses"""
        response = client.get("/api/v1/prompts/statuses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "draft" in data
        assert "active" in data

    @pytest.mark.unit
    def test_prompt_validation_invalid_temperature(self, client: TestClient, auth_headers):
        """Test prompt validation with invalid temperature"""
        prompt_data = {
            "name": "Invalid Temp Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}",
            "temperature": 3.0  # Invalid: should be 0.0-2.0
        }

        response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_prompt_validation_invalid_tokens(self, client: TestClient, auth_headers):
        """Test prompt validation with invalid max tokens"""
        prompt_data = {
            "name": "Invalid Tokens Prompt",
            "category": "code_review",
            "system_prompt": "Test",
            "user_prompt_template": "Test: {code}",
            "max_tokens": 0  # Invalid: should be >= 1
        }

        response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        assert response.status_code == 422