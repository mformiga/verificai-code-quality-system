#!/usr/bin/env python3
"""
AVALIA Streamlit Cloud Deployment Test Script
Tests the deployed application functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
STREAMLIT_APP_URL = "https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/"

def test_app_accessibility() -> bool:
    """Test if the Streamlit app is accessible"""
    print("🔍 Testing app accessibility...")
    try:
        response = requests.get(STREAMLIT_APP_URL, timeout=30)
        if response.status_code == 200:
            print("✅ App is accessible")
            return True
        else:
            print(f"❌ App returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing app: {e}")
        return False

def test_supabase_connection_direct() -> Dict[str, Any]:
    """Test Supabase connection using direct API calls (if service role key available)"""
    print("🔍 Testing Supabase connection...")

    # This would require the service role key from secrets
    # For security reasons, this test should be run from the deployed app itself
    return {"status": "info", "message": "Supabase connection should be tested from within the app"}

def create_deployment_checklist() -> None:
    """Create a checklist for manual verification"""
    checklist = f"""
## 🚀 AVALIA Deployment Verification Checklist

### ✅ Automatic Tests (Completed by this script)
- [x] App accessibility test
- [x] URL validation

### 🔍 Manual Tests Required

#### 1. Authentication Flow
- [ ] Visit {STREAMLIT_APP_URL}
- [ ] Click "Registrar" tab
- [ ] Create a new account with email and password
- [ ] Check email for verification (if enabled)
- [ ] Login with new credentials
- [ ] Verify user session persists
- [ ] Test logout functionality

#### 2. Database Integration
- [ ] After login, check if user profile is created
- [ ] Perform a code analysis
- [ ] Verify analysis is saved to database
- [ ] Check "Histórico" tab for previous analyses
- [ ] Verify only user's own analyses are shown

#### 3. Core Application Features
- [ ] Code upload works (try uploading a Python file)
- [ ] Manual code input works
- [ ] Example code loads correctly
- [ ] Criteria selection works
- [ ] Analysis execution completes
- [ ] Results display properly
- [ ] Violations are highlighted correctly

#### 4. Error Handling
- [ ] Invalid login shows proper error
- [ ] Duplicate registration shows proper error
- [ ] Network failures are handled gracefully
- [ ] Empty analysis requests are rejected

#### 5. UI/UX
- [ ] AVALIA branding is displayed correctly
- [ ] Yellow IA highlighting works
- [ ] Responsive design on mobile
- [ ] Loading indicators work
- [ ] Success/error messages display correctly

### 🛠️ Configuration Verification

In Streamlit Cloud dashboard, verify:
- [ ] Secrets are configured correctly:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY
- [ ] Requirements.txt includes all dependencies
- [ ] App file path points to app.py
- [ ] Python version is compatible

### 📊 Performance Check
- [ ] App loads within 10 seconds
- [ ] Code analysis completes within 2 minutes
- [ ] Database queries are responsive
- [ ] Memory usage stays within limits

### 🔒 Security Verification
- [ ] HTTPS is enforced
- [ ] Row Level Security (RLS) policies are active
- [ ] Users cannot access other users' data
- [ ] Sensitive data is not exposed in client-side code
- [ ] Authentication tokens are handled securely

### 📝 Integration Tests
- [ ] Supabase connection established
- [ ] Authentication flow works end-to-end
- [ ] Database operations complete successfully
- [ ] File storage works (if implemented)
- [ ] Analysis results persist correctly

## 🚨 Troubleshooting Guide

### Common Issues and Solutions:

1. **App Not Loading**
   - Check deployment logs in Streamlit Cloud
   - Verify requirements.txt is correct
   - Ensure app.py exists and is valid

2. **Authentication Fails**
   - Verify Supabase secrets are correct
   - Check Supabase auth settings
   - Ensure email confirmation is properly configured

3. **Database Connection Issues**
   - Verify Supabase URL and keys
   - Check RLS policies
   - Ensure database schema is installed

4. **Analysis Not Working**
   - Check API connectivity
   - Verify criteria are loading
   - Check file upload functionality

## 📞 Support Resources

- Streamlit Cloud Documentation
- Supabase Documentation
- Application logs in Streamlit Cloud dashboard
- Supabase project logs and monitoring
    """

    with open("deployment_checklist.md", "w", encoding="utf-8") as f:
        f.write(checklist)

    print("📋 Deployment checklist created: deployment_checklist.md")

def main():
    """Main deployment test function"""
    print("🚀 AVALIA Streamlit Cloud Deployment Test")
    print("=" * 50)

    # Test app accessibility
    app_accessible = test_app_accessibility()

    if not app_accessible:
        print("\n❌ Critical: App is not accessible. Please check:")
        print("  1. Streamlit Cloud deployment status")
        print("  2. App URL is correct")
        print("  3. No deployment errors in logs")
        sys.exit(1)

    # Test Supabase connection info
    print("\n📊 Supabase Connection Test:")
    print("ℹ️  Supabase connection will be tested from within the app")
    print("ℹ️  Check the app's sidebar for connection status")

    # Create verification checklist
    create_deployment_checklist()

    print(f"\n✅ Automated tests completed!")
    print(f"📋 Manual verification checklist created")
    print(f"🌐 App URL: {STREAMLIT_APP_URL}")
    print(f"📖 Follow deployment_checklist.md for manual testing")

if __name__ == "__main__":
    main()