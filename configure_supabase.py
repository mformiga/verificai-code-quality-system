"""
Configure Supabase for AVALIA Application
Simple setup script for Windows compatibility
"""

import os
import sys

def create_env_file():
    """Create .env.supabase template file"""
    print("Creating .env.supabase configuration file...")

    env_content = """# Supabase Configuration
# Get these values from your Supabase Project Dashboard:
# 1. Go to https://app.supabase.com
# 2. Create or select your project
# 3. Go to Project Settings -> API
# 4. Copy the Project URL and anon public key

SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-service-role-key-here
SUPABASE_PROJECT_REF=your-project-ref

# Database Connection (optional - Supabase client handles this)
# DATABASE_URL=postgresql://postgres.iamuser:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres

# Environment
ENVIRONMENT=development
"""

    with open('.env.supabase', 'w') as f:
        f.write(env_content)

    print("✅ .env.supabase file created successfully!")
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("AVALIA Supabase Configuration")
    print("=" * 60)

    print("\nThis script will help you configure Supabase for your AVALIA application.")
    print("\n📋 STEPS TO FOLLOW:")
    print("1. Create a Supabase project at https://app.supabase.com")
    print("2. Get your Project URL and API keys")
    print("3. Update the .env.supabase file with your credentials")
    print("4. Set up the database schema (see SUPABASE_SETUP_GUIDE.md)")
    print("5. Test your application")

    print("\n" + "=" * 60)
    print("CREATING CONFIGURATION FILES...")
    print("=" * 60)

    # Create .env file
    if create_env_file():
        print("\n✅ Configuration files created successfully!")
        print("\n📝 NEXT STEPS:")
        print("1. Open .env.supabase file")
        print("2. Replace the placeholder values with your actual Supabase credentials")
        print("3. Save the file")
        print("4. Run: streamlit run app.py")
        print("\n📖 For detailed setup instructions, see SUPABASE_SETUP_GUIDE.md")
    else:
        print("❌ Error creating configuration files")
        return 1

    print("\n🚀 Setup complete! Your application is ready for Supabase integration.")
    return 0

if __name__ == "__main__":
    sys.exit(main())