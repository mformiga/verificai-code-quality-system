"""
Create environment configuration for Supabase
"""

def create_env_file():
    """Create .env.supabase file"""
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

# Environment
ENVIRONMENT=development
"""

    with open('.env.supabase', 'w') as f:
        f.write(env_content)
    print(".env.supabase file created successfully!")

if __name__ == "__main__":
    print("Creating Supabase configuration...")
    create_env_file()
    print("Next steps:")
    print("1. Create a Supabase project at https://app.supabase.com")
    print("2. Get your Project URL and API keys")
    print("3. Update .env.supabase with your credentials")
    print("4. Run: streamlit run app.py")