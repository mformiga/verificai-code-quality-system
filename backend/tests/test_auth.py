"""
Authentication tests for VerificAI Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAuth:
    """Authentication test suite"""

    def test_register_user(self, client: TestClient):
        """Test user registration"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username"""
        user_data = {
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }

        # First registration
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Second registration with same username
        user_data["email"] = "user2@example.com"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email"""
        user_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }

        # First registration
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Second registration with same email
        user_data["username"] = "user2"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        user_data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak",
            "confirm_password": "weak"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_password_mismatch(self, client: TestClient):
        """Test registration with password mismatch"""
        user_data = {
            "username": "mismatchuser",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_login_success(self, client: TestClient):
        """Test successful login"""
        # Register user first
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "LoginPassword123!",
            "confirm_password": "LoginPassword123!"
        }
        client.post("/api/v1/auth/register", json=user_data)

        # Login
        login_data = {
            "username": "loginuser",
            "password": "LoginPassword123!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "WrongPassword123!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_json_success(self, client: TestClient):
        """Test successful login with JSON payload"""
        # Register user first
        user_data = {
            "username": "jsonuser",
            "email": "json@example.com",
            "password": "JsonPassword123!",
            "confirm_password": "JsonPassword123!"
        }
        client.post("/api/v1/auth/register", json=user_data)

        # Login with JSON
        login_data = {
            "username": "jsonuser",
            "password": "JsonPassword123!"
        }
        response = client.post("/api/v1/auth/login/json", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting current user profile"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "id" in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_refresh_token(self, client: TestClient, auth_headers):
        """Test token refresh"""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout(self, client: TestClient, auth_headers):
        """Test logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.unit
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data

    @pytest.mark.unit
    def test_ready_check(self, client: TestClient):
        """Test readiness check endpoint"""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data

    @pytest.mark.unit
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        assert data["status"] == "operational"