#!/usr/bin/env python3
"""
Simple test script to verify PostgreSQL direct insertion works
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_postgres_direct_insert():
    """Test direct PostgreSQL insertion"""

    # Import PostgreSQL configuration from app.py
    try:
        import psycopg2
        import uuid
        from datetime import datetime

        # PostgreSQL configuration (same as in backend config)
        POSTGRES_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'verificai',
            'user': 'verificai',
            'password': 'verificai123'
        }

        print("Testing PostgreSQL direct insertion...")

        # Test data
        title = "Teste de Código Python"
        description = "Código de teste para salvar no PostgreSQL"
        content = '''def hello_world():
    """Simple hello world function"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()'''
        file_extension = ".py"

        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Generate code_id
        code_id = f"code_{uuid.uuid4().hex}"

        # Prepare data
        file_name = f"{title.replace(' ', '_').lower()}{file_extension}"
        line_count = len(content.splitlines())
        character_count = len(content)
        size_bytes = len(content.encode('utf-8'))

        # Detect programming language
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript React',
            '.ts': 'TypeScript', '.tsx': 'TypeScript React', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.go': 'Go',
            '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
            '.kt': 'Kotlin', '.sql': 'SQL', '.html': 'HTML',
            '.css': 'CSS', '.scss': 'SCSS', '.json': 'JSON',
            '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
            '.md': 'Markdown', '.txt': 'Plain Text', '.sh': 'Shell'
        }

        programming_language = language_map.get(file_extension, 'Unknown')

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
        cursor.close()
        conn.close()

        print(f"SUCCESS: Source code saved to PostgreSQL!")
        print(f"Code ID: {code_id}")
        print(f"Title: {title}")
        print(f"Language: {programming_language}")
        print(f"Lines: {line_count}")
        print(f"Size: {size_bytes} bytes")
        print(f"File: {file_name}")
        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = test_postgres_direct_insert()
    if success:
        print("\nPostgreSQL direct insertion is WORKING!")
        print("You can now save source code content directly to the database.")
    else:
        print("\nPostgreSQL direct insertion FAILED!")
        print("Check your database connection and table structure.")