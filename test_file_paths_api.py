#!/usr/bin/env python3
"""
Script to test the file-paths bulk API with file copying
"""

import requests
import json
from pathlib import Path

def test_file_paths_bulk():
    """Test the modified file-paths bulk API"""

    # Test data - simulate what frontend sends
    test_data = {
        "file_paths": [
            {
                "file_name": "test_upload.py",
                "full_path": str(Path("test_upload.py").absolute()),
                "folder_path": "backend",
                "file_extension": "py",
                "file_size": Path("test_upload.py").stat().st_size,
                "access_level": "read",
                "is_processed": False
            }
        ]
    }

    print("Testing file-paths bulk API...")
    print(f"Source file: {test_data['file_paths'][0]['full_path']}")
    print(f"File exists: {Path(test_data['file_paths'][0]['full_path']).exists()}")

    # Note: This would need authentication in real scenario
    url = "http://localhost:8000/api/v1/file-paths/bulk"

    try:
        # For testing purposes, let's see what would be sent
        print(f"POST {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")

        # In a real scenario, this would need auth headers
        # response = requests.post(url, json=test_data, headers={"Authorization": "Bearer token"})

        print("\nAPI should copy the file from source to uploads/")
        print("Check uploads folder after testing through frontend")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_file_paths_bulk()