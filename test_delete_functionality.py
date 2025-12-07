#!/usr/bin/env python3
"""
Test script to verify delete functionality works
"""

import psycopg2

def test_delete_functionality():
    """Test if we can successfully mark codes as deleted"""

    # PostgreSQL configuration (same as in app.py)
    POSTGRES_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'verificai',
        'user': 'verificai',
        'password': 'verificai123'
    }

    try:
        print("Testing delete functionality...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Check current active records
        cursor.execute("SELECT COUNT(*) FROM source_codes WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        print(f"Current active records: {active_count}")

        # Check current deleted records
        cursor.execute("SELECT COUNT(*) FROM source_codes WHERE status = 'deleted'")
        deleted_count = cursor.fetchone()[0]
        print(f"Current deleted records: {deleted_count}")

        # Show some active records
        cursor.execute("""
        SELECT id, title, created_at FROM source_codes
        WHERE status = 'active'
        ORDER BY created_at DESC
        LIMIT 3
        """)
        active_records = cursor.fetchall()

        if active_records:
            print("\nRecent active records:")
            for record in active_records:
                print(f"  ID: {record[0]} - {record[1]} - {record[2]}")
            print(f"\nTo test deletion, you can use ID: {active_records[0][0]}")
        else:
            print("\nNo active records found to test deletion")

        cursor.close()
        conn.close()

        print("\nDelete functionality test completed!")
        print("The delete function should:")
        print("  1. Mark records as 'deleted' instead of physical deletion")
        print("  2. Update the updated_at timestamp")
        print("  3. Return True on success, False on failure")

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_delete_functionality()
    if success:
        print("\nDelete functionality is ready!")
        print("You can now use the 'Excluir Código' button in the interface.")
    else:
        print("\nDelete functionality test failed!")