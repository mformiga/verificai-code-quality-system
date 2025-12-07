#!/usr/bin/env python3
"""
Check the structure of prompt_configurations table in PostgreSQL
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

def check_table_structure():
    """Get detailed structure of prompt_configurations table"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Get table structure
        cursor.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'prompt_configurations'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()

        print("=== ESTRUTURA DA TABELA prompt_configurations ===\n")

        for col in columns:
            column_name, data_type, is_nullable, column_default, max_length = col
            print(f"Column: {column_name}")
            print(f"  Type: {data_type}")
            print(f"  Nullable: {is_nullable}")
            print(f"  Default: {column_default}")
            print(f"  Max Length: {max_length}")
            print()

        # Get constraints
        cursor.execute("""
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            LEFT JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            LEFT JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'prompt_configurations'
        """)

        constraints = cursor.fetchall()

        print("=== CONSTRAINTS ===\n")
        for constraint in constraints:
            constraint_name, constraint_type, column_name, foreign_table, foreign_col = constraint
            print(f"{constraint_type}: {constraint_name} on {column_name}")
            if foreign_table:
                print(f"  -> References {foreign_table}.{foreign_col}")
            print()

        # Get sample data
        cursor.execute("SELECT * FROM prompt_configurations LIMIT 3")
        sample_data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        print("=== SAMPLE DATA ===\n")
        print(f"Columns: {column_names}")
        for row in sample_data:
            print(f"Sample: {row}")
            print()

        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_table_structure()