"""
Prompt service for VerificAI Backend - Handles prompt manipulation and criteria insertion
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.prompt import PromptConfiguration
from app.models.prompt import GeneralCriteria

class PromptService:
    """Service for handling prompt operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_general_prompt(self, prompt_id: int = None) -> str:
        """Get the general prompt configuration from database"""
        try:
            if prompt_id:
                # Get specific prompt by ID
                prompt_config = self.db.query(PromptConfiguration).filter(
                    PromptConfiguration.id == prompt_id,
                    PromptConfiguration.is_active == True
                ).first()
            else:
                # Get the most recent general prompt configuration
                prompt_config = self.db.query(PromptConfiguration).filter(
                    PromptConfiguration.prompt_type == "general",
                    PromptConfiguration.is_active == True
                ).order_by(PromptConfiguration.updated_at.desc()).first()

            if prompt_config:
                return prompt_config.content
            else:
                # Return default prompt if no configuration found
                return self._get_default_general_prompt()

        except Exception as e:
            print(f"Error getting general prompt: {e}")
            return self._get_default_general_prompt()

    def get_selected_criteria(self, criteria_ids: List[str]) -> List[GeneralCriteria]:
        """Get selected criteria from database"""
        try:
            # Extract actual IDs from criteria_ids (format: "criteria_123")
            actual_ids = []
            for criteria_id in criteria_ids:
                if criteria_id.startswith("criteria_"):
                    actual_ids.append(int(criteria_id.replace("criteria_", "")))
                else:
                    try:
                        actual_ids.append(int(criteria_id))
                    except ValueError:
                        continue

            # Get criteria from database
            criteria = self.db.query(GeneralCriteria).filter(
                GeneralCriteria.id.in_(actual_ids),
                GeneralCriteria.is_active == True
            ).order_by(GeneralCriteria.order).all()

            return criteria

        except Exception as e:
            print(f"Error getting selected criteria: {e}")
            return []

    def insert_criteria_into_prompt(self, prompt: str, criteria: List[GeneralCriteria]) -> str:
        """Insert criteria into prompt at the # delimiter"""
        try:
            # Format criteria for insertion
            criteria_text = ""
            for i, criterion in enumerate(criteria, 1):
                criteria_text += f"{i}. {criterion.text}\n"

            # Look for # delimiter in prompt
            if "#" in prompt:
                # Replace the first occurrence of # with formatted criteria
                modified_prompt = prompt.replace("#", criteria_text.strip(), 1)
            else:
                # If no # found, append criteria to the end
                modified_prompt = prompt + f"\n\nCritérios a serem avaliados:\n{criteria_text}"

            return modified_prompt

        except Exception as e:
            print(f"Error inserting criteria into prompt: {e}")
            return prompt  # Return original prompt if error occurs

    def _get_default_general_prompt(self) -> str:
        """Get default general prompt"""
        return """
Você é um especialista em análise de código.

### CÓDIGO FONTE PARA ANÁLISE:
```typescript
[INSERIR CÓDIGO AQUI]
```

Analise o código acima com base nos seguintes critérios:

#

Para cada critério, forneça:
1. Uma avaliação clara sobre se o código atende ao critério
2. Nível de confiança (0.0-1.0)
3. Evidências específicas do código
4. Recomendações para melhoria, se aplicável

Forneça sua análise em um formato estruturado que inclua:
- Avaliação geral
- Avaliações individuais dos critérios
- Exemplos de código que apoiam suas conclusões
- Recomendações acionáveis

Formate sua resposta em markdown com a seguinte estrutura exata:

## Avaliação Geral
[Resumo geral da análise]

## Critério 1: [Nome do critério]
**Status:** [Conforme/Parcialmente Conforme/Não Conforme]
**Confiança:** [X.X]%

[Avaliação detalhada com evidências do código]

**Recomendações:**
- [Lista de recomendações específicas]

## Critério 2: [Nome do critério]
**Status:** [Conforme/Parcialmente Conforme/Não Conforme]
**Confiança:** [X.X]%

[Avaliação detalhada com evidências do código]

**Recomendações:**
- [Lista de recomendações específicas]

## Recomendações Gerais
[Lista de recomendações gerais]
"""

# Global instance function
def get_prompt_service(db: Session) -> PromptService:
    """Get prompt service instance"""
    return PromptService(db)