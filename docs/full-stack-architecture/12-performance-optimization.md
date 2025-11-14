# 12. Performance Optimization

### 12.1 Frontend Performance

#### 12.1.1 Code Splitting and Lazy Loading

```typescript
// frontend/src/router.tsx
import { createBrowserRouter, createRoutesFromElements, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import MainLayout from './components/layout/MainLayout';
import LoadingSpinner from './components/common/Feedback/LoadingSpinner';

// Lazy loading for code splitting
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const CodeUploadPage = lazy(() => import('./pages/CodeUploadPage'));
const PromptConfigPage = lazy(() => import('./pages/PromptConfigPage'));
const GeneralAnalysisPage = lazy(() => import('./pages/GeneralAnalysisPage'));
const ArchitecturalAnalysisPage = lazy(() => import('./pages/ArchitecturalAnalysisPage'));
const BusinessAnalysisPage = lazy(() => import('./pages/BusinessAnalysisPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route
        index
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <DashboardPage />
          </Suspense>
        }
      />
      <Route
        path="upload"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <CodeUploadPage />
          </Suspense>
        }
      />
      <Route
        path="prompts"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <PromptConfigPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/general"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <GeneralAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/architectural"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <ArchitecturalAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/business"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <BusinessAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="settings"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <SettingsPage />
          </Suspense>
        }
      />
    </Route>
  )
);

export default router;
```

#### 12.1.2 Virtual Scrolling for Large Lists

```typescript
// frontend/src/components/features/Analysis/ResultsTable.tsx
import { FixedSizeList as List } from 'react-window';
import { useMemo } from 'react';
import type { AnalysisResult } from '../../types/analysis';

interface ResultsTableProps {
  results: AnalysisResult[];
  onSelectResult: (result: AnalysisResult) => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results, onSelectResult }) => {
  const sortedResults = useMemo(() => {
    return [...results].sort((a, b) => {
      // Sort by score descending, then by file name
      if (a.score && b.score) {
        return b.score - a.score;
      }
      if (a.score) return -1;
      if (b.score) return 1;
      return a.fileName?.localeCompare(b.fileName || '') || 0;
    });
  }, [results]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const result = sortedResults[index];

    return (
      <div
        style={style}
        className={`border-b border-gray-200 hover:bg-gray-50 cursor-pointer ${
          index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
        }`}
        onClick={() => onSelectResult(result)}
      >
        <div className="p-4">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">
                {result.fileName || 'Unnamed File'}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {result.analysisType} Analysis
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {result.score && (
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  result.score >= 8 ? 'bg-green-100 text-green-800' :
                  result.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {result.score.toFixed(1)}
                </span>
              )}
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                result.status === 'completed' ? 'bg-green-100 text-green-800' :
                result.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                result.status === 'failed' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {result.status}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Analysis Results ({results.length})
        </h2>
      </div>

      {results.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-gray-500">No analysis results available</p>
        </div>
      ) : (
        <List
          height={600}
          itemCount={sortedResults.length}
          itemSize={80}
          itemData={sortedResults}
          className="divide-y divide-gray-200"
        >
          {Row}
        </List>
      )}
    </div>
  );
};

export default ResultsTable;
```

#### 12.1.3 Image and Asset Optimization

```typescript
// frontend/src/utils/imageOptimization.ts
export class ImageOptimizer {
  private static readonly MAX_WIDTH = 800;
  private static readonly MAX_HEIGHT = 600;
  private static readonly QUALITY = 0.8;
  private static readonly MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

  static async optimizeImage(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          if (!ctx) {
            reject(new Error('Canvas context not available'));
            return;
          }

          // Calculate new dimensions
          let { width, height } = img;

          if (width > height) {
            if (width > this.MAX_WIDTH) {
              height = (height * this.MAX_WIDTH) / width;
              width = this.MAX_WIDTH;
            }
          } else {
            if (height > this.MAX_HEIGHT) {
              width = (width * this.MAX_HEIGHT) / height;
              height = this.MAX_HEIGHT;
            }
          }

          canvas.width = width;
          canvas.height = height;

          // Draw image on canvas
          ctx.drawImage(img, 0, 0, width, height);

          // Convert to blob with compression
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Failed to create blob'));
                return;
              }

              // Check if optimized image is still too large
              if (blob.size > this.MAX_FILE_SIZE) {
                // Further reduce quality
                const quality = this.MAX_FILE_SIZE / blob.size;
                canvas.toBlob(
                  (finalBlob) => {
                    if (!finalBlob) {
                      reject(new Error('Failed to create final blob'));
                      return;
                    }
                    resolve(URL.createObjectURL(finalBlob));
                  },
                  'image/jpeg',
                  quality * 0.8
                );
              } else {
                resolve(URL.createObjectURL(blob));
              }
            },
            'image/jpeg',
            this.QUALITY
          );
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = e.target?.result as string;
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  }

  static async getFileDimensions(file: File): Promise<{ width: number; height: number }> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.onload = () => {
          resolve({
            width: img.naturalWidth,
            height: img.naturalHeight
          });
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = e.target?.result as string;
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  }
}
```

