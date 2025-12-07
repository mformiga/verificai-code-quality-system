#!/usr/bin/env python3
"""
Check all prompt-related tables in PostgreSQL database
"""

import psycopg2
import os

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def check_all_prompt_tables():
    """Check all tables that might contain prompts"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Check all tables in database
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print("All tables in database:")
        for table in tables:
            table_name = table[0]
            if 'prompt' in table_name.lower():
                print(f"  * {table_name} (PROMPT TABLE)")

                # Check if table has data
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Records: {count}")

                if count > 0:
                    # Get sample data
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    print(f"    Columns: {columns}")
                    for row in rows:
                        print(f"    Sample: {row}")
                print()
            else:
                print(f"    {table_name}")

        # Specifically check prompt_configurations table
        try:
            cursor.execute("SELECT COUNT(*) FROM prompt_configurations")
            config_count = cursor.fetchone()[0]
            print(f"\nPrompt configurations found: {config_count}")

            if config_count > 0:
                cursor.execute("""
                    SELECT id, name, prompt_type, content, is_active
                    FROM prompt_configurations
                    ORDER BY created_at DESC
                """)

                configs = cursor.fetchall()
                print("\nPrompt configurations:")
                for config in configs:
                    id, name, prompt_type, content, is_active = config
                    print(f"\nID: {id}")
                    print(f"Name: {name}")
                    print(f"Type: {prompt_type}")
                    print(f"Active: {is_active}")
                    print(f"Content preview: {content[:200]}...")
                    print("-" * 50)

        except Exception as e:
            print(f"No prompt_configurations table: {e}")

        conn.close()

    except Exception as e:
        print(f"Error checking tables: {str(e)}")

if __name__ == "__main__":
    check_all_prompt_tables()