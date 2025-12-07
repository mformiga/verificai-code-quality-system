#!/usr/bin/env python3
"""
AVALIA Supabase Setup Validation Script
This script validates that all required files and configurations are in place
"""

import os
import sys
from pathlib import Path


def print_status(message: str, success: bool):
    """Print formatted status message"""
    icon = "[PASS]" if success else "[FAIL]"
    print(f"{icon} {message}")


def validate_file_structure():
    """Validate that all required files exist"""
    print("Validating File Structure...")
    print("-" * 40)

    required_files = [
        "supabase/migrations/001_initial_schema.sql",
        "supabase/storage/setup_storage.sql",
        "supabase/config.toml",
        "supabase/scripts/setup_project.py",
        "supabase/scripts/test_connection.py",
        "backend/app/core/supabase.py",
        "backend/app/dependencies/supabase.py",
        "backend/app/api/v1/supabase_auth.py",
        "frontend/utils/supabase_client.py",
        "frontend/pages/auth.py",
        "backend/requirements_supabase.txt",
        ".env.supabase.template",
        "supabase/README.md"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        exists = full_path.exists()
        print_status(f"File: {file_path}", exists)
        if not exists:
            all_exist = False

    return all_exist


def validate_schema_content():
    """Validate database schema content"""
    print("\nValidating Database Schema...")
    print("-" * 40)

    schema_file = Path("supabase/migrations/001_initial_schema.sql")
    if not schema_file.exists():
        print_status("Schema file exists", False)
        return False

    content = schema_file.read_text()

    required_elements = [
        ("CREATE EXTENSION", "PostgreSQL extensions"),
        ("CREATE TYPE user_role", "User role enum"),
        ("CREATE TABLE public.profiles", "Profiles table"),
        ("CREATE TABLE public.prompts", "Prompts table"),
        ("CREATE TABLE public.analyses", "Analyses table"),
        ("CREATE TABLE public.uploaded_files", "Uploaded files table"),
        ("ALTER TABLE.*ENABLE ROW LEVEL SECURITY", "RLS enabled"),
        ("CREATE POLICY", "RLS policies")
    ]

    schema_valid = True
    for element, description in required_elements:
        found = element in content
        print_status(f"Schema element: {description}", found)
        if not found:
            schema_valid = False

    return schema_valid


def validate_storage_setup():
    """Validate storage configuration"""
    print("\nValidating Storage Setup...")
    print("-" * 40)

    storage_file = Path("supabase/storage/setup_storage.sql")
    if not storage_file.exists():
        print_status("Storage setup file exists", False)
        return False

    content = storage_file.read_text()

    required_buckets = [
        "code-files",
        "analysis-reports",
        "user-avatars"
    ]

    required_policies = [
        "Users can upload their own",
        "Users can view their own",
        "RLS policies"
    ]

    storage_valid = True
    for bucket in required_buckets:
        found = f"'{bucket}'" in content
        print_status(f"Bucket configuration: {bucket}", found)
        if not found:
            storage_valid = False

    for policy in required_policies:
        found = policy in content
        print_status(f"Policy: {policy}", found)
        if not found:
            storage_valid = False

    return storage_valid


def validate_backend_integration():
    """Validate backend integration files"""
    print("\nValidating Backend Integration...")
    print("-" * 40)

    backend_files = [
        ("backend/app/core/supabase.py", ["class SupabaseConfig", "def get_supabase_client", "class SupabaseAuth"]),
        ("backend/app/dependencies/supabase.py", ["async def get_current_user", "require_permissions", "get_supabase_services_dep"]),
        ("backend/app/api/v1/supabase_auth.py", ["@router.post('/auth/signup')", "@router.post('/auth/login')", "class LoginRequest"])
    ]

    backend_valid = True
    for file_path, required_content in backend_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print_status(f"File exists: {file_path}", False)
            backend_valid = False
            continue

        content = full_path.read_text()
        for content_item in required_content:
            found = content_item in content
            print_status(f"{file_path}: {content_item}", found)
            if not found:
                backend_valid = False

    return backend_valid


def validate_frontend_integration():
    """Validate frontend integration files"""
    print("\nValidating Frontend Integration...")
    print("-" * 40)

    frontend_files = [
        ("frontend/utils/supabase_client.py", ["class SupabaseClient", "def sign_in", "def upload_file"]),
        ("frontend/pages/auth.py", ["def sign_in_form", "def sign_up_form", "st.title"])
    ]

    frontend_valid = True
    for file_path, required_content in frontend_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print_status(f"File exists: {file_path}", False)
            frontend_valid = False
            continue

        content = full_path.read_text()
        for content_item in required_content:
            found = content_item in content
            print_status(f"{file_path}: {content_item}", found)
            if not found:
                frontend_valid = False

    return frontend_valid


def validate_configuration_templates():
    """Validate configuration templates"""
    print("\nValidating Configuration Templates...")
    print("-" * 40)

    templates = [
        (".env.supabase.template", ["SUPABASE_URL=", "SUPABASE_ANON_KEY=", "DATABASE_URL="]),
        ("supabase/config.toml", ["[project]", "[api]", "[db]", "[auth]"])
    ]

    config_valid = True
    for file_path, required_content in templates:
        full_path = Path(file_path)
        if not full_path.exists():
            print_status(f"Template exists: {file_path}", False)
            config_valid = False
            continue

        content = full_path.read_text()
        for content_item in required_content:
            found = content_item in content
            print_status(f"{file_path}: {content_item}", found)
            if not found:
                config_valid = False

    return config_valid


def validate_documentation():
    """Validate documentation"""
    print("\nValidating Documentation...")
    print("-" * 40)

    readme_file = Path("supabase/README.md")
    if not readme_file.exists():
        print_status("README.md exists", False)
        return False

    content = readme_file.read_text()
    required_sections = [
        "# AVALIA Supabase Integration Guide",
        "## Prerequisites",
        "## Quick Setup",
        "## Database Schema",
        "## Integration with Backend",
        "## Integration with Frontend",
        "## Testing"
    ]

    docs_valid = True
    for section in required_sections:
        found = section in content
        print_status(f"Documentation section: {section}", found)
        if not found:
            docs_valid = False

    return docs_valid


def main():
    """Main validation function"""
    print("AVALIA Supabase Setup Validation")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")

    print("\n" + "=" * 50)

    # Run all validations
    validations = [
        ("File Structure", validate_file_structure),
        ("Database Schema", validate_schema_content),
        ("Storage Setup", validate_storage_setup),
        ("Backend Integration", validate_backend_integration),
        ("Frontend Integration", validate_frontend_integration),
        ("Configuration Templates", validate_configuration_templates),
        ("Documentation", validate_documentation)
    ]

    results = []
    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            results.append((validation_name, result))
        except Exception as e:
            print(f"\n❌ Error in {validation_name}: {str(e)}")
            results.append((validation_name, False))

    # Print summary
    print("\n" + "=" * 50)
    print("Validation Summary")
    print("-" * 50)

    passed = 0
    failed = 0

    for validation_name, result in results:
        if result:
            passed += 1
            print(f"✅ {validation_name}: PASSED")
        else:
            failed += 1
            print(f"❌ {validation_name}: FAILED")

    print(f"\nTotal: {passed + failed} validations")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 All validations passed! Your Supabase setup is complete.")
        print("\n📋 Next Steps:")
        print("1. Run the setup script to create your Supabase project:")
        print("   python supabase/scripts/setup_project.py")
        print("2. Install required dependencies:")
        print("   pip install -r backend/requirements_supabase.txt")
        print("3. Update your environment configuration")
        print("4. Test the connection with:")
        print("   python supabase/scripts/test_connection.py")
        return 0
    else:
        print(f"\n⚠️  {failed} validation(s) failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())