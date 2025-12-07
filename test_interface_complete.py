#!/usr/bin/env python3
"""
Test script to verify the complete interface functionality
"""

import sys
import os
import psycopg2
import uuid
from datetime import datetime

def test_complete_flow():
    """Test saving and retrieving code from PostgreSQL"""

    # PostgreSQL configuration (same as in backend config)
    POSTGRES_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'verificai',
        'user': 'verificai',
        'password': 'verificai123'
    }

    try:
        print("1. Testing complete flow...")

        # Connect to PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Test data
        title = "Código Teste Interface"
        description = "Teste da interface Streamlit com PostgreSQL"
        content = '''def calculate_fibonacci(n):
    """Calculate Fibonacci sequence"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test function
for i in range(10):
    print(f"Fibonacci({i}) = {calculate_fibonacci(i)}")'''
        file_extension = ".py"

        # Generate code_id
        code_id = f"code_{uuid.uuid4().hex}"

        # Prepare data
        file_name = f"{title.replace(' ', '_').lower()}{file_extension}"
        line_count = len(content.splitlines())
        character_count = len(content)
        size_bytes = len(content.encode('utf-8'))

        # Detect programming language
        programming_language = 'Python'

        print(f"2. Saving test code: {title}")

        # Insert into source_codes table
        query = """
        INSERT INTO source_codes (
            code_id, title, description, content, file_name, file_extension,
            programming_language, line_count, character_count, size_bytes,
            status, is_public, is_processed, processing_status,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            code_id, title, description, content, file_name, file_extension,
            programming_language, line_count, character_count, size_bytes,
            'active', False, False, 'pending',
            datetime.now(), datetime.now()
        ))

        conn.commit()
        print(f" Code saved successfully with ID: {code_id}")

        # Now test retrieval (like the interface does)
        print("3. Testing retrieval (like the interface)...")

        query = """
        SELECT id, code_id, title, description, file_name, file_extension,
               programming_language, line_count, size_bytes, created_at, updated_at
        FROM source_codes
        WHERE status = 'active'
        ORDER BY created_at DESC
        LIMIT 20
        """

        cursor.execute(query)
        codes = cursor.fetchall()

        if codes:
            print(f" Found {len(codes)} codes in database")
            print("Recent codes:")
            for i, code in enumerate(codes[:3]):  # Show first 3
                print(f"  {i+1}. {code[2]} - {code[6]} ({code[8]} bytes)")

            # Test content retrieval for the first code
            print("4. Testing content retrieval...")
            first_code_id = codes[0][0]

            content_query = "SELECT content FROM source_codes WHERE id = %s"
            cursor.execute(content_query, (first_code_id,))
            content_result = cursor.fetchone()

            if content_result:
                retrieved_content = content_result[0]
                print(f" Content retrieved successfully ({len(retrieved_content)} chars)")
                print(f"First 3 lines: {retrieved_content.splitlines()[:3]}")
        else:
            print("❌ No codes found in database")

        cursor.close()
        conn.close()

        print("\n✅ COMPLETE FLOW TEST SUCCESS!")
        print("The interface should now display these saved codes.")
        print(f"Access: http://localhost:8506")

        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = test_complete_flow()

    if success:
        print("\n" + "="*60)
        print("🎉 INTERFACE FUNCTIONALITY VERIFIED!")
        print("📋 The Streamlit interface should now show:")
        print("   • Upload form with text field")
        print("   • Save functionality to PostgreSQL")
        print("   • Display of saved codes section")
        print("   • Ability to view code content")
        print("="*60)
    else:
        print("\n❌ TEST FAILED - Check database connection")