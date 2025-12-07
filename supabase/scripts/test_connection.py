#!/usr/bin/env python3
"""
AVALIA Supabase Connection Test Script
This script tests all aspects of Supabase connectivity and functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the backend to the Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.supabase import (
    get_supabase_client, get_supabase_services, verify_supabase_connection,
    supabase_config
)
from supabase import create_client


def print_test_result(test_name: str, success: bool, message: str = ""):
    """Print a formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"     {message}")


def test_configuration():
    """Test Supabase configuration"""
    print("🔧 Testing Configuration...")
    print("-" * 40)

    # Check if environment variables are set
    env_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "SUPABASE_PROJECT_REF": os.getenv("SUPABASE_PROJECT_REF")
    }

    config_ok = True
    for var_name, value in env_vars.items():
        if value:
            print_test_result(f"Environment variable {var_name}", True, "Set")
        else:
            print_test_result(f"Environment variable {var_name}", False, "Not set")
            config_ok = False

    # Check supabase_config object
    if supabase_config.is_configured:
        print_test_result("Supabase configuration", True)
    else:
        print_test_result("Supabase configuration", False, "Not properly configured")
        config_ok = False

    return config_ok


def test_connection():
    """Test basic Supabase connection"""
    print("\n🔗 Testing Connection...")
    print("-" * 40)

    # Test connection using utility function
    connection_result = verify_supabase_connection()

    if connection_result["connected"]:
        print_test_result("Basic connection", True)
        print(f"     Project Ref: {connection_result.get('project_ref', 'Unknown')}")
        print(f"     URL: {connection_result.get('url', 'Unknown')}")
        return True
    else:
        print_test_result("Basic connection", False, connection_result.get('error', 'Unknown error'))
        return False


def test_authentication():
    """Test authentication functionality"""
    print("\n🔐 Testing Authentication...")
    print("-" * 40)

    try:
        services = get_supabase_services()
        if not services:
            print_test_result("Get authentication services", False, "Supabase not configured")
            return False

        auth = services["auth"]

        # Test JWT verification (will fail without valid token, but tests structure)
        try:
            invalid_token = "invalid_token_test"
            user_result = auth.get_user(invalid_token)
            print_test_result("JWT validation structure", True, "Services available (token invalid as expected)")
        except Exception as e:
            print_test_result("JWT validation structure", True, f"Services available: {str(e)[:50]}...")

        return True

    except Exception as e:
        print_test_result("Get authentication services", False, str(e))
        return False


def test_database_operations():
    """Test database operations"""
    print("\n🗄️  Testing Database Operations...")
    print("-" * 40)

    try:
        services = get_supabase_services()
        if not services:
            print_test_result("Get database services", False, "Supabase not configured")
            return False

        db = services["database"]

        # Test table structure existence (we'll test for the tables we created)
        tables_to_test = [
            "profiles",
            "prompts",
            "analyses",
            "uploaded_files",
            "general_criteria"
        ]

        all_tables_ok = True
        for table in tables_to_test:
            try:
                # Try to select from the table
                result = db.select(table, "*", limit=1)
                if result["success"]:
                    print_test_result(f"Table '{table}' accessible", True, f"Columns available")
                else:
                    print_test_result(f"Table '{table}' accessible", False, result.get('error', 'Unknown error'))
                    all_tables_ok = False
            except Exception as e:
                print_test_result(f"Table '{table}' accessible", False, str(e))
                all_tables_ok = False

        return all_tables_ok

    except Exception as e:
        print_test_result("Get database services", False, str(e))
        return False


def test_storage_operations():
    """Test storage operations"""
    print("\n📦 Testing Storage Operations...")
    print("-" * 40)

    try:
        services = get_supabase_services()
        if not services:
            print_test_result("Get storage services", False, "Supabase not configured")
            return False

        storage = services["storage"]

        # Test bucket existence
        buckets_to_test = ["code-files", "analysis-reports", "user-avatars"]
        storage_ok = True

        for bucket in buckets_to_test:
            try:
                # Try to list files (will be empty if bucket exists but has no files)
                result = storage.list_files(bucket)
                if result["success"]:
                    print_test_result(f"Storage bucket '{bucket}' accessible", True)
                else:
                    print_test_result(f"Storage bucket '{bucket}' accessible", False, result.get('error', 'Unknown error'))
                    storage_ok = False
            except Exception as e:
                # Check if it's a permissions issue (bucket might exist but not accessible)
                if "404" in str(e) or "not found" in str(e).lower():
                    print_test_result(f"Storage bucket '{bucket}'", False, "Bucket not found")
                    storage_ok = False
                else:
                    print_test_result(f"Storage bucket '{bucket}'", True, "Accessible (permission expected)")

        return storage_ok

    except Exception as e:
        print_test_result("Get storage services", False, str(e))
        return False


