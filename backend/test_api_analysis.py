#!/usr/bin/env python3
"""
Test script to simulate the complete API analysis process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.prompt_service import PromptService
from app.models.prompt import GeneralCriteria
import json
import time

def test_complete_analysis_flow():
    """Test the complete analysis flow with single criterion"""
    print("=== TESTING COMPLETE ANALYSIS FLOW ===")

    db = SessionLocal()
    prompt_service = PromptService(db)

    # Test with single criterion (ID: 64)
    print("\n1. Testing single criterion analysis (ID: 64)")
    criteria_ids = ["criteria_64"]
    file_paths = ["C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\example_code.js"]

    # Get selected criteria
    selected_criteria = prompt_service.get_selected_criteria(criteria_ids)
    print(f"Selected criteria count: {len(selected_criteria)}")
    for criterion in selected_criteria:
        print(f"  - ID: {criterion.id}, Text: {criterion.text[:60]}...")

    # Get prompt and insert criteria
    base_prompt = prompt_service.get_general_prompt(1)
    modified_prompt = prompt_service.insert_criteria_into_prompt(base_prompt, selected_criteria)

    print(f"\nModified prompt length: {len(modified_prompt)}")
    print("Modified prompt with criteria:")
    print("=" * 50)
    print(modified_prompt)
    print("=" * 50)

    # Test file content
    test_file_content = """
// Example JavaScript code for analysis
function calculateTotal(items) {
    let total = 0;
    for (let i = 0; i < items.length; i++) {
        total += items[i].price * items[i].quantity;
    }
    return total;
}

class UserService {
    constructor(database) {
        this.db = database;
    }

    async getUser(id) {
        try {
            const user = await this.db.query('SELECT * FROM users WHERE id = ?', [id]);
            return user[0];
        } catch (error) {
            console.error('Error getting user:', error);
            throw error;
        }
    }

    async saveUser(user) {
        // Business logic mixed with data access
        if (!user.email || !user.email.includes('@')) {
            throw new Error('Invalid email format');
        }

        const validationQuery = 'SELECT COUNT(*) as count FROM users WHERE email = ?';
        const existingUsers = await this.db.query(validationQuery, [user.email]);

        if (existingUsers[0].count > 0) {
            throw new Error('Email already exists');
        }

        const insertQuery = 'INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)';
        await this.db.query(insertQuery, [user.name, user.email, new Date()]);

        // Send welcome email
        this.sendWelcomeEmail(user);
    }

    sendWelcomeEmail(user) {
        // Email sending logic mixed in with user service
        console.log(`Sending welcome email to ${user.email}`);
        // In a real app, this would call an email service
    }
}
"""

    # Simulate LLM call (without actually calling it)
    print(f"\n2. Simulating LLM analysis...")
    print(f"File content length: {len(test_file_content)} characters")
    full_prompt = modified_prompt + '\n\n' + test_file_content
    print(f"Total prompt length: {len(full_prompt)} characters")

    # Create a mock response to test parsing
    mock_llm_response = {
        "model": "claude-3-sonnet-20240229",
        "usage": {
            "input_tokens": 1500,
            "output_tokens": 800,
            "total_tokens": 2300
        },
        "content": """## Avaliação Geral
O código analisado apresenta alguns problemas de arquitetura, principalmente relacionados à separação de responsabilidades e violação de camadas.

## Critério 1: Violação de Camadas
**Status:** Não Conforme
**Confiança:** 0.9

O código apresenta clara violação de camadas, especialmente na classe `UserService`. O método `saveUser` mistura lógica de negócio (validação de email) com acesso a dados (queries SQL) e até mesmo lógica de comunicação (envio de email). Isso viola o princípio da separação de responsabilidades e cria um acoplamento inadequado entre camadas.

**Evidências:**
- A classe `UserService` contém queries SQL diretamente nos métodos
- Lógica de validação de negócio está misturada com persistência de dados
- O método `sendWelcomeEmail` está na mesma classe que manipula dados do usuário

