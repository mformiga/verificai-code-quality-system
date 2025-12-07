#!/usr/bin/env python3
"""
AVALIA Supabase Project Setup Script
This script helps set up the complete Supabase project for AVALIA
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")

    tools = {
        'supabase': 'Supabase CLI',
        'psql': 'PostgreSQL client',
        'git': 'Git'
    }

    missing = []
    for tool, name in tools.items():
        success, _, _ = run_command(f"{tool} --version")
        if success:
            print(f"✅ {name} found")
        else:
            print(f"❌ {name} not found")
            missing.append(tool)

    if missing:
        print(f"\n❌ Missing tools: {', '.join(missing)}")
        print("Please install the missing tools and try again.")
        return False

    return True

def create_supabase_project():
    """Create a new Supabase project"""
    print("\n🚀 Creating Supabase project...")

    # Get project details from user
    project_name = input("Enter project name (default: avalia-code-analysis): ").strip() or "avalia-code-analysis"
    db_password = input("Enter database password (min 10 chars): ").strip()

    if len(db_password) < 10:
        print("❌ Password must be at least 10 characters long")
        return False

    # Login to Supabase
    print("\n🔐 Logging into Supabase...")
    success, _, _ = run_command("supabase login")
    if not success:
        print("❌ Failed to login to Supabase")
        return False

    # Initialize local project
    print("\n📁 Initializing local project...")
    success, _, _ = run_command("supabase init")
    if not success:
        print("❌ Failed to initialize local project")
        return False

    # Create project (this requires manual confirmation)
    print(f"\n🏗️  Creating project '{project_name}'...")
    print("Please complete the project creation in the browser that will open...")
    input("Press Enter after you have created the project...")

    # Link local project to remote
    project_ref = input("Enter your project reference (from Supabase dashboard): ").strip()
    if not project_ref:
        print("❌ Project reference is required")
        return False

    success, _, _ = run_command(f"supabase link --project-ref {project_ref}")
    if not success:
        print("❌ Failed to link project")
        return False

    return True

def apply_database_schema():
    """Apply the database schema"""
    print("\n🗄️  Applying database schema...")

    # Apply initial schema
    schema_file = Path("supabase/migrations/001_initial_schema.sql")
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False

    success, _, error = run_command(f"supabase db push")
    if not success:
        print(f"❌ Failed to apply schema: {error}")
        return False

    print("✅ Database schema applied successfully")

    # Apply storage configuration
    storage_file = Path("supabase/storage/setup_storage.sql")
    if storage_file.exists():
        print("\n📦 Setting up storage...")
        success, _, error = run_command(f"supabase db push --db-url $(supabase status --output json | jq -r '.db.url') --file {storage_file}")
        if not success:
            print(f"⚠️  Warning: Failed to apply storage configuration: {error}")
        else:
            print("✅ Storage configured successfully")

    return True

def get_project_info():
    """Get project information and keys"""
    print("\n🔑 Getting project information...")

    # Get project status
    success, output, error = run_command("supabase status --output json")
    if not success:
        print(f"❌ Failed to get project status: {error}")
        return None

    try:
        status = json.loads(output)

        project_info = {
            'project_url': status.get('API_URL', ''),
            'anon_key': status.get('ANON_KEY', ''),
            'service_role_key': status.get('SERVICE_ROLE_KEY', ''),
            'project_ref': status.get('PROJECT_ID', ''),
            'db_url': status.get('DB_URL', '')
        }

        return project_info
    except json.JSONDecodeError:
        print("❌ Failed to parse project status")
        return None

def update_environment_files(project_info):
    """Update environment files with project information"""
    print("\n📝 Updating environment files...")

    # Create .env file from template
    template_file = Path(".env.supabase.template")
    env_file = Path(".env")

    if template_file.exists():
        content = template_file.read_text()

        # Replace placeholders
        replacements = {
            'your-project-url.supabase.co': project_info['project_url'].replace('https://', '').replace('/rest/v1', ''),
            'your-supabase-anon-key': project_info['anon_key'],
            'your-supabase-service-role-key': project_info['service_role_key'],
            'your-project-ref': project_info['project_ref'],
            '[YOUR-PASSWORD]': '',  # Will be filled manually
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Update database URL
        if 'db_url' in project_info and project_info['db_url']:
            content = content.replace(
                'postgresql://postgres.iamuser:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres',
                project_info['db_url']
            )

        env_file.write_text(content)
        print(f"✅ Created {env_file}")

        # Update backend config
        update_backend_config(project_info)

        # Create Streamlit secrets
        create_streamlit_secrets(project_info)

    return True

def update_backend_config(project_info):
    """Update backend configuration to use Supabase"""
    backend_config_file = Path("backend/app/core/config.py")

    if backend_config_file.exists():
        content = backend_config_file.read_text()

        # Update database URL
        new_db_url = f"# Supabase Configuration\n    DATABASE_URL: str = Field(\n        default=\"{project_info['db_url']}\",\n        env=\"DATABASE_URL\"\n    )"

        # Replace the existing DATABASE_URL configuration
        lines = content.split('\n')
        new_lines = []
        skip_lines = False

        for i, line in enumerate(lines):
            if 'DATABASE_URL: str = Field(' in line:
                skip_lines = True
                # Find the end of the DATABASE_URL configuration
                new_lines.append(new_db_url)
                # Skip lines until we find the closing parenthesis
                for j in range(i + 1, len(lines)):
                    if ')' in lines[j]:
                        break
            elif skip_lines and ')' in line:
                skip_lines = False
                continue
            elif not skip_lines:
                new_lines.append(line)

        backend_config_file.write_text('\n'.join(new_lines))
        print("✅ Updated backend configuration")

def create_streamlit_secrets(project_info):
    """Create Streamlit secrets file"""
    secrets = {
        "supabase": {
            "url": project_info['project_url'],
            "anon_key": project_info['anon_key'],
            "service_role_key": project_info['service_role_key']
        },
        "database": {
            "url": project_info['db_url']
        }
    }

    secrets_file = Path(".streamlit/secrets.toml")
    secrets_file.parent.mkdir(exist_ok=True)

    # Convert to TOML format
    toml_content = "[supabase]\n"
    toml_content += f'url = "{secrets["supabase"]["url"]}"\n'
    toml_content += f'anon_key = "{secrets["supabase"]["anon_key"]}"\n'
    toml_content += f'service_role_key = "{secrets["supabase"]["service_role_key"]}"\n\n'
    toml_content += "[database]\n"
    toml_content += f'url = "{secrets["database"]["url"]}"'

    secrets_file.write_text(toml_content)
    print("✅ Created Streamlit secrets file")

def print_summary(project_info):
    """Print setup summary"""
    print("\n" + "="*60)
    print("🎉 AVALIA Supabase Setup Complete!")
    print("="*60)
    print(f"Project URL: {project_info['project_url']}")
    print(f"Project Ref: {project_info['project_ref']}")
    print(f"Database URL: {project_info['db_url']}")
    print("\n🔑 API Keys:")
    print(f"Anon Key: {project_info['anon_key'][:50]}...")
    print(f"Service Role Key: {project_info['service_role_key'][:50]}...")
    print("\n📝 Next Steps:")
    print("1. Review and update the .env file with your database password")
    print("2. Test the connection using the provided test scripts")
    print("3. Deploy your FastAPI backend with the new configuration")
    print("4. Update your Streamlit frontend to use the new database")
    print("\n🌐 Access your project:")
    print(f"Supabase Dashboard: https://app.supabase.com/project/{project_info['project_ref']}")
    print(f"Supabase Studio: https://app.supabase.com/project/{project_info['project_ref']}/editor")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 AVALIA Supabase Setup Script")
    print("=" * 40)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    print(f"Working directory: {os.getcwd()}")

    # Create Supabase project
    if not create_supabase_project():
        sys.exit(1)

    # Apply database schema
    if not apply_database_schema():
        sys.exit(1)

    # Get project information
    project_info = get_project_info()
    if not project_info:
        sys.exit(1)

    # Update environment files
    update_environment_files(project_info)

    # Print summary
    print_summary(project_info)

if __name__ == "__main__":
    main()