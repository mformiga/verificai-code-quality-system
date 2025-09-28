#!/usr/bin/env python3
"""
Test script to verify single criteria analysis fix
"""

import asyncio
import json
from app.services.llm_service import llm_service

def test_single_criteria_extraction():
    """Test that extract_markdown_content handles single criteria correctly"""

    # Simulate a response that should only have one criteria
    test_response = """
# Análise de Código

## Critério 1: O código deve seguir convenções de nomenclatura consistentes

**Status:** Conforme
**Confiança:** 85%

O código analisado apresenta boas práticas de nomenclatura, com nomes descritivos para variáveis e funções.

#FIM#
"""

    print("=== Testing Single Criteria Extraction ===")
    print(f"Input response length: {len(test_response)}")
    print(f"Input response preview: {test_response[:200]}...")

    # Extract content
    result = llm_service.extract_markdown_content(test_response)

    print(f"\n=== Extraction Results ===")
    print(f"Number of criteria found: {len(result['criteria_results'])}")
    print(f"Criteria keys: {list(result['criteria_results'].keys())}")

    for key, criteria in result['criteria_results'].items():
        print(f"\nCriteria {key}:")
        print(f"  Name: {criteria['name'][:50]}...")
        print(f"  Content preview: {criteria['content'][:100]}...")

    # Check if we got exactly one criteria (which is what we want for single criteria analysis)
    criteria_count = len(result['criteria_results'])
    if criteria_count == 1:
        print("\n[SUCCESS] Exactly 1 criteria found (correct for single analysis)")
    elif criteria_count > 1:
        print(f"\n[ISSUE] Found {criteria_count} criteria when expecting 1")
        print("This could indicate over-extraction is still happening")
    else:
        print(f"\n[ISSUE] Found {criteria_count} criteria - extraction may have failed")

    return criteria_count == 1

def test_multiple_criteria_extraction():
    """Test that extract_markdown_content handles multiple criteria correctly"""

    # Simulate a response with multiple criteria
    test_response = """
# Análise de Código

## Critério 1: O código deve seguir convenções de nomenclatura consistentes

**Status:** Conforme
**Confiança:** 85%

O código analisado apresenta boas práticas de nomenclatura.

## Critério 2: Funções e métodos devem ter documentação adequada

**Status:** Parcialmente Conforme
**Confiança:** 70%

Algumas funções estão sem documentação.

## Critério 3: O código deve ter tratamento adequado de erros

**Status:** Não Conforme
**Confiança:** 90%

Falta tratamento de erros em vários pontos.

#FIM#
"""

    print("\n=== Testing Multiple Criteria Extraction ===")
    print(f"Input response length: {len(test_response)}")

    # Extract content
    result = llm_service.extract_markdown_content(test_response)

    print(f"\n=== Extraction Results ===")
    print(f"Number of criteria found: {len(result['criteria_results'])}")
    print(f"Criteria keys: {list(result['criteria_results'].keys())}")

    criteria_count = len(result['criteria_results'])
    if criteria_count == 3:
        print("\n[SUCCESS] Exactly 3 criteria found (correct for multiple analysis)")
    elif criteria_count > 3:
        print(f"\n[ISSUE] Found {criteria_count} criteria when expecting 3")
        print("This indicates over-extraction is happening")
    else:
        print(f"\n[ISSUE] Found {criteria_count} criteria - extraction may have failed")

    return criteria_count == 3

if __name__ == "__main__":
    print("Testing criteria extraction fixes...")

    single_success = test_single_criteria_extraction()
    multiple_success = test_multiple_criteria_extraction()

    print(f"\n=== Summary ===")
    print(f"Single criteria test: {'[PASSED]' if single_success else '[FAILED]'}")
    print(f"Multiple criteria test: {'[PASSED]' if multiple_success else '[FAILED]'}")

    if single_success and multiple_success:
        print("\nAll tests passed! The fix should work correctly.")
    else:
        print("\nSome tests failed. Additional fixes may be needed.")