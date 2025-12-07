#!/usr/bin/env python3
"""
Simple test script to verify AVALIA application deployment status
"""

import requests
import json
import time
from datetime import datetime

def test_frontend_access():
    """Test if frontend is accessible"""
    print("Testing frontend access...")
    frontend_urls = [
        "https://avalia-app.onrender.com",
        "https://avalia-app.onrender.com/",
    ]

    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"SUCCESS: Frontend accessible at: {url}")
                print(f"   Status Code: {response.status_code}")

                # Check for demo mode message
                content = response.text.lower()
                if "rodando em modo demo" in content:
                    print("WARNING: 'Rodando em modo demo' message found!")
                    return False
                elif "avalia" in content:
                    print("SUCCESS: AVALIA branding found in content")
                    return True
                else:
                    print("WARNING: AVALIA branding not found")
                    return False
            else:
                print(f"ERROR: Frontend returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to access {url}: {str(e)}")

    return False

def test_backend_access():
    """Test if backend API is accessible"""
    print("\nTesting backend access...")
    backend_urls = [
        "https://avalia-backend.onrender.com/health",
        "https://avalia-backend.onrender.com/api/v1/general-analysis/criteria-working"
    ]

    for url in backend_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"SUCCESS: Backend endpoint accessible: {url}")
                return True
            else:
                print(f"ERROR: Backend endpoint returned: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to access {url}: {str(e)}")

    return False

def test_code_analysis():
    """Test code analysis functionality"""
    print("\nTesting code analysis functionality...")

    test_code = '''
def calculate_user_score(user_data):
    """Calculate score with potential issues"""
    total = 0
    # SQL injection vulnerability
    query = f"SELECT score FROM users WHERE name = '{user_data['name']}'"

    # Resource not properly closed
    file = open("data.txt", "r")
    data = file.read()

    # Hard-coded password
    password = "123456"

    return total
'''

    # Try to test with the deployed API
    try:
        response = requests.post(
            "https://avalia-backend.onrender.com/api/v1/general-analysis/analyze",
            json={
                "code_content": test_code,
                "file_path": "test.py",
                "selected_criteria": ["criteria_66", "criteria_70", "criteria_75"]
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Code analysis API working!")
            print(f"   Analysis type: {result.get('analysis_type', 'Unknown')}")
            print(f"   Demo mode: {result.get('demo_mode', 'Unknown')}")
            return True
        else:
            print(f"ERROR: Code analysis API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to test code analysis: {str(e)}")

    return False

def check_deployment_logs():
    """Check deployment status via git"""
    print("\nChecking deployment configuration...")

    # Check latest commit
    import subprocess
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-5'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Recent commits:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to check git logs: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("AVALIA Deployment Verification Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {
        "frontend": False,
        "backend": False,
        "code_analysis": False,
        "deployment_config": False
    }

    # Run tests
    results["frontend"] = test_frontend_access()
    results["backend"] = test_backend_access()
    results["code_analysis"] = test_code_analysis()
    results["deployment_config"] = check_deployment_logs()

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.title():<20}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nOverall: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("All tests passed! Deployment is working correctly.")
    elif total_passed >= 2:
        print("Partial success. Some services may need attention.")
    else:
        print("Critical issues detected. Deployment needs immediate attention.")

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()