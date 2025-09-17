# 10. Error Handling Strategy

### 10.1 Error Categories and Handling

#### 10.1.1 System Errors

```python
# backend/app/core/errors/base.py
from typing import Optional, Dict, Any
from enum import Enum

class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    DATABASE_ERROR = "database_error"
    FILE_PROCESSING_ERROR = "file_processing_error"
    LLM_ERROR = "llm_error"
    INTERNAL_ERROR = "internal_error"

class BaseError(Exception):
    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseError):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            status_code=422,
            details={"field": field} if field else {}
        )

class AuthenticationError(BaseError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHENTICATION_ERROR,
            status_code=401
        )

class AuthorizationError(BaseError):
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHORIZATION_ERROR,
            status_code=403
        )

class NotFoundError(BaseError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_type=ErrorType.NOT_FOUND_ERROR,
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class ExternalServiceError(BaseError):
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details={"service": service}
        )

class LLMError(BaseError):
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"LLM provider '{provider}' error: {message}",
            error_type=ErrorType.LLM_ERROR,
            status_code=502,
            details={"provider": provider}
        )
```

#### 10.1.2 Error Middleware

```python
# backend/app/middleware/error_handler.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import logging
import traceback
from typing import Dict, Any
from ..core.errors.base import BaseError, ErrorType

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    def create_error_response(error: BaseError) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "error": {
                "type": error.error_type.value,
                "message": error.message,
                "details": error.details
            },
            "success": False
        }

    @staticmethod
    async def handle_base_error(request: Request, error: BaseError) -> JSONResponse:
        """Handle application-specific errors"""
        logger.error(f"Application error: {error.error_type.value} - {error.message}")

        return JSONResponse(
            status_code=error.status_code,
            content=ErrorHandler.create_error_response(error)
        )

    @staticmethod
    async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        """Handle FastAPI validation errors"""
        logger.error(f"Validation error: {error.errors()}")

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": ErrorType.VALIDATION_ERROR.value,
                    "message": "Invalid request data",
                    "details": {"validation_errors": error.errors()}
                },
                "success": False
            }
        )

    @staticmethod
    async def handle_http_exception(request: Request, error: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        logger.error(f"HTTP exception: {error.status_code} - {error.detail}")

        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": error.detail,
                    "details": {}
                },
                "success": False
            }
        )

    @staticmethod
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": ErrorType.INTERNAL_ERROR.value,
                    "message": "An unexpected error occurred",
                    "details": {}
                },
                "success": False
            }
        )
```

### 10.2 Retry and Fallback Mechanisms

```python
# backend/app/core/utils/retry.py
import asyncio
import random
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_with_fallback(
    config: RetryConfig = None,
    fallback_function: Optional[Callable] = None
):
    """Decorator for retry with fallback functionality"""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                    if attempt < config.max_attempts - 1:
                        delay = _calculate_delay(config, attempt)
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed")

            # Try fallback function if available
            if fallback_function:
                try:
                    logger.info("Attempting fallback function")
                    return await fallback_function(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback function failed: {str(fallback_error)}")

            # Re-raise the last exception
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                    if attempt < config.max_attempts - 1:
                        delay = _calculate_delay(config, attempt)
                        asyncio.sleep(delay)
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed")

            # Try fallback function if available
            if fallback_function:
                try:
                    logger.info("Attempting fallback function")
                    return fallback_function(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback function failed: {str(fallback_error)}")

            # Re-raise the last exception
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def _calculate_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter"""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)

    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)

    return delay
```

### 10.3 Circuit Breaker Pattern

```python
# backend/app/core/utils/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Callable, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker moving to HALF_OPEN state")
                else:
                    raise self.expected_exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    async def _on_success(self):
        """Handle successful execution"""
        async with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker reset to CLOSED state")

    async def _on_failure(self):
        """Handle failed execution"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if (self.state == CircuitState.CLOSED and
                self.failure_count >= self.failure_threshold):
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker re-opened from HALF_OPEN state")
```

---
