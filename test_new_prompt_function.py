#!/usr/bin/env python3
"""
Test the new get_prompts_from_postgres function that reads from prompt_configurations
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

def test_new_prompt_function():
    """Test the new function that reads from prompt_configurations"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Same query as the new function
        query = """
        WITH ranked_prompts AS (
          SELECT prompt_type, content, updated_at, id, name, user_id,
                 ROW_NUMBER() OVER (
                   PARTITION BY prompt_type
                   ORDER BY
                     CASE WHEN id IN (7) THEN 1 ELSE 2 END ASC,
                     CASE WHEN name LIKE '%Template%' THEN 1 ELSE 2 END ASC,
                     LENGTH(content) DESC,
                     updated_at DESC
                 ) as rn
          FROM prompt_configurations
          WHERE is_active = true
        )
        SELECT prompt_type, content, updated_at, id, name
        FROM ranked_prompts
        WHERE rn = 1
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} prompts for user 1:\n")

        if rows:
            prompts = {}
            for row in rows:
                prompt_type, content, updated_at, prompt_id, name = row
                # Convert enum values to lowercase for UI
                prompt_type_lower = prompt_type.lower() if prompt_type else 'general'
                prompts[prompt_type_lower] = {
                    'content': content,
                    'version': 1,
                    'last_modified': str(updated_at) if updated_at else '',
                    'id': prompt_id,
                    'name': name
                }

                print(f"Prompt Type: {prompt_type_lower}")
                print(f"Name: {name}")
                print(f"ID: {prompt_id}")
                print(f"Last Modified: {updated_at}")
                print(f"Content Preview: {content[:150]}...")
                print("-" * 60)

            print(f"\nTotal prompts loaded: {len(prompts)}")
            print(f"Types: {list(prompts.keys())}")
        else:
            print("No prompts found!")

        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_new_prompt_function()