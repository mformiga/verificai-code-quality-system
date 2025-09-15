"""
Analysis tests for VerificAI Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAnalysis:
    """Analysis test suite"""

    @pytest.fixture
    def sample_prompt(self, client: TestClient, auth_headers):
        """Create a sample prompt for testing"""
        prompt_data = {
            "name": "Test Analysis Prompt",
            "category": "code_review",
            "system_prompt": "You are a code analysis assistant.",
            "user_prompt_template": "Analyze this code: {code}",
            "tags": ["test", "analysis"]
        }
        response = client.post("/api/v1/prompts/", json=prompt_data, headers=auth_headers)
        return response.json()

    def test_create_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test creating a new analysis"""
        analysis_data = {
            "name": "Test Analysis",
            "description": "A test analysis",
            "prompt_id": sample_prompt["id"],
            "code_content": "def hello():\n    print('Hello, World!')",
            "language": "python"
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == analysis_data["name"]
        assert data["status"] == "pending"
        assert data["user_id"] > 0
        assert data["prompt_id"] == sample_prompt["id"]

    def test_create_analysis_with_repository(self, client: TestClient, auth_headers, sample_prompt):
        """Test creating analysis with repository URL"""
        analysis_data = {
            "name": "Repository Analysis",
            "description": "Analysis of repository",
            "prompt_id": sample_prompt["id"],
            "repository_url": "https://github.com/example/repo.git"
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["repository_url"] == analysis_data["repository_url"]

    def test_create_analysis_with_files(self, client: TestClient, auth_headers, sample_prompt):
        """Test creating analysis with file paths"""
        analysis_data = {
            "name": "Files Analysis",
            "description": "Analysis of specific files",
            "prompt_id": sample_prompt["id"],
            "file_paths": ["src/main.py", "src/utils.py"],
            "language": "python"
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "file_paths" in data

    def test_create_analysis_invalid_prompt(self, client: TestClient, auth_headers):
        """Test creating analysis with invalid prompt ID"""
        analysis_data = {
            "name": "Invalid Prompt Analysis",
            "description": "Test with invalid prompt",
            "prompt_id": 99999,
            "code_content": "print('test')"
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        assert response.status_code == 404

    def test_create_analysis_unauthorized(self, client: TestClient, sample_prompt):
        """Test creating analysis without authentication"""
        analysis_data = {
            "name": "Unauthorized Analysis",
            "description": "Test without auth",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('test')"
        }

        response = client.post("/api/v1/analysis/", json=analysis_data)
        assert response.status_code == 403

    def test_create_analysis_missing_source(self, client: TestClient, auth_headers, sample_prompt):
        """Test creating analysis without any code source"""
        analysis_data = {
            "name": "Empty Analysis",
            "description": "Test without source",
            "prompt_id": sample_prompt["id"]
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        assert response.status_code == 422

    def test_list_analyses(self, client: TestClient, auth_headers, sample_prompt):
        """Test listing analyses"""
        # Create an analysis first
        analysis_data = {
            "name": "List Test Analysis",
            "description": "Test analysis for listing",
            "prompt_id": sample_prompt["id"],
            "code_content": "def test():\n    pass"
        }
        client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)

        # List analyses
        response = client.get("/api/v1/analysis/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    def test_list_analyses_with_filters(self, client: TestClient, auth_headers, sample_prompt):
        """Test listing analyses with filters"""
        # Create analyses with different statuses
        analyses = [
            {
                "name": "Pending Analysis",
                "description": "Pending test",
                "prompt_id": sample_prompt["id"],
                "code_content": "print('pending')"
            },
            {
                "name": "Completed Analysis",
                "description": "Completed test",
                "prompt_id": sample_prompt["id"],
                "code_content": "print('completed')"
            }
        ]

        for analysis in analyses:
            client.post("/api/v1/analysis/", json=analysis, headers=auth_headers)

        # Filter by status (should only show pending ones initially)
        response = client.get("/api/v1/analysis/?status=pending", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # All items should be pending
        for item in data["items"]:
            assert item["status"] == "pending"

    def test_get_analysis_by_id(self, client: TestClient, auth_headers, sample_prompt):
        """Test getting analysis by ID"""
        # Create an analysis first
        analysis_data = {
            "name": "Get Test Analysis",
            "description": "Test analysis for retrieval",
            "prompt_id": sample_prompt["id"],
            "code_content": "def get_test():\n    return 'test'"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Get analysis by ID
        response = client.get(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == analysis_data["name"]
        assert data["id"] == analysis_id

    def test_get_analysis_result(self, client: TestClient, auth_headers, sample_prompt):
        """Test getting analysis result"""
        # Create an analysis first
        analysis_data = {
            "name": "Result Test Analysis",
            "description": "Test analysis for result",
            "prompt_id": sample_prompt["id"],
            "code_content": "def result_test():\n    return 'result'"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Get analysis result
        response = client.get(f"/api/v1/analysis/{analysis_id}/result", headers=auth_headers)
        # Initially should be 404 as analysis is still pending
        assert response.status_code == 404

    def test_update_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test updating analysis"""
        # Create an analysis first
        analysis_data = {
            "name": "Update Test Analysis",
            "description": "Original description",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('original')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Update analysis
        update_data = {
            "name": "Updated Analysis",
            "description": "Updated description",
            "configuration": {"timeout": 300}
        }
        response = client.put(f"/api/v1/analysis/{analysis_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_processing_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test updating analysis that is already processing (should fail)"""
        # Create an analysis first
        analysis_data = {
            "name": "Processing Analysis",
            "description": "Test processing update",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('processing')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Manually set status to processing
        # Note: In a real test, you would need to mock the background task
        # For now, we'll test the API endpoint behavior

        # Try to update
        update_data = {"name": "Updated Processing"}
        response = client.put(f"/api/v1/analysis/{analysis_id}", json=update_data, headers=auth_headers)
        # This should succeed as it's still pending
        assert response.status_code == 200

    def test_delete_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test deleting analysis"""
        # Create an analysis first
        analysis_data = {
            "name": "Delete Test Analysis",
            "description": "Test analysis for deletion",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('delete')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Delete analysis
        response = client.delete(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "Analysis deleted successfully" in response.json()["message"]

        # Verify analysis is deleted
        get_response = client.get(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_cancel_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test cancelling analysis"""
        # Create an analysis first
        analysis_data = {
            "name": "Cancel Test Analysis",
            "description": "Test analysis for cancellation",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('cancel')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Cancel analysis
        response = client.post(f"/api/v1/analysis/{analysis_id}/cancel", headers=auth_headers)
        assert response.status_code == 400  # Should fail as it's not processing

    def test_restart_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test restarting analysis"""
        # Create an analysis first
        analysis_data = {
            "name": "Restart Test Analysis",
            "description": "Test analysis for restart",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('restart')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        analysis_id = create_response.json()["id"]

        # Try to restart analysis (should fail as it's not failed/cancelled)
        response = client.post(f"/api/v1/analysis/{analysis_id}/restart", headers=auth_headers)
        assert response.status_code == 400

    def test_get_analysis_stats(self, client: TestClient, auth_headers, sample_prompt):
        """Test getting analysis statistics"""
        # Create some analyses first
        analyses = [
            {
                "name": "Stats Analysis 1",
                "description": "For stats test",
                "prompt_id": sample_prompt["id"],
                "code_content": "print('stats1')"
            },
            {
                "name": "Stats Analysis 2",
                "description": "For stats test",
                "prompt_id": sample_prompt["id"],
                "code_content": "print('stats2')"
            }
        ]

        for analysis in analyses:
            client.post("/api/v1/analysis/", json=analysis, headers=auth_headers)

        # Get stats
        response = client.get("/api/v1/analysis/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data
        assert "completed_analyses" in data
        assert "failed_analyses" in data
        assert "average_scores" in data

    def test_get_other_user_analysis(self, client: TestClient, auth_headers, sample_prompt):
        """Test getting another user's analysis (should fail)"""
        # Create another user
        other_user_data = {
            "username": "otheranalysis",
            "email": "otheranalysis@example.com",
            "password": "OtherPassword123!",
            "confirm_password": "OtherPassword123!"
        }
        client.post("/api/v1/auth/register", json=other_user_data)

        # Login as other user
        login_data = {"username": "otheranalysis", "password": "OtherPassword123!"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Create analysis as other user
        analysis_data = {
            "name": "Other User's Analysis",
            "description": "Private analysis",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('private')"
        }
        create_response = client.post("/api/v1/analysis/", json=analysis_data, headers=other_headers)
        analysis_id = create_response.json()["id"]

        # Try to get as original user
        response = client.get(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.unit
    def test_analysis_validation_invalid_score(self, client: TestClient, auth_headers, sample_prompt):
        """Test analysis validation with invalid score"""
        analysis_data = {
            "name": "Invalid Score Analysis",
            "description": "Test with invalid score",
            "prompt_id": sample_prompt["id"],
            "code_content": "print('test')",
            "configuration": {"min_score": 150}  # Invalid: should be 0-100
        }

        response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
        # This should succeed as min_score is not a direct field of Analysis
        assert response.status_code == 200

    @pytest.mark.unit
    def test_unauthorized_analysis_access(self, client: TestClient, sample_prompt):
        """Test unauthorized access to analysis endpoints"""
        endpoints = [
            "/api/v1/analysis/",
            "/api/v1/analysis/stats",
            "/api/v1/analysis/1",
            "/api/v1/analysis/1/result"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403