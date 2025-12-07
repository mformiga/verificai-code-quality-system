#!/usr/bin/env python3
"""
Check what's actually deployed at the URLs
"""
import requests
import time
from datetime import datetime

def check_url(url, name):
    """Check what's deployed at a URL"""
    print(f"\n=== Checking {name}: {url} ===")

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")

        # Look for key indicators in the content
        content = response.text.lower()

        if 'streamlit' in content:
            print("❌ STILL RUNNING STREAMLIT")
            if 'streamlit-error' in content:
                print("   Streamlit is showing an error page")

        if 'react' in content or 'vite' in content or '<div id="root">' in content:
            print("✅ RUNNING REACT APPLICATION")

        if 'aval ia' in content or '<title>' in content:
            # Try to extract title
            import re
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                print(f"Page Title: {title_match.group(1)}")

        # Show first few lines of response
        lines = response.text.split('\n')[:10]
        print("First few lines:")
        for i, line in enumerate(lines):
            if line.strip():
                print(f"  {i+1}: {line.strip()[:100]}")

        return response.status_code == 200

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Cannot reach the URL")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print(f"=== URL Status Check ===")
    print(f"Time: {datetime.now().isoformat()}")

    urls_to_check = [
        ("https://verificai-code-quality-system.onrender.com", "Frontend (should be React)"),
        ("https://avalia-backend.onrender.com", "Backend API"),
        ("https://avalia-backend.onrender.com/health", "Backend Health Check"),
        ("https://avalia-backend.onrender.com/api/v1", "Backend API v1"),
    ]

    results = {}

    for url, name in urls_to_check:
        results[url] = check_url(url, name)
        time.sleep(1)  # Wait between requests

    print(f"\n=== SUMMARY ===")
    for url, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"{status} {url}")

    # Additional checks
    print(f"\n=== ADDITIONAL CHECKS ===")

    # Check if backend is serving API
    try:
        response = requests.get("https://avalia-backend.onrender.com/api/v1/analysis", timeout=5)
        print(f"API Analysis Endpoint: {response.status_code}")
        if response.status_code == 401:
            print("✅ Backend is responding (401 = requires authentication, which is expected)")
        elif response.status_code == 404:
            print("⚠️  Backend exists but endpoint not found")
    except:
        print("❌ Cannot reach backend API")

if __name__ == "__main__":
    main()