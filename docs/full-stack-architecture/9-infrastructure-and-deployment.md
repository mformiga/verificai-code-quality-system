# 9. Infrastructure and Deployment

### 9.1 Container Architecture

#### 9.1.1 Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

#### 9.1.2 Docker Compose Development

```yaml
# docker-compose.yml (development)
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: verificai
      POSTGRES_USER: verificai
      POSTGRES_PASSWORD: verificai123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - verificai-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - verificai-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/static/uploads:/app/static/uploads
    networks:
      - verificai-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - verificai-network
    command: npm run dev

  # Celery Worker
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/static/uploads:/app/static/uploads
    networks:
      - verificai-network
    command: celery -A app.core.workers.celery_app worker --loglevel=info

  # Celery Beat (for scheduled tasks)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - verificai-network
    command: celery -A app.core.workers.celery_app beat --loglevel=info

volumes:
  postgres_data:

networks:
  verificai-network:
    driver: bridge
```

### 9.2 Production Deployment

#### 9.2.1 Kubernetes Deployment

```yaml
# infrastructure/kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: verificai-backend
  labels:
    app: verificai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: verificai-backend
  template:
    metadata:
      labels:
        app: verificai-backend
    spec:
      containers:
      - name: backend
        image: verificai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: verificai-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: verificai-secrets
              key: redis-url
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: verificai-backend-service
spec:
  selector:
    app: verificai-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

```yaml
# infrastructure/kubernetes/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: verificai-frontend
  labels:
    app: verificai-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: verificai-frontend
  template:
    metadata:
      labels:
        app: verificai-frontend
    spec:
      containers:
      - name: frontend
        image: verificai/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.verificai.example.com"
        - name: REACT_APP_WS_URL
          value: "wss://api.verificai.example.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"

---
apiVersion: v1
kind: Service
metadata:
  name: verificai-frontend-service
spec:
  selector:
    app: verificai-frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

### 9.3 CI/CD Pipeline

#### 9.3.1 GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]
        python-version: [3.11]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
        cache-dependency-path: backend/requirements.txt

    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Install backend dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run frontend tests
      working-directory: ./frontend
      run: |
        npm run type-check
        npm run lint
        npm run test:coverage

    - name: Run backend tests
      working-directory: ./backend
      run: |
        pytest tests/ --cov=app --cov-report=xml

    - name: Build frontend
      working-directory: ./frontend
      run: npm run build

    - name: Upload coverage reports
      if: matrix.node-version == '20.x'
      uses: codecov/codecov-action@v3
      with:
        files: ./frontend/coverage/lcov.info,./backend/coverage.xml
        flags: frontend,backend
        name: code-coverage

  security:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - uses: actions/checkout@v4

    - name: Run security audit
      working-directory: ./frontend
      run: npm audit --audit-level=moderate

    - name: Run backend security scan
      working-directory: ./backend
      run: |
        pip install bandit safety
        bandit -r app/
        safety check

  build-and-deploy:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Deploy to staging
      if: github.ref == 'refs/heads/develop'
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          cd /opt/verificai
          docker-compose pull
          docker-compose up -d

    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/verificai
          docker-compose pull
          docker-compose up -d
```

---
