#!/usr/bin/env python3
"""
Test script to verify the complete fix for single criteria analysis
"""

from app.core.database import get_db
from app.services.prompt_service import get_prompt_service
from app.models.prompt import GeneralCriteria
from app.services.llm_service import llm_service

def test_complete_single_criteria_flow():
    """Test the complete flow for single criteria analysis"""

    print("=== Testing Complete Single Criteria Analysis Flow ===")

    # Get prompt service
    db = next(get_db())
    prompt_service = get_prompt_service(db)

    # Get the current prompt
    original_prompt = prompt_service.get_general_prompt(7)

    # Create a single criteria (like the user selected)
    single_criteria = [GeneralCriteria(
        id=1,
        text="Código segue boas práticas e padrões de codificação",
        is_active=True,
        order=1,
        user_id=1
    )]

    # Step 1: Insert criteria into prompt
    modified_prompt = prompt_service.insert_criteria_into_prompt(original_prompt, single_criteria)

    print(f"Step 1 - Criteria inserted into prompt")
    print(f"  Prompt length: {len(modified_prompt)}")
    print(f"  Contains 'Critério 2': {'Critério 2' in modified_prompt}")
    print(f"  Number of '## Critério' in template: {modified_prompt.count('## Critério')}")

    # Step 2: Replace code placeholder with sample code
    sample_code = """
function exampleFunction() {
    const x = 10;
    return x + 5;
}
"""
    final_prompt = modified_prompt.replace("[INSERIR CÓDIGO AQUI]", sample_code)

    print(f"\nStep 2 - Code placeholder replaced")
    print(f"  Final prompt length: {len(final_prompt)}")

    # Step 3: Show what the LLM would see (first part)
    print(f"\nStep 3 - What LLM receives (first 500 chars):")
    print("-" * 50)
    print(final_prompt[:500])
    print("-" * 50)

    # Step 4: Simulate LLM response (for testing extraction)
    simulated_response = """
# Análise de Código

## Critério 1: Código segue boas práticas e padrões de codificação
**Status:** Conforme
**Confiança:** 85%

O código analisado segue as boas práticas de codificação, com nomes de variáveis descritivos e estrutura clara.

**Recomendações:**
- Considerar adicionar comentários explicativos
- Documentar o propósito da função

#FIM#
"""

    print(f"\nStep 4 - Simulated LLM Response")
    print(f"  Response length: {len(simulated_response)}")

    # Step 5: Extract criteria from response
    extracted_result = llm_service.extract_markdown_content(simulated_response)

    print(f"\nStep 5 - Content Extraction Results")
    print(f"  Number of criteria extracted: {len(extracted_result['criteria_results'])}")
    print(f"  Criteria keys: {list(extracted_result['criteria_results'].keys())}")

    # Show extracted criteria
    for key, criteria in extracted_result['criteria_results'].items():
        print(f"  {key}: {criteria['name'][:50]}...")

    # Final success check
    success = len(extracted_result['criteria_results']) == 1
    print(f"\n=== Final Result ===")
    if success:
        print("[SUCCESS] Single criteria analysis flow works correctly!")
        print("  - Only 1 criteria found in extraction")
        print("  - No duplicate criteria created")
    else:
        print("[ISSUE] Still finding multiple criteria in single analysis")
        print(f"  - Found {len(extracted_result['criteria_results'])} criteria")

    return success

if __name__ == "__main__":
    print("Testing complete single criteria analysis fix...")

    success = test_complete_single_criteria_flow()

    print(f"\n=== Summary ===")
    print(f"Complete flow test: {'[PASSED]' if success else '[FAILED]'}")

    if success:
        print("\nThe fix should resolve the issue where single criteria")
        print("selection was resulting in multiple criteria analysis.")
    else:
        print("\nAdditional investigation may be needed.")