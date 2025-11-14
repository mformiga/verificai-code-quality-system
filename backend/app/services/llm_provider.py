"""
LLM provider service for VerificAI Backend
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import openai
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMResponse:
    """LLM response data structure"""

    def __init__(self, content: str, tokens_used: int = 0, model: str = "", usage: Dict[str, Any] = None):
        self.content = content
        self.tokens_used = tokens_used
        self.model = model
        self.usage = usage or {}


class LLMProvider:
    """Service for interacting with LLM providers"""

    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider()
        }
        self.token_optimizer = TokenOptimizer()

    async def analyze_code(
        self,
        prompt: str,
        code: str,
        provider: str = 'openai',
        temperature: float = 0.7,
        max_tokens: int = 32000  # Aumentado para acomodar análises completas
    ) -> LLMResponse:
        """Analyze code using specified LLM provider"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")

        return await self.providers[provider].analyze(prompt, code, temperature, max_tokens)

    async def analyze_with_fallback(
        self,
        prompt: str,
        code: str,
        preferred_provider: str = 'openai',
        temperature: float = 0.7,
        max_tokens: int = 32000  # Aumentado para acomodar análises completas
    ) -> LLMResponse:
        """Analyze with fallback between providers"""
        providers = [preferred_provider]

        # Add fallback providers
        if preferred_provider != 'openai':
            providers.append('openai')
        if preferred_provider != 'anthropic':
            providers.append('anthropic')

        for provider in providers:
            try:
                logger.info(f"Attempting analysis with provider: {provider}")
                response = await self.analyze_code(prompt, code, provider, temperature, max_tokens)
                logger.info(f"Successfully analyzed with {provider}")
                return response
            except Exception as e:
                logger.error(f"Failed to analyze with {provider}: {str(e)}")
                continue

        # All providers failed
        raise Exception("All LLM providers failed")

    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return self.token_optimizer.estimate_tokens(text)

    async def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                status[name] = {
                    'healthy': is_healthy,
                    'last_check': datetime.utcnow().isoformat()
                }
            except Exception as e:
                status[name] = {
                    'healthy': False,
                    'error': str(e),
                    'last_check': datetime.utcnow().isoformat()
                }
        return status


class OpenAIProvider:
    """OpenAI API provider"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL or "gpt-4-turbo-preview"

    async def analyze(self, prompt: str, code: str, temperature: float = 0.7, max_tokens: int = 32000) -> LLMResponse:
        """Analyze code using OpenAI"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": code}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=60
            )

            content = response.choices[0].message.content
            usage = response.usage

            return LLMResponse(
                content=content,
                tokens_used=usage.total_tokens,
                model=response.model,
                usage={
                    'prompt_tokens': usage.prompt_tokens,
                    'completion_tokens': usage.completion_tokens,
                    'total_tokens': usage.total_tokens
                }
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI API is healthy"""
        try:
            # Simple health check - list models
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return False


class AnthropicProvider:
    """Anthropic Claude provider"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20240229"

    async def analyze(self, prompt: str, code: str, temperature: float = 0.7, max_tokens: int = 32000) -> LLMResponse:
        """Analyze code using Anthropic Claude"""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")

        try:
            # Combine system prompt and user message
            full_prompt = f"{prompt}\n\n{code}"

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                timeout=60
            )

            content = response.content[0].text
            usage = response.usage

            return LLMResponse(
                content=content,
                tokens_used=usage.input_tokens + usage.output_tokens,
                model=response.model,
                usage={
                    'prompt_tokens': usage.input_tokens,
                    'completion_tokens': usage.output_tokens,
                    'total_tokens': usage.input_tokens + usage.output_tokens
                }
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check if Anthropic API is healthy"""
        try:
            # Simple health check - send a minimal message
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {str(e)}")
            return False


class TokenOptimizer:
    """Token optimization utilities"""

    def __init__(self):
        self.max_tokens = 32000  # Default context window limit - aumentado para evitar truncamento

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def optimize_code(self, code: str, language: str = "") -> str:
        """Optimize code for token usage"""
        # Remove comments
        optimized = self._remove_comments(code, language)

        # Minify whitespace
        optimized = self._minify_whitespace(optimized)

        # Remove empty lines
        optimized = self._remove_empty_lines(optimized)

        return optimized

    def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt for token usage"""
        # Remove redundant whitespace
        optimized = self._minify_whitespace(prompt)

        # Remove unnecessary formatting
        optimized = optimized.strip()

        return optimized

    def create_chunks(self, content: str, max_chunk_size: int = 2000) -> List[str]:
        """Split content into optimal chunks"""
        chunks = []
        current_chunk = ""
        lines = content.split('\n')

        for line in lines:
            # Check if adding this line would exceed the chunk size
            if len(current_chunk) + len(line) + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
            current_chunk += line + '\n'

        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def optimize_content(self, processed_files: List[Dict[str, Any]], max_tokens: int = 100000) -> str:
        """Optimize content from processed files"""
        optimized_content = ""

        for file_info in processed_files:
            file_path = file_info.get('path', '')
            file_content = file_info.get('content', '')
            language = file_info.get('language', '')

            # Optimize each file
            optimized_code = self.optimize_code(file_content, language)

            # Add file header
            optimized_content += f"\n\n// File: {file_path} ({language})\n"
            optimized_content += optimized_code

        return optimized_content.strip()

    def _remove_comments(self, code: str, language: str = "") -> str:
        """Remove comments from code"""
        # Simple comment removal (this is basic - in production you'd want language-specific parsers)
        lines = code.split('\n')
        optimized_lines = []

        for line in lines:
            # Remove single-line comments
            if language in ['python', 'javascript', 'typescript', 'java', 'c', 'cpp']:
                if '//' in line:
                    line = line.split('//')[0]
                elif '#' in line and language == 'python':
                    line = line.split('#')[0]

            # Remove empty comment lines
            line = line.strip()
            if line:
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def _minify_whitespace(self, text: str) -> str:
        """Minify whitespace in text"""
        # Replace multiple spaces with single space
        text = ' '.join(text.split())

        # Preserve line breaks for code readability
        return text

    def _remove_empty_lines(self, text: str) -> str:
        """Remove empty lines from text"""
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)