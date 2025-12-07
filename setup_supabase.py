#!/usr/bin/env python3
"""
AVALIA Supabase Setup Script
Automates the configuration of a new Supabase project for AVALIA Code Analysis
"""

import os
import sys
import json
import secrets
from typing import Dict, List
from supabase import create_client, Client

def load_schema_sql(file_path: str) -> str:
    """Load SQL schema from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Schema file not found: {file_path}")
        return None

def test_connection(supabase: Client) -> bool:
    """Test Supabase connection"""
    try:
        # Test basic connection
        response = supabase.table('profiles').select('count').execute()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def execute_schema_migration(supabase: Client, schema_sql: str) -> bool:
    """Execute the database schema migration"""
    try:
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

        print(f"📊 Executing {len(statements)} SQL statements...")

        # Note: Supabase Python client doesn't support executing arbitrary SQL
        # This needs to be done manually in the Supabase SQL Editor
        print("⚠️  Schema migration must be executed manually in Supabase SQL Editor")
        print("📝 Please copy the contents of supabase/migrations/001_initial_schema.sql")

        return True
    except Exception as e:
        print(f"❌ Schema migration failed: {e}")
        return False

def create_storage_buckets(supabase: Client) -> bool:
    """Create storage buckets for files"""
    try:
        # Note: Storage bucket creation via API is limited
        # This is better done through the Supabase Dashboard
        print("📁 Storage buckets need to be created manually in Supabase Dashboard")
        print("📋 Required buckets:")
        print("   - code-files (100MB limit, private)")
        print("   - analysis-reports (50MB limit, private)")
        print("   - user-avatars (2MB limit, public)")

        return True
    except Exception as e:
        print(f"❌ Storage setup failed: {e}")
        return False

def generate_env_template(project_url: str, anon_key: str, service_role_key: str,
                        project_ref: str, database_url: str, jwt_secret: str) -> str:
    """Generate .env.supabase file content"""

    env_content = f"""# AVALIA Supabase Configuration
# Generated on {os.times()[4]}

# Supabase Configuration
SUPABASE_URL={project_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_role_key}
SUPABASE_PROJECT_REF={project_ref}

# Database Configuration
DATABASE_URL={database_url}

# Authentication
JWT_SECRET={jwt_secret}
SUPABASE_JWT_SECRET={jwt_secret}

# Storage Configuration
STORAGE_URL={project_url}/storage/v1
STORAGE_REGION=us-west-1

