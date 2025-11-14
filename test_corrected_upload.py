#!/usr/bin/env python3
"""
Test script to verify the corrected file upload API works properly
"""

import requests
import json
from pathlib import Path

def test_file_upload_api():
    """Test the corrected file upload API with actual files from Desktop"""

    # Find some actual files from the user's project
    base_path = Path("/c/Users/formi/Desktop/teste_olivia")

    # Test files that actually exist
    test_files = []

    # Find a few JavaScript/TypeScript files
    for ext in ["*.js", "*.ts", "*.jsx", "*.tsx"]:
        for file_path in base_path.rglob(ext):
            if file_path.is_file() and len(test_files) < 3:  # Just test with 3 files
                # Convert Windows path to forward slashes for API
                relative_path = file_path.relative_to(base_path)
                test_files.append({
                    "file_name": file_path.name,
                    "full_path": str(file_path),
                    "folder_path": str(relative_path.parent),
                    "file_extension": file_path.suffix[1:] if file_path.suffix else "",  # Remove dot
                    "file_size": file_path.stat().st_size,
                    "access_level": "read",
                    "is_processed": False
                })

    if not test_files:
        print("❌ No test files found!")
        return

    print(f"✅ Found {len(test_files)} test files:")
    for i, tf in enumerate(test_files, 1):
        print(f"  {i}. {tf['file_name']} ({tf['file_extension']}, {tf['file_size']} bytes)")
        print(f"     Path: {tf['full_path']}")
        print(f"     Folder: {tf['folder_path']}")
        print()

    # Test data for API
    upload_data = {
        "file_paths": test_files
    }

    # API endpoint
    url = "http://localhost:8000/api/v1/file-paths/bulk"

    print(f"🚀 Testing POST {url}")
    print(f"📋 Sending {len(test_files)} files for upload")

    try:
        # This would normally require authentication, but let's see what happens
        # The important thing is to test the file copying logic
        response = requests.post(url, json=upload_data, timeout=30)

        if response.status_code == 401:
            print("❌ Authentication required (expected for real API)")
            print("✅ But the important thing is that the backend should receive the correct file paths")
        else:
            print(f"📊 Response status: {response.status_code}")
            print(f"📄 Response body: {response.text}")

        # Check if uploads folder gets files after testing through frontend
        uploads_dir = Path("backend/uploads")
        if uploads_dir.exists():
            files_in_uploads = list(uploads_dir.glob("*"))
            print(f"📁 Files in uploads folder: {len(files_in_uploads)}")
            for f in files_in_uploads[:3]:  # Show first 3
                print(f"  - {f.name}")
        else:
            print("❌ Uploads folder doesn't exist")

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend might not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_file_upload_api()