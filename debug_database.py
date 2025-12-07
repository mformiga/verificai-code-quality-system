#!/usr/bin/env python3
"""
Debug script to check what's actually in the database
"""

import psycopg2

def debug_database():
    """Check database contents directly"""

    # PostgreSQL configuration
    POSTGRES_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'verificai',
        'user': 'verificai',
        'password': 'verificai123'
    }

    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        print("\n1. Check table structure:")
        cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'source_codes'
        ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]}")

        print("\n2. Total records in source_codes table:")
        cursor.execute("SELECT COUNT(*) FROM source_codes")
        total = cursor.fetchone()[0]
        print(f"  Total: {total} records")

        print("\n3. Records by status:")
        cursor.execute("SELECT status, COUNT(*) FROM source_codes GROUP BY status")
        status_counts = cursor.fetchall()
        for status, count in status_counts:
            print(f"  {status}: {count} records")

        print("\n4. Recent records (all):")
        cursor.execute("""
        SELECT id, code_id, title, file_name, programming_language,
               size_bytes, created_at, status
        FROM source_codes
        ORDER BY created_at DESC
        LIMIT 10
        """)
        recent = cursor.fetchall()

        for i, record in enumerate(recent):
            print(f"  {i+1}. ID:{record[0]} - {record[2]} - {record[4]} ({record[5]} bytes) - {record[7]}")

        print("\n5. Active records only (like the interface query):")
        cursor.execute("""
        SELECT id, code_id, title, file_name, programming_language,
               size_bytes, created_at, status
        FROM source_codes
        WHERE status = 'active'
        ORDER BY created_at DESC
        LIMIT 10
        """)
        active_records = cursor.fetchall()

        print(f"  Found {len(active_records)} active records:")
        for i, record in enumerate(active_records):
            print(f"    {i+1}. ID:{record[0]} - {record[2]} - {record[4]} ({record[5]} bytes)")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    debug_database()