# Development Configuration
ALLOWED_HOSTS=http://localhost:3000,http://localhost:5173,http://localhost:3026
"""
    return env_content

def validate_configuration(supabase_url: str, anon_key: str, service_role_key: str) -> bool:
    """Validate Supabase configuration"""
    if not supabase_url or not anon_key or not service_role_key:
        print("❌ Missing required Supabase configuration")
        return False

    if not supabase_url.startswith('https://') or not supabase_url.endswith('.supabase.co'):
        print("❌ Invalid Supabase URL format")
        return False

    if not anon_key.startswith('eyJ') or not service_role_key.startswith('eyJ'):
        print("❌ Invalid API key format")
        return False

    return True

def setup_project():
    """Main setup function"""
    print("🔍 AVALIA Supabase Setup Script")
    print("=" * 40)

    # Step 1: Collect Supabase credentials
    print("\n📝 Step 1: Supabase Project Credentials")
    print("Please enter your Supabase project details:")

    supabase_url = input("Supabase Project URL: ").strip()
    anon_key = input("Supabase Anon Key: ").strip()
    service_role_key = input("Supabase Service Role Key: ").strip()
    project_ref = input("Project Reference (from URL): ").strip()

    # Construct database URL
    db_password = input("Database Password: ").strip()
    database_url = f"postgresql://postgres.iamuser:{db_password}@aws-0-us-west-1.pooler.supabase.com:5432/postgres"

    # JWT secret (typical format)
    jwt_secret = input("JWT Secret: ").strip()

    # Validate configuration
    if not validate_configuration(supabase_url, anon_key, service_role_key):
        print("❌ Invalid configuration. Please check your inputs.")
        return False

    # Step 2: Test connection
    print("\n🔌 Step 2: Testing Database Connection")
    try:
        supabase = create_client(supabase_url, anon_key)
        if not test_connection(supabase):
            print("❌ Connection test failed. Please check your credentials.")
            return False
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

    # Step 3: Load and validate schema
    print("\n📊 Step 3: Database Schema")
    schema_file = "supabase/migrations/001_initial_schema.sql"
    schema_sql = load_schema_sql(schema_file)

    if not schema_sql:
        print("❌ Schema file not found. Please ensure the file exists.")
        return False

    print(f"✅ Schema file loaded: {len(schema_sql)} characters")

    # Step 4: Storage setup
    print("\n📁 Step 4: Storage Configuration")
    create_storage_buckets(supabase)

    # Step 5: Generate environment file
    print("\n⚙️ Step 5: Environment Configuration")
    env_content = generate_env_template(
        supabase_url, anon_key, service_role_key,
        project_ref, database_url, jwt_secret
    )

    env_file = ".env.supabase"
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Environment file created: {env_file}")
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

    # Step 6: Manual setup instructions
    print("\n📋 Step 6: Manual Setup Required")
    print("The following steps need to be completed manually in the Supabase Dashboard:")
    print()
    print("1. 🗄️  Database Schema:")
    print("   - Go to SQL Editor")
    print(f"   - Copy contents of '{schema_file}'")
    print("   - Execute the migration")
    print()
    print("2. 📁 Storage Buckets:")
    print("   - Go to Storage")
    print("   - Create bucket 'code-files' (100MB, private)")
    print("   - Create bucket 'analysis-reports' (50MB, private)")
    print("   - Create bucket 'user-avatars' (2MB, public)")
    print("   - Run storage policies from 'supabase/storage/setup_storage.sql'")
    print()
    print("3. 🔐 Authentication:")
    print("   - Go to Authentication → Settings")
    print("   - Set Site URL to your frontend URL")
    print("   - Add redirect URLs for your domains")
    print("   - Configure email templates")
    print()
    print("4. 🌐 CORS Configuration:")
    print("   - Add your frontend domains to CORS settings")

    # Step 7: Test application
    print("\n🧪 Step 7: Application Testing")
    print("After completing the manual setup:")
    print("1. Run: streamlit run app.py")
    print("2. Test user registration and login")
    print("3. Test file upload and analysis")
    print("4. Verify data privacy (RLS)")

    print("\n✅ Setup completed successfully!")
    print("📖 Refer to SUPABASE_SETUP_GUIDE.md for detailed instructions")

    return True

def check_requirements():
    """Check if required files and dependencies exist"""
    print("🔍 Checking requirements...")

    required_files = [
        "supabase/migrations/001_initial_schema.sql",
        "supabase/storage/setup_storage.sql",
        "supabase_client.py"
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    # Check Python dependencies
    try:
        import supabase
        print("✅ Supabase Python client installed")
    except ImportError:
        print("❌ Supabase Python client not installed")
        print("   Run: pip install supabase")
        return False

    try:
        import streamlit
        print("✅ Streamlit installed")
    except ImportError:
        print("❌ Streamlit not installed")
        print("   Run: pip install streamlit")
        return False

    print("✅ All requirements satisfied")
    return True

if __name__ == "__main__":
    print("🚀 AVALIA Supabase Setup")
    print("This script will help you configure your Supabase project for AVALIA Code Analysis")
    print()

    # Check requirements first
    if not check_requirements():
        sys.exit(1)

    # Check if environment file already exists
    if os.path.exists(".env.supabase"):
        overwrite = input("⚠️  .env.supabase already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            sys.exit(0)

    # Run setup
    try:
        success = setup_project()
        if success:
            print("\n🎉 Setup completed successfully!")
            print("📖 Follow the manual setup instructions in SUPABASE_SETUP_GUIDE.md")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)