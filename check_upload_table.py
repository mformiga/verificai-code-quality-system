#!/usr/bin/env python3
"""
Check for other tables that might contain uploaded files
"""

import psycopg2

def check_upload_table():
    """Check if files are being saved elsewhere"""

    # PostgreSQL configuration
    POSTGRES_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'verificai',
        'user': 'verificai',
        'password': 'verificai123'
    }

    try:
        print("Checking for other tables that might contain uploaded files...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """)
        tables = cursor.fetchall()

        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"  {table_name}")

        # Check specific tables that might contain uploaded files
        upload_tables = []
        for table in tables:
            table_name = table[0]
            if any(keyword in table_name.lower() for keyword in ['upload', 'file', 'document', 'asset', 'binary']):
                upload_tables.append(table_name)

        if upload_tables:
            print(f"\nChecking upload-related tables:")
            for table_name in upload_tables:
                print(f"\n  Table: {table_name}")
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Records: {count}")

                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    recent = cursor.fetchall()
                    for record in recent:
                        print(f"    {record}")

        # Check file_paths table specifically
        cursor.execute("""
        SELECT COUNT(*) FROM file_paths
        """)
        file_paths_count = cursor.fetchone()[0]
        print(f"\nFile paths table: {file_paths_count} records")

        if file_paths_count > 0:
            cursor.execute("""
            SELECT * FROM file_paths ORDER BY created_at DESC LIMIT 5
            """)
            recent_files = cursor.fetchall()
            print("Recent file paths:")
            for file_path in recent_files:
                print(f"  {file_path}")

        # Check timestamps - see when records were created
        cursor.execute("""
        SELECT DATE_TRUNC('minute', created_at) as minute, COUNT(*) as count
        FROM source_codes
        GROUP BY DATE_TRUNC('minute', created_at)
        ORDER BY minute DESC
        LIMIT 10
        """)
        timeline = cursor.fetchall()

        print(f"\nSource codes creation timeline (last 10 minutes):")
        for minute, count in timeline:
            print(f"  {minute}: {count} records")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    check_upload_table()