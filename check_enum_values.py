#!/usr/bin/env python3
"""
Check enum values in PostgreSQL database
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

def check_enums():
    """Check all enum values in PostgreSQL"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Check prompt_type_enum values
        cursor.execute("""
            SELECT unnest(enum_range(NULL::prompt_type_enum))
        """)

        enum_values = cursor.fetchall()
        print("Available values for prompt_type_enum:")
        for value in enum_values:
            print(f"  - '{value[0]}'")

        conn.close()

    except Exception as e:
        print(f"Error checking enums: {str(e)}")

if __name__ == "__main__":
    check_enums()