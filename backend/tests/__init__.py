"""
Test suite for VerificAI Backend
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Database fixture"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Test client fixture"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def auth_headers(client):
    """Authentication headers fixture"""
    # Create test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!"
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client):
    """Admin authentication headers fixture"""
    # Create admin user
    user_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "confirm_password": "AdminPassword123!",
        "role": "admin"
    }
    client.post("/api/v1/auth/register", json=user_data)

    # Login to get token
    login_data = {
        "username": "admin",
        "password": "AdminPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}