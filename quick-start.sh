#!/bin/bash

# VerificAI Quick Start Script
# Script para inicialização rápida do projeto com Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="verificai"
ENVIRONMENT="${ENVIRONMENT:-development}"

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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Por favor, inicie o Docker Desktop."
    fi
    log "✅ Docker está rodando"
}

# Check if required files exist
check_files() {
    local required_files=("docker-compose.yml" "frontend/Dockerfile" "backend/Dockerfile")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Arquivo requerido não encontrado: $file"
        fi
    done
    log "✅ Todos os arquivos requeridos existem"
}

# Stop existing containers
stop_existing() {
    info "Parando containers existentes..."
    docker-compose down --remove-orphans 2>/dev/null || true
    log "✅ Containers existentes parados"
}

# Build and start services
start_services() {
    info "Iniciando serviços do $PROJECT_NAME..."

    # Start database and redis first
    info "Iniciando banco de dados e cache..."
    docker-compose up -d postgres redis

    # Wait for database to be ready
    info "Aguardando banco de dados ficar pronto..."
    sleep 10

    # Start backend
    info "Iniciando backend..."
    docker-compose up -d backend

    # Wait for backend to be ready
    info "Aguardando backend ficar pronto..."
    sleep 15

    # Start frontend
    info "Iniciando frontend..."
    docker-compose up -d frontend

    log "✅ Todos os serviços iniciados"
}

# Show service URLs
show_urls() {
    echo ""
    echo -e "${GREEN}🚀 VerificAI está rodando!${NC}"
    echo ""
    echo -e "${BLUE}Serviços disponíveis:${NC}"
    echo -e "  • Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "  • Backend API: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  • Database: ${GREEN}localhost:5432${NC}"
    echo -e "  • Redis: ${GREEN}localhost:6379${NC}"
    echo ""
    echo -e "${YELLOW}Comandos úteis:${NC}"
    echo -e "  • Ver logs: ${GREEN}docker-compose logs -f [serviço]${NC}"
    echo -e "  • Parar tudo: ${GREEN}docker-compose down${NC}"
    echo -e "  • Reiniciar: ${GREEN}docker-compose restart [serviço]${NC}"
    echo ""
}

# Health check
health_check() {
    info "Verificando saúde dos serviços..."

    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Backend está saudável"
    else
        warn "⚠️  Backend ainda não está respondendo"
    fi

    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log "✅ Frontend está saudável"
    else
        warn "⚠️  Frontend ainda não está respondendo"
    fi
}

# Clean up unused resources
cleanup() {
    info "Limpando recursos Docker não utilizados..."
    docker system prune -f
    docker volume prune -f
    log "✅ Limpeza concluída"
}

# Show help
show_help() {
    echo "VerificAI Quick Start Script"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  start     Inicia todos os serviços"
    echo "  stop      Para todos os serviços"
    echo "  restart   Reinicia todos os serviços"
    echo "  logs      Mostra logs de todos os serviços"
    echo "  status    Verifica status dos serviços"
    echo "  cleanup   Limpa recursos Docker não utilizados"
    echo "  help      Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo "  $0 stop"
}

# Main script logic
main() {
    case "${1:-start}" in
        "start")
            check_docker
            check_files
            stop_existing
            start_services
            sleep 5
            health_check
            show_urls
            ;;
        "stop")
            info "Parando serviços..."
            docker-compose down
            log "✅ Serviços parados"
            ;;
        "restart")
            info "Reiniciando serviços..."
            docker-compose restart
            sleep 5
            health_check
            log "✅ Serviços reiniciados"
            ;;
        "logs")
            docker-compose logs -f "${2:-}"
            ;;
        "status")
            health_check
            docker-compose ps
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"