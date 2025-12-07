#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection and check for existing prompts
"""

import psycopg2
import os
from datetime import datetime

# Database configuration (same as app.py)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def test_postgres_connection():
    """Test PostgreSQL connection and check for prompts"""
    try:
        print("Testing PostgreSQL connection...")
        print(f"Connection config: {POSTGRES_CONFIG}")

        # Connect to PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        print("PostgreSQL connection successful!")

        # Check if prompts table exists
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'prompts'
        """)

        table_exists = cursor.fetchone()
        if table_exists:
            print("Prompts table exists!")

            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'prompts'
                ORDER BY ordinal_position
            """)

            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")

            # Check for existing prompts
            cursor.execute("SELECT COUNT(*) FROM prompts")
            count = cursor.fetchone()[0]

            print(f"\nTotal prompts in database: {count}")

            if count > 0:
                # Get all prompts
                cursor.execute("""
                    SELECT id, type, content, version, user_id, created_at, updated_at
                    FROM prompts
                    ORDER BY created_at DESC
                """)

                prompts = cursor.fetchall()

                print("\nExisting prompts:")
                for prompt in prompts:
                    id, type, content, version, user_id, created_at, updated_at = prompt
                    print(f"\n  ID: {id}")
                    print(f"  Type: {type}")
                    print(f"  User ID: {user_id}")
                    print(f"  Version: {version}")
                    print(f"  Created: {created_at}")
                    print(f"  Updated: {updated_at}")
                    print(f"  Content preview: {content[:100]}...")
            else:
                print("No prompts found in database")
        else:
            print("Prompts table does not exist!")

            # List all tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            if tables:
                print("Available tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("No tables found in database")

        # Check for users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\nTotal users in database: {user_count}")

        if user_count > 0:
            cursor.execute("SELECT id, username, email FROM users LIMIT 5")
            users = cursor.fetchall()
            print("\nSample users:")
            for user in users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

        conn.close()
        print("\nTest completed successfully!")

    except Exception as e:
        print(f"Error connecting to PostgreSQL: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

    return True

if __name__ == "__main__":
    print("Starting PostgreSQL connection test...")
    test_postgres_connection()