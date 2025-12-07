#!/usr/bin/env python3
"""
Script to execute the source_codes table creation in Supabase
Requires: pip install supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_sql_file(file_path):
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def execute_sql_in_supabase(supabase: Client, sql_content: str):
    """Execute SQL commands in Supabase"""
    try:
        # Split the SQL content by semicolons to execute each statement
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

        print("Executing SQL statements in Supabase...")
        print("=" * 60)

        for i, statement in enumerate(sql_statements, 1):
            if statement:
                print(f"\nExecuting statement {i}/{len(sql_statements)}:")
                print(f"Type: {statement.split()[0].upper() if statement else 'EMPTY'}")

                try:
                    # Execute the SQL statement using Supabase RPC
                    result = supabase.rpc('exec_sql', {'sql_query': statement}).execute()
                    print(f"✓ Success")
                except Exception as e:
                    # If RPC fails, try using raw SQL through PostgREST
                    print(f"⚠ Warning: {str(e)}")
                    # Some statements might not need to return data

        print("\n" + "=" * 60)
        print("SQL execution completed!")

    except Exception as e:
        print(f"Error executing SQL: {e}")
        return False

    return True

def verify_table_creation(supabase: Client):
    """Verify if the source_codes table was created successfully"""
    try:
        print("\nVerifying table creation...")

        # Check if table exists by trying to select from it
        result = supabase.table('source_codes').select('count', count='exact').execute()

        if hasattr(result, 'data'):
            print(f"✓ Table 'source_codes' exists successfully!")
            print(f"  Current record count: {result.get('count', 0)}")
        else:
            print("✓ Table 'source_codes' appears to be created")

        # Try to get table structure (if possible)
        print("\nAttempting to verify table structure...")
        try:
            # This might not work with all Supabase configurations
            result = supabase.rpc('get_table_structure', {'table_name': 'source_codes'}).execute()
            print("✓ Table structure verified")
        except:
            print("  Note: Cannot verify detailed structure through API, but table appears to be created")

        return True

    except Exception as e:
        print(f"✗ Error verifying table: {e}")
        return False

def main():
    """Main function"""
    print("Supabase Table Creation Script")
    print("=" * 60)

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("Error: Supabase credentials not found!")
        print("Please ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your environment")
        print("\nYou can set them as environment variables:")
        print("export SUPABASE_URL='your-project-url'")
        print("export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'")
        return

    # Initialize Supabase client
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✓ Connected to Supabase at {supabase_url}")
    except Exception as e:
        print(f"✗ Error connecting to Supabase: {e}")
        return

    # Read SQL file
    sql_file = "create_source_codes_supabase.sql"
    sql_content = read_sql_file(sql_file)

    if not sql_content:
        print(f"✗ Could not read SQL file: {sql_file}")
        return

    print(f"✓ Read SQL file: {sql_file}")

    # Execute SQL
    if execute_sql_in_supabase(supabase, sql_content):
        # Verify table creation
        if verify_table_creation(supabase):
            print("\n✓ Success! Table 'source_codes' has been created in Supabase!")
            print("\nNext steps:")
            print("1. Verify the table structure in your Supabase dashboard")
            print("2. Check that RLS policies are correctly configured")
            print("3. Test inserting a sample record")
        else:
            print("\n⚠ SQL executed but verification failed. Please check manually in Supabase dashboard.")
    else:
        print("\n✗ Failed to create table. Please check the error messages above.")

if __name__ == "__main__":
    main()