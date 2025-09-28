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
    """Service for direct LLM API integration using Google Gemini"""

    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.api_key = "AIzaSyDmhnKGqN5FnF5BSIYMdTvYlswednA3wL0"
        self.model = "gemini-2.5-pro"

    async def send_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send prompt directly to LLM API"""
        headers = {
            "Content-Type": "application/json"
        }

        # Default parameters
        max_output_tokens = kwargs.get("max_tokens", 16000)
        temperature = kwargs.get("temperature", 0.7)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_output_tokens,
                "temperature": temperature
            }
        }

        try:
            async with httpx.AsyncClient(timeout=1800.0) as client:
                response = await client.post(
                    f"{self.base_url}/{self.model}:generateContent?key={self.api_key}",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"LLM API error: {response.text}"
                    )

                result = response.json()

                print(f"=== DEBUG GEMINI API RESPONSE ===")
                print(f"Response keys: {result.keys()}")
                try:
                    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                except UnicodeEncodeError:
                    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False).encode('ascii', 'ignore').decode('ascii')[:500]}...")
                print(f"=== END DEBUG GEMINI API RESPONSE ===")

                # Extract response text from Gemini format
                response_text = ""

                # Gemini response format: candidates[0].content.parts[0].text
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                        response_text = candidate["content"]["parts"][0].get("text", "")

                if not response_text:
                    print("WARNING: Could not extract response text from Gemini response")
                    print(f"Available keys: {list(result.keys())}")
                    for key, value in result.items():
                        print(f"  {key}: {type(value)} - {str(value)[:100] if value else 'None'}")
                else:
                    print(f"SUCCESS: Extracted response text of length {len(response_text)}")

                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model,
                    "usage": result.get("usageMetadata", {}),
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

        # Check for #FIM# tag and truncate response at that point
        fim_tag_pos = response.find('#FIM#')
        if fim_tag_pos != -1:
            response = response[:fim_tag_pos]
            print(f"=== FOUND #FIM# TAG AT POSITION {fim_tag_pos} ===")
            print(f"Truncated response length: {len(response)}")
            print(f"=== TRUNCATED RESPONSE ===")
        else:
            print(f"=== WARNING: #FIM# TAG NOT FOUND ===")
            print(f"Response ends with: {response[-200:] if len(response) > 200 else response}")
            print(f"=== END WARNING ===")

        # Pattern to match markdown code blocks
        pattern = r'```(?:markdown|md)?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)

        # Use the entire response (excluding code blocks) - code blocks contain examples, not analysis
        if matches:
            # Remove code blocks from response as they contain code examples, not analysis content
            content = re.sub(r'```.*?\n.*?\n```', '', response, flags=re.DOTALL)
            content = content.strip()
        else:
            content = response

        print(f"=== DEBUG EXTRACTED CONTENT ===")
        print(f"Content from code blocks: {bool(matches)}")
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:800]}")
        print(f"=== END EXTRACTED CONTENT ===")

        # Extract individual criteria from the content
        criteria_results = {}

        # Look for criteria sections - handle both numbered and non-numbered formats, including exact format "## Critério: Nome"
        criteria_pattern = r'##\s*Crit[ée]rio\s*(?:(\d+(?:\.\d+)*)\s*[:]\s*)?(?:[:]\s*)?(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*(?:(?:\d+)\s*[:]?\s*)?(?:[:]\s*)?|\n##\s*(?:Resultado|Recomendações)\s*(?:Geral|)|#FIM#|$)'
        criteria_matches = re.findall(criteria_pattern, content, re.DOTALL)

        print(f"=== DEBUG CRITERIA EXTRACTION ===")
        print(f"Criteria pattern: {criteria_pattern}")
        print(f"Criteria matches found: {len(criteria_matches)}")
        print(f"Criteria matches: {criteria_matches}")
        print(f"=== END CRITERIA EXTRACTION ===")

        # Also try a more flexible pattern if no matches found
        if not criteria_matches:
            flexible_pattern = r'##\s*Crit[ée]rio\s*(?:(\d+(?:\.\d+)*)\s*[:\-]?\s*)?(?:[:]\s*)?(.+?)\n(.*?)(?=\n##\s*Crit[ée]rio\s*(?:(?:\d+)\s*[:\-]?\s*)?(?:[:]\s*)?|\n##\s*(?:Resultado|Recomendações)\s*(?:Geral|)|#FIM#|\Z|$)'
            flexible_matches = re.findall(flexible_pattern, content, re.DOTALL)
            print(f"Flexible pattern matches: {len(flexible_matches)}")
            criteria_matches = flexible_matches

        # If still no matches, try even more flexible pattern
        if not criteria_matches:
            print("Trying even more flexible pattern...")
            super_flexible_pattern = r'##\s*Crit[ée]rio\s*(\d+(?:\.\d+)*)[^\n]*\n+(.*?)(?=\n##\s*Crit[ée]rio\s*\d+|\n##\s*(?:Resultado|Recomendações)|#FIM#|$)'
            super_flexible_matches = re.findall(super_flexible_pattern, content, re.DOTALL)
            print(f"Super flexible pattern matches: {len(super_flexible_matches)}")

            # Reformat matches to expected structure
            criteria_matches = []
            for match in super_flexible_matches:
                criteria_num = match[0]
                rest_content = match[1]
                # Try to extract name and content
                name_match = re.search(r'^(.*?)(?=\*\*Status:\*\*|\n)', rest_content, re.DOTALL)
                if name_match:
                    criteria_name = name_match.group(1).strip()
                    criteria_content = rest_content[len(criteria_name):].strip()
                else:
                    # CRITICAL FIX: Don't use criteria_num directly as it might contain non-numeric values
                    # Instead, use a generic name or try to extract from first line
                    first_line = rest_content.split('\n')[0].strip()
                    if first_line and len(first_line) < 100 and not first_line.startswith('**'):
                        criteria_name = first_line
                    else:
                        criteria_name = f"Critério analisado"  # Generic fallback instead of using potentially broken criteria_num
                    criteria_content = rest_content
                criteria_matches.append((criteria_num, criteria_name, criteria_content))

        # LAST RESORT: Try to catch malformed criteria headers (like "## Critério criteria_2")
        if not criteria_matches:
            print("Trying last resort pattern for malformed criteria...")
            last_resort_pattern = r'##\s*Crit[ée]rio\s*(?::\s*)?([^\n]+?)\n+(.*?)(?=\n##\s*Crit[ée]rio|\n##\s*(?:Resultado|Recomendações)|#FIM#|$)'
            last_resort_matches = re.findall(last_resort_pattern, content, re.DOTALL)
            print(f"Last resort pattern matches: {len(last_resort_matches)}")

            criteria_matches = []
            for match in last_resort_matches:
                header_text = match[0].strip()
                rest_content = match[1]

                # Extract a clean criteria name from the header
                # Remove common prefixes and clean up
                clean_name = header_text
                for prefix in ['criteria_', 'critério ', 'criterion ', '##', ':', '']:
                    if clean_name.lower().startswith(prefix):
                        clean_name = clean_name[len(prefix):].strip()

                # Try to extract name from content if header cleanup didn't work well
                name_match = re.search(r'^(.*?)(?=\*\*Status:\*\*|\n)', rest_content, re.DOTALL)
                if name_match:
                    criteria_name = name_match.group(1).strip()
                    criteria_content = rest_content[len(criteria_name):].strip()
                else:
                    # Use cleaned header name or fallback
                    criteria_name = clean_name if clean_name and len(clean_name) > 2 else "Critério analisado"
                    criteria_content = rest_content

                criteria_matches.append(("1", criteria_name, criteria_content))  # Use "1" as default number

        # Check for actual duplicate criteria (not just similar length)
        # This helps prevent LLM duplication while allowing legitimate multiple criteria
        if len(criteria_matches) > 1:
            print(f"Multiple criteria matches found ({len(criteria_matches)}) - checking for actual duplicates")

            # Look for evidence of actual duplication
            unique_criteria_names = set()
            unique_criteria_content = set()
            for match in criteria_matches:
                if len(match) >= 3:
                    name = match[1].lower().strip()
                    content = match[2].lower()[:200]  # First 200 chars of content
                    unique_criteria_names.add(name)
                    unique_criteria_content.add(content)

            print(f"Unique criteria names found: {len(unique_criteria_names)}")
            print(f"Unique criteria content found: {len(unique_criteria_content)}")

            # Only deduplicate if names are actually identical (true duplicates)
            if len(unique_criteria_names) < len(criteria_matches):
                print(f"WARNING: Found duplicate criteria names - deduplicating")
                # Keep first occurrence of each unique name
                seen_names = set()
                deduplicated_matches = []
                for match in criteria_matches:
                    if len(match) >= 3:
                        name = match[1].lower().strip()
                        if name not in seen_names:
                            seen_names.add(name)
                            deduplicated_matches.append(match)
                criteria_matches = deduplicated_matches
                print(f"After deduplication: {len(criteria_matches)} criteria remain")

        # Final safety limit - allow multiple criteria as requested
        max_criteria = 10  # Allow up to 10 criteria to be processed
        if len(criteria_matches) > max_criteria:
            print(f"WARNING: Too many criteria matches found ({len(criteria_matches)}), limiting to first {max_criteria}")
            criteria_matches = criteria_matches[:max_criteria]

        for i, match in enumerate(criteria_matches):
            # Handle different match lengths - new format may have 3 groups (num_optional, name, content)
            print(f"Processing match {i}: {match}")
            print(f"Match length: {len(match)}")

            if len(match) >= 3:
                criteria_num_optional, criteria_name, criteria_content = match[0], match[1], match[2]
                # If criteria_num_optional is empty, use the match index + 1 as the criteria number
                if not criteria_num_optional:
                    criteria_num = str(i + 1)  # Use index + 1 to avoid duplicate keys
                else:
                    criteria_num = criteria_num_optional
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