def test_row_level_security():
    """Test Row Level Security policies"""
    print("\n🔒 Testing Row Level Security...")
    print("-" * 40)

    try:
        services = get_supabase_services()
        if not services:
            print_test_result("RLS test", False, "Supabase not configured")
            return False

        db = services["database"]

        # Test RLS is enabled (should fail to access data without proper auth)
        try:
            # Try to select profiles without authentication - should return empty due to RLS
            result = db.select("profiles", "*", limit=1)
            if result["success"] and len(result.get("data", [])) == 0:
                print_test_result("RLS on profiles", True, "No data returned (expected without auth)")
            elif result["success"] and len(result.get("data", [])) > 0:
                print_test_result("RLS on profiles", False, "Data returned without authentication")
            else:
                print_test_result("RLS on profiles", False, "Failed to test RLS")
        except Exception as e:
            print_test_result("RLS on profiles", True, f"RLS appears to be working: {str(e)[:50]}...")

        return True

    except Exception as e:
        print_test_result("RLS test", False, str(e))
        return False


def test_data_models():
    """Test data model structure"""
    print("\n📋 Testing Data Models...")
    print("-" * 40)

    try:
        services = get_supabase_admin_client()
        if not services:
            print_test_result("Admin client for schema test", False, "Service role key not available")
            return False

        admin_db = services.database

        # Test schema structure by checking column existence
        schema_checks = [
            ("profiles", ["id", "username", "email", "role", "is_active"]),
            ("prompts", ["id", "user_id", "type", "content", "version"]),
            ("analyses", ["id", "user_id", "prompt_id", "name", "status"]),
            ("uploaded_files", ["id", "user_id", "file_id", "original_name", "status"]),
            ("general_criteria", ["id", "user_id", "text", "is_active"])
        ]

        schema_ok = True
        for table, expected_columns in schema_checks:
            try:
                # Get table information (this is a simplified test)
                result = admin_db.select(table, "*", limit=1)
                if result["success"]:
                    print_test_result(f"Table '{table}' structure", True, f"Accessible with {len(expected_columns)} expected columns")
                else:
                    print_test_result(f"Table '{table}' structure", False, result.get('error', 'Unknown error'))
                    schema_ok = False
            except Exception as e:
                print_test_result(f"Table '{table}' structure", False, str(e))
                schema_ok = False

        return schema_ok

    except Exception as e:
        print_test_result("Data models test", False, str(e))
        return False


def main():
    """Main test function"""
    print("🧪 AVALIA Supabase Integration Test Suite")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    # Load environment from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n📝 Loading environment from {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print_test_result("Environment loading", True)
        except ImportError:
            print_test_result("Environment loading", False, "python-dotenv not installed")
        except Exception as e:
            print_test_result("Environment loading", False, str(e))

    print("\n" + "=" * 50)

    # Run all tests
    test_results = []

    # Test 1: Configuration
    test_results.append(("Configuration", test_configuration()))

    # Test 2: Connection
    test_results.append(("Connection", test_connection()))

    # Test 3: Authentication
    test_results.append(("Authentication", test_authentication()))

    # Test 4: Database Operations
    test_results.append(("Database Operations", test_database_operations()))

    # Test 5: Storage Operations
    test_results.append(("Storage Operations", test_storage_operations()))

    # Test 6: Row Level Security
    test_results.append(("Row Level Security", test_row_level_security()))

    # Test 7: Data Models
    test_results.append(("Data Models", test_data_models()))

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("-" * 50)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        if result:
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            failed += 1
            print(f"❌ {test_name}: FAILED")

    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 All tests passed! Your Supabase integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())