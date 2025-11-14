#!/usr/bin/env python3
"""
Simple test to verify file paths and API structure
"""

import requests
from pathlib import Path

def test_upload_system():
    """Test the upload system with actual files"""

    base_path = Path("/c/Users/formi/Desktop/teste_olivia")

    # Find test files
    test_files = []
    for ext in ["*.js", "*.ts", "*.jsx", "*.tsx", "*.py", "*.java"]:
        for file_path in base_path.rglob(ext):
            if file_path.is_file() and len(test_files) < 3:
                relative_path = file_path.relative_to(base_path)
                test_files.append({
                    "file_name": file_path.name,
                    "full_path": str(file_path),
                    "folder_path": str(relative_path.parent).replace("\\", "/"),
                    "file_extension": file_path.suffix[1:] if file_path.suffix else "",
                    "file_size": file_path.stat().st_size,
                    "access_level": "read",
                    "is_processed": False
                })

    print(f"Found {len(test_files)} test files:")
    for i, tf in enumerate(test_files, 1):
        print(f"  {i}. {tf['file_name']}")
        print(f"     Extension: {tf['file_extension']}")
        print(f"     Size: {tf['file_size']} bytes")
        print(f"     Full path: {tf['full_path']}")
        print(f"     Folder: {tf['folder_path']}")
        print()

    # Check if backend is responding
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Backend health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Backend connection error: {e}")
        return

    # Test the file paths endpoint structure
    try:
        url = "http://localhost:8000/api/v1/file-paths/test"
        response = requests.get(url, timeout=5)
        print(f"File paths test endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"File paths endpoint error: {e}")

if __name__ == "__main__":
    test_upload_system()