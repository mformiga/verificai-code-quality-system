"""
LLM service for VerificAI Backend - Direct LLM API integration
"""

import os
import json
import re
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import HTTPException, status

class LLMService:
    """Service for direct LLM API integration using Anthropic"""

    def __init__(self):
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")

        if not self.base_url or not self.auth_token:
            raise ValueError("ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN environment variables are required")

    async def send_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send prompt directly to LLM API"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Default parameters
        max_tokens = kwargs.get("max_tokens", 4000)
        temperature = kwargs.get("temperature", 0.7)

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"LLM API error: {response.text}"
                    )

                result = response.json()

                print(f"=== DEBUG LLM API RESPONSE ===")
                print(f"Response keys: {result.keys()}")
                print(f"Content: {result.get('content', 'NO_CONTENT_KEY')}")
                print(f"Full response structure: {type(result)}")
                for key, value in result.items():
                    print(f"  {key}: {type(value)} - {str(value)[:200] if value else 'None'}")
                print(f"=== END DEBUG LLM API RESPONSE ===")

                # Try different response formats based on the LLM provider
                response_text = ""

                # Try Anthropic format first
                content = result.get("content", [{}])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")

                # If empty, try other formats
                if not response_text:
                    # Try direct response field
                    response_text = result.get("response", "")

                    # Try choices format (OpenAI-like)
                    if not response_text and "choices" in result:
                        choices = result.get("choices", [])
                        if choices and len(choices) > 0:
                            response_text = choices[0].get("message", {}).get("content", "")

                    # Try data field
                    if not response_text:
                        response_text = result.get("data", "")

                    # Try text field directly
                    if not response_text:
                        response_text = result.get("text", "")

                if not response_text:
                    print("WARNING: Could not extract response text from any supported format")
                    print(f"Available keys: {list(result.keys())}")
                    for key, value in result.items():
                        print(f"  {key}: {type(value)} - {str(value)[:100] if value else 'None'}")
                else:
                    print(f"SUCCESS: Extracted response text of length {len(response_text)}")

                return {
                    "success": True,
                    "response": response_text,
                    "model": result.get("model", "claude-3-sonnet-20240229"),
                    "usage": result.get("usage", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM API request timed out"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calling LLM API: {str(e)}"
            )

    def extract_markdown_content(self, response: str) -> Dict[str, str]:
        """Extract content from markdown code blocks in LLM response"""
        print(f"=== EXTRACT_MARKDOWN_CONTENT CALLED ===")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response)}")
        print(f"Response first 200 chars: {response[:200]}")
        print(f"=== END EXTRACT_MARKDOWN_CONTENT CALL ===")

        import logging
        logger = logging.getLogger(__name__)

        # Debug: Log the raw response
        logger.info(f"=== DEBUG RAW RESPONSE ===")
        logger.info(f"Response length: {len(response)}")
        logger.info(f"Response preview: {response[:800]}")
        logger.info(f"=== END RAW RESPONSE ===")

        print(f"=== DEBUG RAW RESPONSE ===")
        print(f"Response length: {len(response)}")
        print(f"Response preview: {response[:800]}")
        print(f"=== END RAW RESPONSE ===")

        # Pattern to match markdown code blocks
        pattern = r'```(?:markdown|md)?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)

        # Use the content from code blocks if found, otherwise use entire response
        content = matches[0] if matches else response

        print(f"=== DEBUG EXTRACTED CONTENT ===")
        print(f"Content from code blocks: {bool(matches)}")
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:800]}")
        print(f"=== END EXTRACTED CONTENT ===")

        # Extract individual criteria from the content
        criteria_results = {}

        # Look for criteria sections
        criteria_pattern = r'##\s*Crit[ée]rio\s*(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*\d+|\n##\s*(?:Resultado|Recomendações)\s*(?:Geral|)|$)'
        criteria_matches = re.findall(criteria_pattern, content, re.DOTALL)

        print(f"=== DEBUG CRITERIA EXTRACTION ===")
        print(f"Criteria pattern: {criteria_pattern}")
        print(f"Criteria matches found: {len(criteria_matches)}")
        print(f"Criteria matches: {criteria_matches}")
        print(f"=== END CRITERIA EXTRACTION ===")

        # Also try a more flexible pattern
        if not criteria_matches:
            flexible_pattern = r'##\s*Crit[ée]rio\s*(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*\d+|\n##\s*(?:Resultado|Recomendações)\s*(?:Geral|)|\Z|$)'
            flexible_matches = re.findall(flexible_pattern, content, re.DOTALL)
            print(f"Flexible pattern matches: {flexible_matches}")
            criteria_matches = flexible_matches

        for i, match in enumerate(criteria_matches):
            # Handle different match lengths (3, 4, or 5 groups due to regex capturing)
            if len(match) >= 3:
                criteria_num, criteria_name, criteria_content = match[0], match[1], match[2]
            else:
                continue  # Skip invalid matches
            print(f"Processing criteria {i+1}: num={criteria_num}, name={criteria_name[:50]}...")
            criteria_results[f"criteria_{criteria_num}"] = {
                "name": criteria_name.strip(),
                "content": criteria_content.strip()
            }

        print(f"Final criteria_results: {criteria_results}")

        return {
            "criteria_results": criteria_results,
            "raw_response": response.strip()
        }

# Global instance
llm_service = LLMService()
# Force reload