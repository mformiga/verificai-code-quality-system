"""
User management tests for VerificAI Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestUsers:
    """User management test suite"""

    def test_get_current_user_profile(self, client: TestClient, auth_headers):
        """Test getting current user profile"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "is_active" in data

    def test_update_current_user(self, client: TestClient, auth_headers):
        """Test updating current user"""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
            "preferred_language": "pt"
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]
        assert data["preferred_language"] == update_data["preferred_language"]

    def test_update_current_user_password(self, client: TestClient, auth_headers):
        """Test updating current user password"""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword456!",
            "confirm_password": "NewPassword456!"
        }
        response = client.put("/api/v1/users/me/password", json=password_data, headers=auth_headers)
        assert response.status_code == 200
        assert "Password updated successfully" in response.json()["message"]

    def test_update_password_wrong_current(self, client: TestClient, auth_headers):
        """Test updating password with wrong current password"""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
            "confirm_password": "NewPassword456!"
        }
        response = client.put("/api/v1/users/me/password", json=password_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_get_user_preferences(self, client: TestClient, auth_headers):
        """Test getting user preferences"""
        response = client.get("/api/v1/users/me/preferences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert "timezone" in data
        assert "email_notifications" in data

    def test_update_user_preferences(self, client: TestClient, auth_headers):
        """Test updating user preferences"""
        preferences_data = {
            "language": "pt",
            "timezone": "America/Sao_Paulo",
            "email_notifications": False
        }
        response = client.put("/api/v1/users/me/preferences", json=preferences_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == preferences_data["language"]
        assert data["timezone"] == preferences_data["timezone"]
        assert data["email_notifications"] == preferences_data["email_notifications"]

    def test_create_api_key(self, client: TestClient, auth_headers):
        """Test creating API key"""
        key_data = {
            "name": "Test API Key",
            "expires_in_days": 30
        }
        response = client.post("/api/v1/users/me/api-key", json=key_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == key_data["name"]
        assert "api_key" in data
        assert data["is_active"] is True

    def test_revoke_api_key(self, client: TestClient, auth_headers):
        """Test revoking API key"""
        # Create API key first
        key_data = {"name": "Test API Key"}
        client.post("/api/v1/users/me/api-key", json=key_data, headers=auth_headers)

        # Revoke API key
        response = client.delete("/api/v1/users/me/api-key", headers=auth_headers)
        assert response.status_code == 200
        assert "API key revoked successfully" in response.json()["message"]

    @pytest.mark.admin
    def test_list_users_as_admin(self, client: TestClient, admin_auth_headers):
        """Test listing users as admin"""
        response = client.get("/api/v1/users/", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_users_as_regular_user(self, client: TestClient, auth_headers):
        """Test listing users as regular user (should fail)"""
        response = client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.admin
    def test_get_user_by_id_as_admin(self, client: TestClient, admin_auth_headers):
        """Test getting user by ID as admin"""
        # Create a user first
        user_data = {
            "username": "targetuser",
            "email": "target@example.com",
            "password": "TargetPassword123!",
            "confirm_password": "TargetPassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Get user by ID
        response = client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]

    def test_get_other_user_as_regular_user(self, client: TestClient, auth_headers):
        """Test getting another user as regular user (should fail)"""
        # Create another user
        user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "OtherPassword123!",
            "confirm_password": "OtherPassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Try to get other user
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.admin
    def test_update_user_as_admin(self, client: TestClient, admin_auth_headers):
        """Test updating user as admin"""
        # Create a user first
        user_data = {
            "username": "updateuser",
            "email": "update@example.com",
            "password": "UpdatePassword123!",
            "confirm_password": "UpdatePassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Update user
        update_data = {"full_name": "Admin Updated Name"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]

    @pytest.mark.admin
    def test_delete_user_as_admin(self, client: TestClient, admin_auth_headers):
        """Test deleting user as admin"""
        # Create a user first
        user_data = {
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "DeletePassword123!",
            "confirm_password": "DeletePassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Delete user
        response = client.delete(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert "User deleted successfully" in response.json()["message"]

    @pytest.mark.admin
    def test_activate_user_as_admin(self, client: TestClient, admin_auth_headers):
        """Test activating user as admin"""
        # Create an inactive user
        user_data = {
            "username": "inactiveuser",
            "email": "inactive@example.com",
            "password": "InactivePassword123!",
            "confirm_password": "InactivePassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Deactivate user first
        client.post(f"/api/v1/users/{user_id}/deactivate", headers=admin_auth_headers)

        # Activate user
        response = client.post(f"/api/v1/users/{user_id}/activate", headers=admin_auth_headers)
        assert response.status_code == 200
        assert "User activated successfully" in response.json()["message"]

    @pytest.mark.admin
    def test_deactivate_user_as_admin(self, client: TestClient, admin_auth_headers):
        """Test deactivating user as admin"""
        # Create a user first
        user_data = {
            "username": "deactivateuser",
            "email": "deactivate@example.com",
            "password": "DeactivatePassword123!",
            "confirm_password": "DeactivatePassword123!"
        }
        create_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = create_response.json()["id"]

        # Deactivate user
        response = client.post(f"/api/v1/users/{user_id}/deactivate", headers=admin_auth_headers)
        assert response.status_code == 200
        assert "User deactivated successfully" in response.json()["message"]

    @pytest.mark.admin
    def test_get_user_stats_as_admin(self, client: TestClient, admin_auth_headers):
        """Test getting user statistics as admin"""
        response = client.get("/api/v1/users/stats", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "users_by_role" in data

    def test_get_user_stats_as_regular_user(self, client: TestClient, auth_headers):
        """Test getting user statistics as regular user (should fail)"""
        response = client.get("/api/v1/users/stats", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.unit
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to protected endpoints"""
        endpoints = [
            "/api/v1/users/me",
            "/api/v1/users/me/preferences",
            "/api/v1/users/me/api-key",
            "/api/v1/users/",
            "/api/v1/users/stats"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403