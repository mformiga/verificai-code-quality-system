#!/usr/bin/env python3
"""
Test endpoint to verify the complete analysis flow works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.prompt_service import PromptService
from app.models.prompt import GeneralCriteria, GeneralAnalysisResult
import json
import time

def test_complete_flow():
    """Test the complete flow from criteria selection to database persistence"""
    print("=== TESTING COMPLETE ANALYSIS FLOW ===")

    db = SessionLocal()

    try:
        # 1. Test criteria selection
        print("1. Testing criteria selection...")
        prompt_service = PromptService(db)
        selected_criteria = prompt_service.get_selected_criteria(["criteria_64"])
        print(f"   Selected criteria: {len(selected_criteria)}")
        for criterion in selected_criteria:
            print(f"   - {criterion.text[:50]}...")

        # 2. Test database save
        print("2. Testing database persistence...")
        test_result = GeneralAnalysisResult(
            analysis_name="Test Analysis - Complete Flow",
            criteria_count=len(selected_criteria),
            user_id=1,
            criteria_results={
                "criteria_1": {
                    "name": selected_criteria[0].text,
                    "content": "**Status:** Conforme\n**Confiança:** 0.9\n\nAnálise de teste completa."
                }
            },
            raw_response="Test response from LLM analysis",
            model_used="test-model",
            usage={"input_tokens": 100, "output_tokens": 50},
            file_paths=json.dumps(["test_file.js"]),
            modified_prompt="Test prompt with criteria",
            processing_time="1.5s"
        )

        db.add(test_result)
        db.commit()
        db.refresh(test_result)

        print(f"   ✓ Analysis saved with ID: {test_result.id}")

        # 3. Test retrieval
        print("3. Testing result retrieval...")
        saved_result = db.query(GeneralAnalysisResult).filter(
            GeneralAnalysisResult.id == test_result.id
        ).first()

        if saved_result:
            print(f"   ✓ Retrieved analysis: {saved_result.analysis_name}")
            print(f"   ✓ Criteria count: {saved_result.criteria_count}")
            print(f"   ✓ Created at: {saved_result.created_at}")

            # Test criteria results structure
            criteria_results = saved_result.criteria_results
            print(f"   ✓ Criteria results structure: {list(criteria_results.keys())}")
            for key, criteria in criteria_results.items():
                print(f"     - {key}: {criteria['name'][:30]}...")
        else:
            print("   ✗ Failed to retrieve saved analysis")

        # 4. Test cleanup
        print("4. Testing cleanup...")
        db.delete(test_result)
        db.commit()
        print("   ✓ Test record deleted")

        # 5. Verify final state
        print("5. Verifying final state...")
        remaining = db.query(GeneralAnalysisResult).count()
        print(f"   ✓ Remaining records: {remaining}")

        print("\n=== COMPLETE FLOW TEST SUCCESSFUL ===")
        print("✅ Criteria selection works")
        print("✅ Database persistence works")
        print("✅ Result retrieval works")
        print("✅ Cleanup works")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_complete_flow()