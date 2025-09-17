# 13. Monitoring and Observability

### 13.1 Logging Strategy

#### 13.1.1 Structured Logging

```python
# backend/app/core/logging_config.py
import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import os

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # Add custom fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'extra_data'):
            log_entry['extra_data'] = record.extra_data

        return json.dumps(log_entry)

def setup_logging():
    """Setup structured logging for the application"""
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # File handler with rotation
    if os.getenv('ENVIRONMENT') == 'production':
        file_handler = logging.handlers.RotatingFileHandler(
            '/var/log/verificai/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)

    # Set specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    return root_logger

class LoggerMixin:
    """Mixin class for adding logging to classes"""

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    def log_with_context(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log message with additional context"""
        log_method = getattr(self.logger, level.lower(), self.logger.info)

        kwargs = {'extra': extra} if extra else {}
        log_method(message, **kwargs)

@contextmanager
def log_operation(operation_name: str, logger: logging.Logger, **context):
    """Context manager for logging operation duration and results"""
    start_time = datetime.utcnow()
    logger.info(f"Starting operation: {operation_name}", extra=context)

    try:
        yield
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Completed operation: {operation_name}",
            extra={
                **context,
                'duration_seconds': duration,
                'status': 'success'
            }
        )
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"Failed operation: {operation_name}",
            extra={
                **context,
                'duration_seconds': duration,
                'status': 'error',
                'error': str(e)
            }
        )
        raise
```

#### 13.1.2 Request Logging Middleware

```python
# backend/app/middleware/request_logging.py
from fastapi import Request, Response
from fastapi.middleware import Middleware
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Generate request ID
        request_id = str(uuid.uuid4())
        scope['request_id'] = request_id

        # Extract user info if available
        user_id = getattr(request.state, 'user_id', None)
        session_id = getattr(request.state, 'session_id', None)

        # Log request start
        start_time = time.time()
        logger.info(
            "Incoming request",
            extra={
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'user_agent': request.headers.get('user-agent'),
                'user_id': user_id,
                'session_id': session_id
            }
        )

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Calculate request duration
                duration = time.time() - start_time
                status_code = message.get("status", 500)

                # Log request completion
                log_level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
                getattr(logger, log_level)(
                    "Request completed",
                    extra={
                        'request_id': request_id,
                        'method': request.method,
                        'url': str(request.url),
                        'status_code': status_code,
                        'duration_seconds': duration,
                        'user_id': user_id,
                        'session_id': session_id
                    }
                )

                # Add request ID to response headers
                headers = dict(message.get("headers", []))
                headers[b"X-Request-ID"] = request_id.encode()
                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)
```

### 13.2 Metrics and Monitoring

#### 13.2.1 Custom Metrics

