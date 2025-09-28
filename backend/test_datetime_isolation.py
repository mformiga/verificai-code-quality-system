#!/usr/bin/env python3
"""
Test script to isolate the datetime error in the analysis function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prompt import GeneralCriteria
from datetime import datetime

def test_datetime_import():
    """Test if datetime import works"""
    try:
        print("Testing datetime import...")
        now = datetime.now()
        print(f"datetime.now() works: {now}")
        return True
    except Exception as e:
        print(f"Datetime import failed: {e}")
        return False

def test_database_query():
    """Test database query for criteria"""
    try:
        print("Testing database query...")
        db = SessionLocal()
        criteria = db.query(GeneralCriteria).filter(GeneralCriteria.id == 66).first()
        if criteria:
            print(f"Found criteria 66: {criteria.text[:100]}...")
            return True
        else:
            print("Criteria 66 not found")
            return False
    except Exception as e:
        print(f"Database query failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Testing components ===")

    # Test datetime import
    datetime_ok = test_datetime_import()

    # Test database query
    db_ok = test_database_query()

    print(f"\nResults:")
    print(f"Datetime import: {'OK' if datetime_ok else 'FAILED'}")
    print(f"Database query: {'OK' if db_ok else 'FAILED'}")

    if datetime_ok and db_ok:
        print("\nAll components work individually!")
    else:
        print("\nSome components failed!")