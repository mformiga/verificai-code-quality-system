# 5. External API Integrations

### 5.1 LLM Provider Integration

#### 5.1.1 LangChain Configuration

```python
# backend/app/core/services/llm_service.py
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any, List, Optional
import asyncio
import logging

class LLMService:
    def __init__(self):
        self.providers = {
            'openai': ChatOpenAI,
            'anthropic': ChatAnthropic,
            'google': ChatGoogleGenerativeAI
        }
        self.current_provider = 'openai'
        self.fallback_providers = ['anthropic', 'google']

    async def analyze_code(
        self,
        code: str,
        prompt: str,
        analysis_type: str,
        callback_handler: Optional[BaseCallbackHandler] = None
    ) -> str:
        """Analyze code using LLM with fallback mechanism"""

        for provider_name in [self.current_provider] + self.fallback_providers:
            try:
                provider = self._get_provider(provider_name)
                messages = self._build_messages(code, prompt, analysis_type)

                response = await asyncio.to_thread(
                    provider.invoke,
                    messages,
                    callbacks=[callback_handler] if callback_handler else None
                )

                return response.content

            except Exception as e:
                logging.error(f"Provider {provider_name} failed: {e}")
                continue

        raise RuntimeError("All LLM providers failed")

    def _get_provider(self, provider_name: str):
        """Get configured LLM provider instance"""
        provider_class = self.providers[provider_name]

        if provider_name == 'openai':
            return provider_class(
                model="gpt-4",
                temperature=0.1,
                max_tokens=4000
            )
        elif provider_name == 'anthropic':
            return provider_class(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                max_tokens=4000
            )
        elif provider_name == 'google':
            return provider_class(
                model="gemini-pro",
                temperature=0.1,
                max_tokens=4000
            )

    def _build_messages(self, code: str, prompt: str, analysis_type: str) -> List:
        """Build message structure for LLM"""
        system_message = SystemMessage(
            content=f"You are an expert code analyst specializing in {analysis_type} analysis."
        )

        human_message = HumanMessage(
            content=f"""{prompt}

Code to analyze:
```python
{code}
```

Please provide a detailed analysis following the specified criteria."""
        )

        return [system_message, human_message]
```

#### 5.1.2 Token Optimization Strategy

```python
# backend/app/core/utils/token_optimizer.py
import re
import tiktoken
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class TokenOptimizationResult:
    optimized_content: str
    token_count: int
    compression_ratio: float

class TokenOptimizer:
    def __init__(self, model: str = "gpt-4"):
        self.encoder = tiktoken.encoding_for_model(model)
        self.max_tokens = 8000  # Conservative limit
        self.target_tokens = 6000  # Target for optimization

    def optimize_code(self, code: str) -> TokenOptimizationResult:
        """Optimize code content for LLM processing"""
        original_tokens = len(self.encoder.encode(code))

        if original_tokens <= self.target_tokens:
            return TokenOptimizationResult(
                optimized_content=code,
                token_count=original_tokens,
                compression_ratio=1.0
            )

        # Apply optimization strategies
        optimized = self._apply_optimizations(code)
        final_tokens = len(self.encoder.encode(optimized))

        return TokenOptimizationResult(
            optimized_content=optimized,
            token_count=final_tokens,
            compression_ratio=final_tokens / original_tokens
        )

    def _apply_optimizations(self, code: str) -> str:
        """Apply multiple optimization strategies"""
        # Strategy 1: Remove comments
        code = self._remove_comments(code)

        # Strategy 2: Remove empty lines
        code = self._remove_empty_lines(code)

        # Strategy 3: Minify whitespace
        code = self._minify_whitespace(code)

        # Strategy 4: Remove imports if too large
        if len(self.encoder.encode(code)) > self.max_tokens:
            code = self._remove_imports(code)

        # Strategy 5: Split into chunks if still too large
        if len(self.encoder.encode(code)) > self.max_tokens:
            code = self._create_chunked_summary(code)

        return code

    def _remove_comments(self, code: str) -> str:
        """Remove single-line and multi-line comments"""
        # Remove single-line comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _remove_empty_lines(self, code: str) -> str:
        """Remove excessive empty lines"""
        return re.sub(r'\n\s*\n', '\n', code)

    def _minify_whitespace(self, code: str) -> str:
        """Reduce whitespace while preserving structure"""
        lines = code.split('\n')
        minified_lines = []

        for line in lines:
            # Remove leading/trailing whitespace but preserve indentation
            minified_line = line.rstrip()
            minified_lines.append(minified_line)

        return '\n'.join(minified_lines)

    def _remove_imports(self, code: str) -> str:
        """Remove import statements to save tokens"""
        lines = code.split('\n')
        filtered_lines = []
        skip_imports = False

        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                if not skip_imports:
                    filtered_lines.append("# [Imports section removed for token optimization]")
                    skip_imports = True
            else:
                skip_imports = False
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _create_chunked_summary(self, code: str) -> str:
        """Create a summary when code is too large"""
        lines = code.split('\n')
        total_lines = len(lines)

        # Take first 100 lines and last 50 lines
        header_lines = lines[:100]
        footer_lines = lines[-50:] if total_lines > 150 else []

        result = []
        result.extend(header_lines)

        if footer_lines:
            result.append(f"\n# ... {total_lines - len(header_lines) - len(footer_lines)} lines omitted ...")
            result.extend(footer_lines)

        return '\n'.join(result)
```

### 5.2 API Rate Limiting and Error Handling

```python
# backend/app/core/middleware/rate_limiter.py
from fastapi import Request, Response, HTTPException
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

class RateLimiter:
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)
        self.requests = {}

    async def __call__(self, request: Request, call_next):
        client_ip = get_remote_address(request)
        endpoint = request.url.path

        # Different limits for different endpoints
        if endpoint.startswith('/api/analysis'):
            limit = 10  # 10 requests per minute
        elif endpoint.startswith('/api/upload'):
            limit = 5   # 5 uploads per minute
        else:
            limit = 100 # General API calls

        current_time = time.time()
        key = f"{client_ip}:{endpoint}"

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests.get(key, [])
            if current_time - req_time < 60
        ]

        # Check limit
        if len(self.requests[key]) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        self.requests[key].append(current_time)

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

---