### 12.2 Backend Performance

#### 12.2.1 Database Optimization

```python
# backend/app/database/optimization.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Index, text
import os

class DatabaseOptimizer:
    @staticmethod
    def create_optimized_engine(database_url: str):
        """Create optimized database engine"""
        return create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=30,
            echo=False,  # Set to True for debugging
            execution_options={
                "isolation_level": "READ COMMITTED",
                "autocommit": False
            }
        )

    @staticmethod
    def create_optimized_indexes():
        """Create optimized database indexes"""
        return [
            # Composite indexes for common query patterns
            Index('idx_analysis_sessions_user_created',
                  text("(user_id, created_at DESC)")),
            Index('idx_analysis_results_session_type_status',
                  text("(analysis_session_id, analysis_type, status)")),
            Index('idx_file_uploads_session_status',
                  text("(analysis_session_id, upload_status)")),

            # Partial indexes for active data
            Index('idx_active_sessions',
                  text("(status) WHERE status IN ('created', 'processing')")),
            Index('idx_recent_results',
                  text("(created_at) WHERE created_at > NOW() - INTERVAL '7 days'")),

            # Text search indexes
            Index('idx_configurations_search',
                  text("to_tsvector('english', prompt_content)"),
                  postgresql_using='gin')
        ]

    @staticmethod
    def optimize_query(query, limit=None, offset=None):
        """Apply common query optimizations"""
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query

    @staticmethod
    def get_paginated_query(query, page=1, per_page=20):
        """Get paginated query with count"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
```

#### 12.2.2 Caching Strategy

```python
# backend/app/core/services/cache_service.py
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import redis
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # Try to parse as JSON first, then as pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                try:
                    return pickle.loads(value.encode('latin1'))
                except:
                    return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_pickle: bool = False
    ) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            if use_pickle:
                serialized_value = pickle.dumps(value)
            else:
                try:
                    serialized_value = json.dumps(value, default=str)
                except TypeError:
                    serialized_value = pickle.dumps(value)
                    use_pickle = True

            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

    def cache_result(self, ttl: int = None, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(cache_key, result, ttl)

                return result
            return wrapper
        return decorator

# Usage example
cache_service = CacheService(os.getenv("REDIS_URL"))

@cache_service.cache_result(ttl=1800, key_prefix="analysis:")
async def get_analysis_results(session_id: str):
    # Database query logic
    pass
```

#### 12.2.3 Connection Pooling

```python
# backend/app/database/connection_pool.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import contextlib
import logging
import time
import os

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.pool_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'avg_connection_time': 0
        }
        self._setup_pool()

    def _setup_pool(self):
        """Setup connection pool with optimized settings"""
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=20,           # Number of permanent connections
            max_overflow=30,        # Additional connections when pool is full
            pool_pre_ping=True,     # Check connection before use
            pool_recycle=300,       # Recycle connections after 5 minutes
            pool_timeout=30,        # Wait time for connection
            echo=False,             # SQL logging
            connect_args={
                'connect_timeout': 10,
                'application_name': 'verificai-backend',
                'options': '-c timezone=utc'
            }
        )

    @contextlib.contextmanager
    def get_connection(self):
        """Get connection from pool with timing and error handling"""
        start_time = time.time()
        connection = None

        try:
            connection = self.engine.connect()
            connection_time = time.time() - start_time

            # Update pool statistics
            self.pool_stats['total_connections'] += 1
            self.pool_stats['active_connections'] += 1

            # Update average connection time
            if self.pool_stats['avg_connection_time'] == 0:
                self.pool_stats['avg_connection_time'] = connection_time
            else:
                self.pool_stats['avg_connection_time'] = (
                    self.pool_stats['avg_connection_time'] * 0.9 + connection_time * 0.1
                )

            yield connection

        except SQLAlchemyError as e:
            self.pool_stats['failed_connections'] += 1
            logger.error(f"Connection pool error: {e}")
            raise
        finally:
            if connection:
                connection.close()
                self.pool_stats['active_connections'] -= 1
                self.pool_stats['idle_connections'] += 1

    def get_pool_stats(self) -> dict:
        """Get current pool statistics"""
        pool = self.engine.pool
        return {
            **self.pool_stats,
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalidated': pool.invalidated()
        }

    def health_check(self) -> bool:
        """Check if connection pool is healthy"""
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Pool health check failed: {e}")
            return False

    def close_pool(self):
        """Close all connections in pool"""
        if self.engine:
            self.engine.dispose()
            logger.info("Connection pool closed")

# Global instance
pool_manager = ConnectionPoolManager(os.getenv("DATABASE_URL"))
```

---
