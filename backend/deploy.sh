#!/bin/bash

# VerificAI Backend Deployment Script
# This script automates the deployment process

set -e

# Configuration
PROJECT_NAME="verificai-backend"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    log "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    log "Docker Compose is installed"
}

# Build Docker image
build_image() {
    log "Building Docker image..."
    docker build -t ${PROJECT_NAME}:${IMAGE_TAG} .
    docker tag ${PROJECT_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}
    log "Docker image built successfully"
}

# Push image to registry
push_image() {
    log "Pushing image to registry..."
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}
    log "Image pushed successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    docker-compose run --rm api alembic upgrade head
    log "Database migrations completed"
}

# Deploy the application
deploy() {
    log "Deploying ${PROJECT_NAME} to ${ENVIRONMENT}..."

    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose down

    # Pull latest images
    log "Pulling latest images..."
    docker-compose pull

    # Start services
    log "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30

    # Run migrations
    run_migrations

    # Check health
    log "Checking service health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ API service is healthy"
    else
        error "❌ API service is not healthy"
    fi

    log "🚀 Deployment completed successfully!"
}

# Rollback deployment
rollback() {
    local rollback_tag=$1
    if [ -z "$rollback_tag" ]; then
        error "Rollback tag is required"
    fi

    log "Rolling back to version ${rollback_tag}..."

    # Stop current deployment
    docker-compose down

    # Pull rollback image
    docker pull ${DOCKER_REGISTRY}/${PROJECT_NAME}:${rollback_tag}

    # Update docker-compose to use rollback tag
    sed -i.bak "s/${PROJECT_NAME}:${IMAGE_TAG}/${PROJECT_NAME}:${rollback_tag}/g" docker-compose.yml

    # Start services
    docker-compose up -d

    # Wait for services
    sleep 30

    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Rollback completed successfully"
    else
        error "❌ Rollback failed"
    fi

    # Restore original docker-compose.yml
    mv docker-compose.yml.bak docker-compose.yml
}

# Show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Cleanup unused resources
cleanup() {
    log "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    log "Cleanup completed"
}

# Show help
show_help() {
    echo "VerificAI Backend Deployment Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  deploy                  Deploy the application"
    echo "  build                   Build Docker image"
    echo "  push                    Push image to registry"
    echo "  rollback <tag>          Rollback to specific version"
    echo "  logs [service]           Show logs for all or specific service"
    echo "  cleanup                 Cleanup unused Docker resources"
    echo "  health                  Check service health"
    echo "  help                    Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DOCKER_REGISTRY         Docker registry URL"
    echo "  IMAGE_TAG              Image tag to deploy"
    echo "  ENVIRONMENT            Deployment environment"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 rollback v1.0.0"
    echo "  $0 logs api"
    echo "  ENVIRONMENT=staging IMAGE_TAG=v1.0.0 $0 deploy"
}

# Check service health
check_health() {
    log "Checking service health..."

    # Check API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ API is healthy"
    else
        error "❌ API is not healthy"
    fi

    # Check Database
    if docker-compose exec db pg_isready -U verificai -d verificai > /dev/null 2>&1; then
        log "✅ Database is healthy"
    else
        error "❌ Database is not healthy"
    fi

    # Check Redis
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log "✅ Redis is healthy"
    else
        error "❌ Redis is not healthy"
    fi
}

# Main script logic
main() {
    case "${1:-help}" in
        "deploy")
            check_docker
            check_docker_compose
            deploy
            ;;
        "build")
            check_docker
            build_image
            ;;
        "push")
            check_docker
            push_image
            ;;
        "rollback")
            check_docker
            check_docker_compose
            rollback "$2"
            ;;
        "logs")
            show_logs "$2"
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "health")
            check_docker
            check_docker_compose
            check_health
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"