**Recomendações:**
- Separar a lógica de acesso a dados em um repositório (UserRepository)
- Mover a lógica de validação para uma camada de serviço dedicada
- Criar um serviço de notificação separado para envio de emails
- Implementar um padrão de injeção de dependências para reduzir acoplamento

## Recomendações Gerais
- Refatorar o código seguindo os princípios de arquitetura limpa
- Implementar separação clara entre camadas de apresentação, serviço e dados
- Utilizar padrões de projeto como Repository e Service Layer
"""
    }

    print(f"\n3. Testing response parsing...")
    # Parse the mock response
    from app.api.v1.general_analysis import extract_criteria_results_from_response
    extracted_content = extract_criteria_results_from_response(mock_llm_response["content"], selected_criteria)

    print(f"Extracted criteria results: {len(extracted_content.get('criteria_results', {}))}")
    for key, result in extracted_content.get('criteria_results', {}).items():
        print(f"  - {key}: {result['name'][:50]}...")

    # Test database persistence
    print(f"\n4. Testing database persistence...")
    try:
        from app.models.prompt import GeneralAnalysisResult
        from datetime import datetime

        # Create analysis result
        analysis_result = GeneralAnalysisResult(
            analysis_name="Test Analysis - Single Criterion",
            criteria_count=len(selected_criteria),
            user_id=1,
            criteria_results=extracted_content.get("criteria_results", {}),
            raw_response=mock_llm_response["content"],
            model_used=mock_llm_response.get("model", "claude-3-sonnet-20240229"),
            usage=mock_llm_response.get("usage", {}),
            file_paths=json.dumps(file_paths),
            modified_prompt=modified_prompt,
            processing_time="2.5s"
        )

        db.add(analysis_result)
        db.commit()
        db.refresh(analysis_result)

        print(f"✓ Analysis result saved with ID: {analysis_result.id}")

        # Verify it was saved
        saved_result = db.query(GeneralAnalysisResult).filter(GeneralAnalysisResult.id == analysis_result.id).first()
        if saved_result:
            print(f"✓ Verified saved result has {len(saved_result.criteria_results)} criteria")
            print(f"✓ Analysis name: {saved_result.analysis_name}")
        else:
            print("✗ Failed to verify saved result")

    except Exception as e:
        print(f"✗ Database persistence failed: {e}")
        import traceback
        traceback.print_exc()

    db.close()

def test_endpoint_routing():
    """Test if the API endpoint is properly routed"""
    print("\n=== TESTING ENDPOINT ROUTING ===")

    # Check if the endpoint exists by importing the router
    try:
        from app.api.v1.general_analysis import router
        print("✓ General analysis router imported successfully")

        # Check route definitions
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                routes.append(f"{route.methods} {route.path}")

        print(f"Available routes: {routes}")
    except Exception as e:
        print(f"✗ Failed to import router: {e}")

    # Check main app routing
    try:
        from app.main import app
        print("✓ Main app imported successfully")

        # Check if the route is registered
        app_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                app_routes.append(f"{route.methods} {route.path}")

        print(f"Total app routes: {len(app_routes)}")
        general_analysis_routes = [r for r in app_routes if 'general-analysis' in r]
        print(f"General analysis routes: {general_analysis_routes}")

    except Exception as e:
        print(f"✗ Failed to check app routing: {e}")

def main():
    """Run all tests"""
    print("COMPLETE ANALYSIS FLOW TESTING")
    print("=" * 80)

    test_complete_analysis_flow()
    test_endpoint_routing()

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("\nNEXT STEPS:")
    print("1. Verify that frontend is sending correct criteria_ids")
    print("2. Check why database persistence might be failing in real API calls")
    print("3. Test the actual API endpoint with HTTP requests")
    print("4. Investigate routing issues if endpoints are not accessible")

if __name__ == "__main__":
    main()