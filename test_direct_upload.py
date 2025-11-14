#!/usr/bin/env python3
"""
Direct test of upload system with specific files
"""

import os
from pathlib import Path

def test_specific_files():
    """Test with specific files we know exist"""

    # Files we know exist from the directory listing
    test_files = [
        {
            "file_name": ".eslintrc.js",
            "full_path": "/c/Users/formi/Desktop/teste_olivia/olivia-back/.eslintrc.js",
            "folder_path": "teste_olivia/olivia-back",
            "file_extension": "js",
            "file_size": 650,
            "access_level": "read",
            "is_processed": False
        },
        {
            "file_name": "package.json",
            "full_path": "/c/Users/formi/Desktop/teste_olivia/olivia-back/package.json",
            "folder_path": "teste_olivia/olivia-back",
            "file_extension": "json",
            "file_size": 3978,
            "access_level": "read",
            "is_processed": False
        }
    ]

    print("Testing upload system with specific files:")
    for i, tf in enumerate(test_files, 1):
        print(f"  {i}. {tf['file_name']}")
        print(f"     Path: {tf['full_path']}")
        print(f"     Exists: {os.path.exists(tf['full_path'])}")
        print(f"     Size: {tf['file_size']} bytes")
        print()

    # Now create the data structure exactly as the frontend would send it
    upload_data = {
        "file_paths": test_files
    }

    print("This is the data structure that will be sent to the API:")
    import json
    print(json.dumps(upload_data, indent=2))

if __name__ == "__main__":
    test_specific_files()