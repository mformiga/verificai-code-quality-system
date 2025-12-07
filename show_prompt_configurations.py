#!/usr/bin/env python3
"""
Show all prompt configurations from PostgreSQL database
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

def show_prompt_configurations():
    """Show all prompt configurations with full content"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Get all prompt configurations
        cursor.execute("""
            SELECT id, name, prompt_type, content, is_active, is_default, created_at, updated_at
            FROM prompt_configurations
            ORDER BY prompt_type, name
        """)

        configs = cursor.fetchall()

        print(f"Found {len(configs)} prompt configurations:\n")

        for config in configs:
            id, name, prompt_type, content, is_active, is_default, created_at, updated_at = config

            print(f"ID: {id}")
            print(f"Name: {name}")
            print(f"Type: {prompt_type}")
            print(f"Active: {is_active}")
            print(f"Default: {is_default}")
            print(f"Created: {created_at}")
            print(f"Updated: {updated_at}")
            print(f"\nContent:")
            print("=" * 50)
            print(content)
            print("=" * 50)
            print("\n" + "="*80 + "\n")

        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    show_prompt_configurations()