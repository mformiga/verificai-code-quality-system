#!/usr/bin/env python3
"""
Comprehensive test script to analyze criteria selection and prompt construction issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.prompt_service import PromptService
from app.models.prompt import GeneralCriteria
import json

def test_criteria_selection():
    """Test criteria selection with different scenarios"""
    print("=== TESTING CRITERIA SELECTION ===")

    db = SessionLocal()
    prompt_service = PromptService(db)

    # Test 1: Single criterion selection
    print("\n1. Testing single criterion selection (ID: 64)")
    selected_criteria = prompt_service.get_selected_criteria(["criteria_64"])
    print(f"Selected criteria count: {len(selected_criteria)}")
    for criterion in selected_criteria:
        print(f"  - ID: {criterion.id}, Text: {criterion.text[:80]}...")

    # Test 2: Multiple criteria selection
    print("\n2. Testing multiple criteria selection (IDs: 64, 66)")
    selected_criteria = prompt_service.get_selected_criteria(["criteria_64", "criteria_66"])
    print(f"Selected criteria count: {len(selected_criteria)}")
    for criterion in selected_criteria:
        print(f"  - ID: {criterion.id}, Text: {criterion.text[:80]}...")

    # Test 3: Raw ID selection
    print("\n3. Testing raw ID selection (ID: 67)")
    selected_criteria = prompt_service.get_selected_criteria(["67"])
    print(f"Selected criteria count: {len(selected_criteria)}")
    for criterion in selected_criteria:
        print(f"  - ID: {criterion.id}, Text: {criterion.text[:80]}...")

    db.close()
    return selected_criteria

def test_prompt_construction():
    """Test prompt construction with criteria insertion"""
    print("\n=== TESTING PROMPT CONSTRUCTION ===")

    db = SessionLocal()
    prompt_service = PromptService(db)

    # Get base prompt
    base_prompt = prompt_service.get_general_prompt(1)
    print(f"Base prompt length: {len(base_prompt)}")
    print(f"Base prompt preview: {base_prompt[:200]}...")

    # Test with single criterion
    print("\n1. Testing prompt with single criterion (ID: 64)")
    selected_criteria = prompt_service.get_selected_criteria(["criteria_64"])
    modified_prompt = prompt_service.insert_criteria_into_prompt(base_prompt, selected_criteria)

    print(f"Modified prompt length: {len(modified_prompt)}")
    print(f"Modified prompt preview: {modified_prompt[:300]}...")

    # Find where criteria were inserted
    if "#" in base_prompt:
        hash_position = base_prompt.find("#")
        print(f"Hash position in base prompt: {hash_position}")

        # Show what was inserted
        criteria_section = modified_prompt[hash_position:hash_position + 500]
        print(f"Criteria section: {criteria_section}")

    db.close()
    return modified_prompt

def test_database_query():
    """Test database queries for criteria"""
    print("\n=== TESTING DATABASE QUERIES ===")

    db = SessionLocal()

    # Show all active criteria
    all_active = db.query(GeneralCriteria).filter(GeneralCriteria.is_active == True).all()
    print(f"All active criteria: {len(all_active)}")
    for criterion in all_active:
        print(f"  ID: {criterion.id}, Order: {criterion.order}, Text: {criterion.text[:60]}...")

    # Test specific query
    print("\nTesting query for IDs 64, 66, 67:")
    specific_criteria = db.query(GeneralCriteria).filter(
        GeneralCriteria.id.in_([64, 66, 67]),
        GeneralCriteria.is_active == True
    ).order_by(GeneralCriteria.order).all()

    print(f"Specific criteria count: {len(specific_criteria)}")
    for criterion in specific_criteria:
        print(f"  ID: {criterion.id}, Order: {criterion.order}")

    db.close()

def analyze_api_behavior():
    """Analyze how the API processes criteria_ids"""
    print("\n=== ANALYZING API BEHAVIOR ===")

    # Simulate different criteria_id formats that might be coming from frontend
    test_cases = [
        ["criteria_64"],  # Standard format
        ["64"],           # Raw ID
        ["criteria_64", "criteria_66"],  # Multiple standard
        ["64", "66"],                    # Multiple raw
        ["criteria_64", "66"],           # Mixed format
    ]

    db = SessionLocal()
    prompt_service = PromptService(db)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case}")
        selected_criteria = prompt_service.get_selected_criteria(test_case)
        print(f"  Result count: {len(selected_criteria)}")
        for criterion in selected_criteria:
            print(f"    - ID: {criterion.id}, Order: {criterion.order}")

    db.close()

def main():
    """Run all tests"""
    print("COMPREHENSIVE ANALYSIS OF CRITERIA SELECTION AND PROMPT CONSTRUCTION")
    print("=" * 80)

    test_criteria_selection()
    test_prompt_construction()
    test_database_query()
    analyze_api_behavior()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("\nRECOMMENDATIONS:")
    print("1. Check if frontend is sending correct criteria_ids format")
    print("2. Verify that only selected criteria are being processed")
    print("3. Ensure database persistence is working correctly")
    print("4. Test the complete flow from frontend to backend")

if __name__ == "__main__":
    main()