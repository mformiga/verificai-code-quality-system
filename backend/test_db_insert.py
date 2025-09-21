#!/usr/bin/env python3
"""
Test script to verify database insertion works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prompt import GeneralAnalysisResult
from datetime import datetime
import json

def test_database_insert():
    """Test direct database insertion"""
    print("=== TESTING DATABASE INSERT ===")

    db = SessionLocal()

    try:
        # Create a simple test record
        test_result = GeneralAnalysisResult(
            analysis_name="Test Analysis - Direct Insert",
            criteria_count=1,
            user_id=1,
            criteria_results={"criteria_1": {"name": "Test Criterion", "content": "Test content"}},
            raw_response="Test raw response",
            model_used="test-model",
            usage={"input_tokens": 100, "output_tokens": 50},
            file_paths=json.dumps(["test_file.js"]),
            modified_prompt="Test prompt",
            processing_time="1.0s"
        )

        print("DEBUG: Adding test record to session...")
        db.add(test_result)

        print("DEBUG: Committing transaction...")
        db.commit()

        print("DEBUG: Refreshing record...")
        db.refresh(test_result)

        print(f"✓ Test record saved with ID: {test_result.id}")

        # Verify it was saved
        saved_result = db.query(GeneralAnalysisResult).filter(GeneralAnalysisResult.id == test_result.id).first()
        if saved_result:
            print(f"✓ Verification successful - found record with ID {saved_result.id}")
            print(f"  Analysis name: {saved_result.analysis_name}")
            print(f"  Criteria count: {saved_result.criteria_count}")
            print(f"  Created at: {saved_result.created_at}")
        else:
            print("✗ Verification failed - record not found")

    except Exception as e:
        print(f"✗ Database insert failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    # Check total records
    db = SessionLocal()
    try:
        total_records = db.query(GeneralAnalysisResult).count()
        print(f"Total records in database: {total_records}")
    except Exception as e:
        print(f"Error counting records: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database_insert()