```python
# backend/app/core/metrics.py
import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def record_gauge(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a gauge metric (current value)"""
        with self.lock:
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(point)

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Dict[str, str] = None
    ):
        """Increment a counter metric"""
        with self.lock:
            key = f"{name}:{self._tags_to_string(tags or {})}"
            self.counters[key] += value

    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a histogram metric (distribution of values)"""
        self.record_gauge(f"{name}.count", 1, tags)
        self.record_gauge(f"{name}.sum", value, tags)
        self.record_gauge(f"{name}.last", value, tags)

    def get_metric(
        self,
        name: str,
        since: datetime = None,
        tags: Dict[str, str] = None
    ) -> List[MetricPoint]:
        """Get metric points"""
        with self.lock:
            points = list(self.metrics[name])

            # Filter by time
            if since:
                points = [p for p in points if p.timestamp >= since]

            # Filter by tags
            if tags:
                points = [p for p in points if self._tags_match(p.tags, tags)]

            return points

    def get_counter(
        self,
        name: str,
        tags: Dict[str, str] = None
    ) -> int:
        """Get counter value"""
        with self.lock:
            key = f"{name}:{self._tags_to_string(tags or {})}"
            return self.counters.get(key, 0)

    def get_stats(
        self,
        name: str,
        since: datetime = None,
        tags: Dict[str, str] = None
    ) -> Dict[str, float]:
        """Get basic statistics for a metric"""
        points = self.get_metric(name, since, tags)

        if not points:
            return {}

        values = [p.value for p in points]

        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p50': self._percentile(values, 50),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }

    def _tags_to_string(self, tags: Dict[str, str]) -> str:
        """Convert tags to string for counter key"""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

    def _tags_match(self, metric_tags: Dict[str, str], filter_tags: Dict[str, str]) -> bool:
        """Check if metric tags match filter tags"""
        for key, value in filter_tags.items():
            if metric_tags.get(key) != value:
                return False
        return True

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

# Global metrics collector
metrics = MetricsCollector()

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Record request duration
                duration = time.time() - start_time
                status_code = message.get("status", 500)

                metrics.record_histogram(
                    "http_request_duration",
                    duration,
                    {
                        'method': request.method,
                        'status': str(status_code // 100) + 'xx',
                        'endpoint': request.url.path
                    }
                )

                # Increment request counter
                metrics.increment_counter(
                    "http_requests_total",
                    tags={
                        'method': request.method,
                        'status': str(status_code // 100) + 'xx'
                    }
                )

                # Record active requests
                metrics.increment_counter("http_requests_active", -1)

            await send(message)

        # Record active request
        metrics.increment_counter("http_requests_active")

        await self.app(scope, receive, send_wrapper)

# Performance monitoring decorator
def monitor_performance(metric_name: str, tags: Dict[str, str] = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        import asyncio

        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    metrics.record_histogram(
                        f"{metric_name}.success",
                        time.time() - start_time,
                        tags
                    )
                    return result
                except Exception as e:
                    metrics.record_histogram(
                        f"{metric_name}.error",
                        time.time() - start_time,
                        {**(tags or {}), 'error': type(e).__name__}
                    )
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    metrics.record_histogram(
                        f"{metric_name}.success",
                        time.time() - start_time,
                        tags
                    )
                    return result
                except Exception as e:
                    metrics.record_histogram(
                        f"{metric_name}.error",
                        time.time() - start_time,
                        {**(tags or {}), 'error': type(e).__name__}
                    )
                    raise
            return sync_wrapper
    return decorator
```

### 13.3 Health Checks

```python
# backend/app/core/health.py
from fastapi import FastAPI, Request, Response
from sqlalchemy import text
from typing import Dict, Any
import asyncio
import redis
import logging
from ..database.connection import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.checks = {}
        self.healthy = True

    def add_check(self, name: str, check_func):
        """Add a health check function"""
        self.checks[name] = check_func

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'timestamp': '2023-01-01T00:00:00Z'
                }
                if not result:
                    overall_healthy = False
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': '2023-01-01T00:00:00Z'
                }
                overall_healthy = False

        self.healthy = overall_healthy

        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'checks': results,
            'timestamp': '2023-01-01T00:00:00Z'
        }

# Global health checker
health_checker = HealthChecker()

def setup_health_checks(app: FastAPI):
    """Setup health check endpoints"""

    @app.get("/health")
    async def health_check():
        """Basic health check"""
        return await health_checker.run_checks()

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check - includes dependencies"""
        return await health_checker.run_checks()

    @app.get("/health/live")
    async def liveness_check():
        """Liveness check - basic application health"""
        return {
            'status': 'healthy',
            'timestamp': '2023-01-01T00:00:00Z'
        }

# Health check functions
async def check_database():
    """Check database connectivity"""
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception:
        return False

async def check_redis():
    """Check Redis connectivity"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
        return redis_client.ping()
    except Exception:
        return False

async def check_llm_providers():
    """Check LLM provider availability"""
    try:
        # Try to connect to at least one LLM provider
        # This is a simplified check - in production, you might want to test actual API calls
        return True
    except Exception:
        return False

async def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        # Check if free space is at least 10% of total
        return free > total * 0.1
    except Exception:
        return False

async def check_memory_usage():
    """Check memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        # Check if memory usage is below 90%
        return memory.percent < 90
    except Exception:
        return True  # Fallback to healthy if we can't check

# Register health checks
health_checker.add_check("database", check_database)
health_checker.add_check("redis", check_redis)
health_checker.add_check("llm_providers", check_llm_providers)
health_checker.add_check("disk_space", check_disk_space)
health_checker.add_check("memory_usage", check_memory_usage)
```

---
