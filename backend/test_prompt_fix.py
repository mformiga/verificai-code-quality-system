#!/usr/bin/env python3
"""
Test script to verify prompt adjustment for single criteria
"""

from app.core.database import get_db
from app.services.prompt_service import get_prompt_service
from app.models.prompt import GeneralCriteria

def test_single_criteria_prompt():
    """Test that prompt gets adjusted correctly for single criteria"""

    print("=== Testing Single Criteria Prompt Adjustment ===")

    # Get prompt service
    db = next(get_db())
    prompt_service = get_prompt_service(db)

    # Get the current prompt
    original_prompt = prompt_service.get_general_prompt(7)  # Using the active prompt
    print(f"Original prompt length: {len(original_prompt)}")
    print(f"Original prompt contains 'Critério 2': {'Critério 2' in original_prompt}")

    # Create a mock single criteria
    single_criteria = [GeneralCriteria(
        id=1,
        text="Código segue boas práticas e padrões de codificação",
        is_active=True,
        order=1,
        user_id=1
    )]

    # Insert criteria into prompt
    modified_prompt = prompt_service.insert_criteria_into_prompt(original_prompt, single_criteria)

    print(f"\nModified prompt length: {len(modified_prompt)}")
    print(f"Modified prompt contains 'Critério 2': {'Critério 2' in modified_prompt}")

    # Check if the adjustment worked
    criteria_count = modified_prompt.count("## Critério")
    print(f"Number of '## Critério' occurrences in modified prompt: {criteria_count}")

    # Show the relevant sections
    print("\n=== Relevant Sections ===")
    lines = modified_prompt.split('\n')
    in_criteria_section = False
    criteria_lines = []

    for line in lines:
        if "Critério 1:" in line:
            in_criteria_section = True
        if in_criteria_section:
            criteria_lines.append(line)
        if "## Recomendações Gerais" in line or "#FIM#" in line:
            break

    print('\n'.join(criteria_lines[:20]))  # Show first 20 lines of criteria section

    # Success criteria
    success = criteria_count <= 2  # Should have 1 or 2 (1 actual + possibly 1 in header)
    print(f"\n=== Result ===")
    if success:
        print("[SUCCESS] Prompt adjustment appears to work correctly")
    else:
        print("[ISSUE] Prompt still contains multiple criteria examples")

    return success

def test_multiple_criteria_prompt():
    """Test that prompt works correctly for multiple criteria"""

    print("\n=== Testing Multiple Criteria Prompt ===")

    # Get prompt service
    db = next(get_db())
    prompt_service = get_prompt_service(db)

    # Get the current prompt
    original_prompt = prompt_service.get_general_prompt(7)

    # Create mock multiple criteria
    multiple_criteria = [
        GeneralCriteria(id=1, text="Código segue boas práticas e padrões de codificação", is_active=True, order=1, user_id=1),
        GeneralCriteria(id=2, text="Funções e métodos devem ter documentação adequada", is_active=True, order=2, user_id=1),
        GeneralCriteria(id=3, text="O código deve ter tratamento adequado de erros", is_active=True, order=3, user_id=1)
    ]

    # Insert criteria into prompt
    modified_prompt = prompt_service.insert_criteria_into_prompt(original_prompt, multiple_criteria)

    criteria_count = modified_prompt.count("## Critério")
    print(f"Number of '## Critério' occurrences in modified prompt: {criteria_count}")

    # Success criteria - should show example structure for multiple criteria (at least 2 in the template)
    success = criteria_count >= 2  # Should have at least 2 examples in the structure
    print(f"\n=== Result ===")
    if success:
        print("[SUCCESS] Multiple criteria prompt structure maintained")
    else:
        print("[ISSUE] Multiple criteria prompt structure affected")

    return success

if __name__ == "__main__":
    print("Testing prompt adjustment fixes...")

    single_success = test_single_criteria_prompt()
    multiple_success = test_multiple_criteria_prompt()

    print(f"\n=== Summary ===")
    print(f"Single criteria test: {'[PASSED]' if single_success else '[FAILED]'}")
    print(f"Multiple criteria test: {'[PASSED]' if multiple_success else '[FAILED]'}")

    if single_success and multiple_success:
        print("\nAll prompt adjustment tests passed! The fix should work correctly.")
    else:
        print("\nSome tests failed. Additional fixes may be needed.")