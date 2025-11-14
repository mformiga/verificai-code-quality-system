"""
LLM service for VerificAI Backend - Direct LLM API integration with global locking
"""

import os
import json
import re
import httpx
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import HTTPException, status

class LLMService:
    """Service for direct LLM API integration using Google Gemini with global request serialization"""

    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.api_key = "AIzaSyDmhnKGqN5FnF5BSIYMdTvYlswednA3wL0"
        self.primary_model = "gemini-2.5-pro"
        self.fallback_model = "gemini-2.5-flash"
        # Lock global para serializar completamente todas as solicitações LLM
        self._global_lock = asyncio.Lock()
        print("=== LLMService: Lock global inicializado para prevenir 429 rate limiting ===")

    async def send_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send prompt directly to LLM API with fallback logic and global serialization"""

        # BLOQUEO GLOBAL - Solo una solicitud LLM puede procesarse a la vez para evitar 429
        print("=== ESPERANDO LOCK GLOBAL DE LLM ===")
        async with self._global_lock:
            print("=== LOCK GLOBAL OBTENIDO - Iniciando solicitud LLM ===")
            try:
                return await self._execute_llm_request(prompt, **kwargs)
            finally:
                print("=== LIBERANDO LOCK GLOBAL DE LLM ===")

    async def _execute_llm_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute the actual LLM request with fallback logic"""
        headers = {
            "Content-Type": "application/json"
        }

        # Default parameters - AUMENTADO para evitar truncamento de análises longas
        max_output_tokens = kwargs.get("max_tokens", 200000)  # Aumentado para 200.000 tokens para analisar múltiplos critérios
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

        max_retries = 1  # Reducido para evitar múltiples reintentos rápidos
        base_delay = 15  # Aumentado significativamente para prevenir 429

        print(f"=== INICIANDO SOLICITUD LLM SERIALIZADA ===")
        print(f"Modelo primario: {self.primary_model}")
        print(f"Modelo fallback: {self.fallback_model}")
        print(f"Max reintentos por modelo: {max_retries}")
        print(f"Delay base: {base_delay} segundos (aumentado para prevenir 429)")

        # Esperar inicial antes de la primera solicitud para asegurar espacio entre solicitudes
        print(f"Esperando {base_delay} segundos antes de la primera solicitud...")
        await asyncio.sleep(base_delay)

        # Try primary model first
        primary_result = await self._try_model(prompt, self.primary_model, headers, payload, max_retries, base_delay)

        if primary_result:
            print(f"=== MODELO PRIMARIO EXITOSO: {primary_result['model']} ===")
            return self._process_successful_response(primary_result["result"], primary_result["model"])
        else:
            print(f"=== MODELO PRIMARIO FALLÓ: {self.primary_model} - INTENTANDO FALLBACK ===")

            # Espera prolongada antes de cambiar de modelo para evitar cualquier posibilidad de 429
            model_switch_delay = base_delay * 6  # 90 segundos de espera entre cambios de modelo
            print(f"ESPERA LARGA: Aguardando {model_switch_delay} segundos antes de intentar modelo fallback...")
            await asyncio.sleep(model_switch_delay)

            # Try fallback model
            fallback_result = await self._try_model(prompt, self.fallback_model, headers, payload, max_retries, base_delay)

            if fallback_result:
                print(f"=== MODELO FALLBACK EXITOSO: {fallback_result['model']} ===")
                return self._process_successful_response(fallback_result["result"], fallback_result["model"])
            else:
                print(f"=== AMBOS MODELOS FALLARON ===")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="El servicio de IA está temporalmente no disponible. Todos los modelos están sobrecargados. Por favor, espere varios minutos antes de intentar nuevamente."
                )

    async def _try_model(
        self,
        prompt: str,
        model: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        max_retries: int,
        base_delay: int
    ) -> Dict[str, Any]:
        """
        Tenta gerar análise usando um modelo específico com retry logic e espaçamento adequado.

        Args:
            prompt: Texto de entrada para análise
            model: Nome do modelo a ser usado
            headers: Headers da requisição HTTP
            payload: Payload da requisição
            max_retries: Número máximo de tentativas
            base_delay: Tempo base de espera em segundos

        Returns:
            Dicionário com a resposta da API

        Raises:
            Exception: Se todas as tentativas falharem
        """
        last_exception = None

        print(f"=== TENTANDO MODELO: {model} ===")
        print(f"Máximo de tentativas: {max_retries + 1}")

        for attempt in range(max_retries + 1):
            try:
                print(f"Tentativa {attempt + 1}/{max_retries + 1} para {model}")

                # SIEMPRE esperar antes de CADA intento (incluyendo el primero)
                # para garantizar espaciado máximo entre solicitudes y prevenir 429
                if attempt >= 0:  # Cambiado de > 0 a >= 0 para esperar también antes del primer intento
                    # Usar backoff exponencial muy conservador para evitar CUALQUIER posibilidad de 429
                    delay = base_delay * (2 ** attempt)  # Backoff exponencial conservador
                    print(f"ESPERA MÍNIMA OBLIGATORIA: Aguardando {delay} segundos antes del intento {attempt + 1}...")
                    await asyncio.sleep(delay)

                # Faz a requisição com timeout maior para evitar bloqueios
                async with httpx.AsyncClient(timeout=300.0) as client:
                    print(f"Enviando requisição para {model}...")
                    start_time = time.time()

                    response = await client.post(
                        f"{self.base_url}/{model}:generateContent?key={self.api_key}",
                        headers=headers,
                        json=payload
                    )

                    end_time = time.time()
                    print(f"Resposta recebida de {model} em {end_time - start_time:.2f}s: {response.status_code}")

                    if response.status_code == 200:
                        print(f"SUCESSO: {model} respondeu com sucesso na tentativa {attempt + 1}!")
                        result = response.json()
                        return {
                            "result": result,
                            "model": model
                        }

                    elif response.status_code == 429:
                        # Rate limit error - esperar MUCHO más tiempo antes de prosseguir
                        error_info = response.text
                        print(f"=== ERROR 429 RATE LIMIT DETECTADO en {model} ===")
                        print(f"Detalles del error: {error_info}")

                        if attempt == max_retries:
                            print(f"=== FALHA TOTAL: {model} atingiu rate limit após {max_retries + 1} tentativas ===")
                            print("=== ADVERTENCIA: Gemini API está saturada ===")
                            return None
                        else:
                            # Para rate limit 429, esperar TIEMPO EXTREMADAMENTE LARGO para asegurar que se resetee
                            rate_limit_delay = base_delay * 10  # 150 segundos de espera para errores 429
                            print(f"=== 429 DETECTADO: ESPERA EXTREMA de {rate_limit_delay} segundos para resetear rate limit ===")
                            print("=== Esto es necesario para evitar más errores 429 ===")
                            await asyncio.sleep(rate_limit_delay)
                            continue

                    elif response.status_code == 503:
                        # Service unavailable - servidor sobrecarregado
                        error_info = response.text
                        print(f"SERVIÇO INDISPONÍVEL (503) em {model}: {error_info}")

                        if attempt == max_retries:
                            print(f"FALHA: {model} sobrecarregado após {max_retries + 1} tentativas")
                            return None
                        else:
                            continue

                    elif response.status_code == 400:
                        error_data = response.json()
                        print(f"ERRO DE REQUISIÇÃO INVÁLIDA para {model}: {error_data}")
                        print(f"FALHA: Erro na requisição para {model} - não é recuperável")
                        return None

                    else:
                        error_info = response.text
                        print(f"ERRO INESPERADO {response.status_code} em {model}: {error_info}")
                        if attempt == max_retries:
                            print(f"FALHA: {model} falhou após todas as tentativas: {response.status_code}")
                            return None

            except httpx.TimeoutException as timeout_error:
                print(f"TIMEOUT em {model} (tentativa {attempt + 1}): {timeout_error}")
                last_exception = timeout_error
                if attempt < max_retries:
                    # Aguardar antes de tentar novamente em caso de timeout
                    timeout_delay = base_delay * 3
                    print(f"Aguardando {timeout_delay}s após timeout...")
                    await asyncio.sleep(timeout_delay)
                    continue
                else:
                    print(f"FALHA: {model} deu timeout após múltiplas tentativas")
                    return None

            except httpx.RequestError as e:
                print(f"ERRO DE REQUISIÇÃO em {model} (tentativa {attempt + 1}): {e}")
                last_exception = e
                if attempt < max_retries:
                    # Aguardar antes de tentar novamente em caso de erro de rede
                    network_delay = base_delay * 3
                    print(f"Aguardando {network_delay}s após erro de rede...")
                    await asyncio.sleep(network_delay)
                    continue
                else:
                    print(f"FALHA: {model} falhou após erros de rede múltiplos")
                    return None

            except Exception as e:
                print(f"ERRO em {model} (tentativa {attempt + 1}): {str(e)}")
                last_exception = e
                if attempt < max_retries:
                    continue
                else:
                    print(f"FALHA: {model} falhou após todas as tentativas: {str(e)}")
                    return None

        print(f"FALHA FINAL: Modelo {model} falhou após todas as tentativas")
        return None

    def _process_successful_response(self, result: Dict, model: str) -> Dict[str, Any]:
        """Process successful response from either primary or fallback model"""
        print(f"=== PROCESSING SUCCESSFUL RESPONSE FROM {model} ===")
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
            print(f"=== RESPONSE ANALYSIS ===")
            print(f"Response length: {len(response_text)} characters")
            print(f"Response preview (first 500 chars): {response_text[:500]}")
            print(f"Response preview (last 500 chars): {response_text[-500:] if len(response_text) > 500 else response_text}")
            print(f"Contains #FIM_ANALISE_CRITERIO#: {'#FIM_ANALISE_CRITERIO#' in response_text}")
            print(f"Contains #FIM#: {'#FIM#' in response_text}")
            print(f"=== END RESPONSE ANALYSIS ===")

            # Save raw response for debugging
            try:
                from pathlib import Path
                prompts_dir = Path(__file__).parent.parent.parent / "prompts"
                debug_response_path = prompts_dir / "debug_raw_response.txt"
                with open(debug_response_path, "w", encoding="utf-8") as f:
                    f.write(response_text)
                print(f"Raw response saved to: {debug_response_path}")
            except Exception as e:
                print(f"Failed to save debug response: {e}")

            # Save latest response to file
            self._save_latest_response(response_text)

            # Save raw response (without any processing)
            self._save_raw_response(response_text)

        return {
            "success": True,
            "response": response_text,
            "model": model,
            "usage": result.get("usageMetadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _filter_prompt_instructions(self, response: str) -> str:
        """Filter out prompt instruction messages from LLM responses"""
        print(f"=== FILTERING PROMPT INSTRUCTIONS ===")

        # Patterns to identify prompt instruction messages that should be removed
        instruction_patterns = [
            r'IMPORTANTE:\s*Ao finalizar a análise deste critério, inclua EXATAMENTE a tag[^#]*?#FIM_ANALISE_CRITERIO#',
            r'Esta tag marca o fim completo da análise do critério acima\.',
            r'Esta marcação indica que todos os aspectos técnicos foram abordados[^#]*?análise completa e detalhada\.',
            r'Esta estrutura garante que cada critério seja analisado de forma[^#]*?#FIM_ANALISE_CRITERIO#',
            r'Este é o marcador final que indica a conclusão[^#]*?análise técnica completa\.',
            r'Por favor, inclua exatamente esta tag ao final[^#]*?#FIM_ANALISE_CRITERIO#',
            r'Esta instrução é apenas para orientação[^#]*?não deve ser enviada pela LLM[^#]*?não faz sentido',
            r'\\*\\*IMPORTANTE:\\*\\*[^\\*]*?inclua EXATAMENTE a tag[^\\*]*?\\*\\*',
            r'Esta tag.*?marca o fim.*?análise.*?critério.*?acima',
            r'Esta marcação.*?indica que.*?aspectos técnicos.*?foram abordados',
            r'Esta estrutura.*?garante que.*?cada critério.*?seja analisado',
            r'Este é o marcador final.*?indica a conclusão.*?análise técnica',
        ]

        filtered_response = response

        # Apply each pattern to filter out instruction messages
        for pattern in instruction_patterns:
            filtered_response = re.sub(pattern, '', filtered_response, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)

        # Clean up extra whitespace and blank lines that might be left after filtering
        filtered_response = re.sub(r'\n\s*\n\s*\n', '\n\n', filtered_response)  # Reduce multiple blank lines
        filtered_response = filtered_response.strip()

        print(f"=== FILTERING COMPLETE ===")
        print(f"Original length: {len(response)}")
        print(f"Filtered length: {len(filtered_response)}")
        print(f"Removed {len(response) - len(filtered_response)} characters")
        print(f"=== END FILTERING ===")

        return filtered_response

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

        # Filter out prompt instruction messages
        response = self._filter_prompt_instructions(response)

        # Check for #FIM# tag first - this is the main completion indicator
        fim_tag_pos = response.find('#FIM#')
        if fim_tag_pos != -1:
            response = response[:fim_tag_pos]
            print(f"=== FOUND #FIM# TAG AT POSITION {fim_tag_pos} ===")
            print(f"Response is COMPLETE - all criteria processed")
            print(f"Truncated response length: {len(response)}")
            print(f"=== COMPLETE RESPONSE ===")
        else:
            # Fallback: Check for #FIM_ANALISE_TOTAL# tag (legacy)
            fim_total_tag_pos = response.find('#FIM_ANALISE_TOTAL#')
            if fim_total_tag_pos != -1:
                response = response[:fim_total_tag_pos]
                print(f"=== FOUND LEGACY #FIM_ANALISE_TOTAL# TAG AT POSITION {fim_total_tag_pos} ===")
                print(f"Truncated response length: {len(response)}")
                print(f"=== TRUNCATED RESPONSE ===")
            else:
                print(f"=== WARNING: NO FINAL TAG FOUND - #FIM# or #FIM_ANALISE_TOTAL# ===")
                print(f"Response ends with: {response[-200:] if len(response) > 200 else response}")
                print(f"=== END WARNING - RESPONSE MAY BE INCOMPLETE ===")

        # NOVO: Primeiro tenta extrair usando as tags #FIM_ANALISE_CRITERIO#
        criteria_results = self._extract_criteria_using_tags(response)

        # Se não encontrou tags, fallback para método original
        if not criteria_results:
            print("=== NO #FIM_ANALISE_CRITERIO# TAGS FOUND - FALLING BACK TO ORIGINAL PARSING ===")

            # Pattern to match markdown code blocks
            pattern = r'```(?:markdown|md)?\n(.*?)\n```'
            matches = re.findall(pattern, response, re.DOTALL)

            # Use the entire response (excluding code blocks) - code blocks contain examples, not analysis content
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

            criteria_results = {}
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

    def _extract_criteria_using_tags(self, response: str) -> Dict[str, str]:
        """Extract individual criteria analysis using #FIM_ANALISE_CRITERIO# tags"""
        print(f"=== EXTRACTING CRITERIA USING #FIM_ANALISE_CRITERIO# TAGS ===")

        criteria_results = {}

        # Verificar se há tags no response
        tag_count = response.count('#FIM_ANALISE_CRITERIO#')
        print(f"=== TAG COUNT: Found {tag_count} #FIM_ANALISE_CRITERIO# tags in response ===")

        if tag_count == 0:
            print("=== NO TAGS FOUND - Response does not contain #FIM_ANALISE_CRITERIO# ===")
            print("=== Response preview (first 1000 chars): ===")
            print(response[:1000])
            print("=== End of preview ===")
            return criteria_results

        # Find all #FIM_ANALISE_CRITERIO# tags and extract content between criteria headers and tags
        parts = response.split('#FIM_ANALISE_CRITERIO#')

        if len(parts) > 1:
            print(f"=== FOUND {len(parts) - 1} #FIM_ANALISE_CRITERIO# TAGS ===")

            # For each part (except the last one), extract the criteria content
            for i in range(len(parts) - 1):
                part = parts[i]
                print(f"=== PROCESSING CRITERIA PART {i+1} ===")
                print(f"Part preview: {part[:300]}")

                # Find the criteria header in this part
                # Look for "## Critério: [Nome]" format
                criteria_match = re.search(r'##\s*Crit[ée]rio\s*[:]\s*(.+?)\n', part, re.DOTALL)
                if not criteria_match:
                    # Fallback: try "## Critério N: [Nome]" format
                    criteria_match = re.search(r'##\s*Crit[ée]rio\s*\d+[:]\s*(.+?)\n', part, re.DOTALL)

                if criteria_match:
                    criteria_name = criteria_match.group(1).strip()
                    criteria_num = str(i + 1)

                    # Extract content from the header to the end of the part
                    header_end = criteria_match.end()
                    criteria_content = part[header_end:].strip()

                    # Clean up - remove any remaining tags and normalize whitespace
                    criteria_content = re.sub(r'#FIM_ANALISE_CRITERIO#', '', criteria_content).strip()
                    criteria_content = re.sub(r'\n\s*\n', '\n\n', criteria_content)  # Normalize multiple newlines

                    # Store the complete criteria analysis
                    criteria_results[f"criteria_{criteria_num}"] = {
                        "name": criteria_name,
                        "content": criteria_content
                    }

                    print(f"[OK] Extracted criteria: {criteria_name}")
                    print(f"   Content length: {len(criteria_content)} chars")
                    print(f"   Content preview: {criteria_content[:200]}...")
                else:
                    print(f"[ERROR] No criteria header found in part {i+1}")

            print(f"=== SUCCESSFULLY EXTRACTED {len(criteria_results)} CRITERIA USING TAGS ===")
            for key, value in criteria_results.items():
                print(f"   {key}: {value['name'][:50]}... ({len(value['content'])} chars)")
        else:
            print("=== NO #FIM_ANALISE_CRITERIO# TAGS FOUND ===")

        print(f"=== END TAG-BASED EXTRACTION ===")
        return criteria_results

    def _save_latest_response(self, response_text: str) -> None:
        """Save the latest LLM response to a file"""
        try:
            from pathlib import Path

            # Get the prompts directory
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
            prompts_dir.mkdir(exist_ok=True)

            # Save to latest_response.txt
            latest_response_path = prompts_dir / "latest_response.txt"

            with open(latest_response_path, "w", encoding="utf-8") as f:
                f.write(response_text)

            print(f"Latest LLM response saved to: {latest_response_path}")
            print(f"Response length: {len(response_text)} characters")

        except Exception as e:
            print(f"Error saving latest LLM response: {e}")

    def _save_raw_response(self, response_text: str) -> None:
        """Save the raw LLM response without any processing"""
        try:
            from pathlib import Path

            # Get the prompts directory
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
            prompts_dir.mkdir(exist_ok=True)

            # Save to raw_response.txt
            raw_response_path = prompts_dir / "raw_response.txt"

            with open(raw_response_path, "w", encoding="utf-8") as f:
                f.write(response_text)

            print(f"Raw LLM response saved to: {raw_response_path}")
            print(f"Raw response length: {len(response_text)} characters")

        except Exception as e:
            print(f"Error saving raw LLM response: {e}")

# Global instance
llm_service = LLMService()
# Force reload