#!/usr/bin/env python3
"""
Simple URL status check
"""
import requests
import re

def check_url(url, name):
    """Check what's deployed at a URL"""
    print(f"\n=== Checking {name}: {url} ===")

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")

        content = response.text.lower()

        # Look for indicators
        if 'streamlit' in content:
            print("[X] STILL RUNNING STREAMLIT")
            if 'streamlit-error' in content:
                print("    Streamlit is showing an error page")

        if 'react' in content or 'vite' in content or '<div id="root">' in content:
            print("[✓] RUNNING REACT APPLICATION")

        # Try to extract title
        title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
        if title_match:
            print(f"Page Title: {title_match.group(1)}")

        # Show some content
        lines = response.text.split('\n')[:8]
        print("Content preview:")
        for i, line in enumerate(lines):
            if line.strip():
                print(f"  {i+1}: {line.strip()[:80]}")

        return response.status_code == 200

    except Exception as e:
        print(f"[X] ERROR: {e}")
        return False

def main():
    print("=== URL Status Check ===")

    urls = [
        ("https://verificai-code-quality-system.onrender.com", "Frontend"),
        ("https://avalia-backend.onrender.com", "Backend"),
        ("https://avalia-backend.onrender.com/health", "Backend Health"),
    ]

    for url, name in urls:
        check_url(url, name)
        print("-" * 60)

if __name__ == "__main__":
    main()