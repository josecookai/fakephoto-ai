#!/bin/bash
#
# FakePhoto.ai - Deployment Helper Script
# Usage: ./scripts/deploy.sh [environment]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="fakephoto-ai"
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
ENVIRONMENT="${1:-staging}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Show usage
show_usage() {
    echo "Usage: $0 [environment] [options]"
    echo ""
    echo "Environments:"
    echo "  local       - Deploy locally using Docker Compose"
    echo "  staging     - Deploy to staging environment"
    echo "  production  - Deploy to production environment"
    echo "  vercel      - Deploy landing page to Vercel"
    echo "  railway     - Deploy to Railway"
    echo "  render      - Deploy to Render"
    echo "  fly         - Deploy to Fly.io"
    echo "  all         - Deploy to all production environments"
    echo ""
    echo "Options:"
    echo "  --skip-tests    Skip running tests before deployment"
    echo "  --build-only    Only build Docker image, don't deploy"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local                    # Run locally"
    echo "  $0 staging --skip-tests     # Deploy to staging without tests"
    echo "  $0 production               # Deploy to production"
    echo "  $0 vercel                   # Deploy landing page"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    if ! command_exists python3; then
        log_error "Python 3 not found"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        log_warning "Virtual environment not found. Running setup..."
        ./scripts/setup.sh
    fi
    
    source venv/bin/activate
    pytest -xvs || {
        log_error "Tests failed. Fix tests before deploying."
        exit 1
    }
    
    log_success "All tests passed"
}

# Build Docker image
build_docker() {
    log_info "Building Docker image..."
    
    if ! command_exists docker; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "latest")
    
    docker build -t "${PROJECT_NAME}:${VERSION}" -t "${PROJECT_NAME}:latest" . || {
        log_error "Docker build failed"
        exit 1
    }
    
    log_success "Docker image built: ${PROJECT_NAME}:${VERSION}"
}

# Deploy locally with Docker Compose
deploy_local() {
    log_info "Deploying locally with Docker Compose..."
    
    if ! command_exists docker-compose && ! command_exists "docker compose"; then
        log_error "Docker Compose not found"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    # Build and start services
    if command_exists docker-compose; then
        docker-compose -f docker-compose.dev.yml up --build -d
    else
        docker compose -f docker-compose.dev.yml up --build -d
    fi
    
    log_success "Local deployment complete!"
    echo ""
    echo "Services running at:"
    echo "  API:    http://localhost:8000"
    echo "  Web UI: http://localhost:8501"
}

# Deploy landing page to Vercel
deploy_vercel() {
    log_info "Deploying landing page to Vercel..."
    
    if ! command_exists vercel; then
        log_error "Vercel CLI not found. Install with: npm i -g vercel"
        exit 1
    fi
    
    if [ ! -d "landing" ]; then
        log_error "Landing directory not found"
        exit 1
    fi
    
    cd landing
    
    if [ "$ENVIRONMENT" == "production" ]; then
        vercel --prod
    else
        vercel
    fi
    
    cd ..
    log_success "Landing page deployed to Vercel!"
}

# Deploy to Railway
deploy_railway() {
    log_info "Deploying to Railway..."
    
    if ! command_exists railway; then
        log_info "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    if [ -z "$RAILWAY_TOKEN" ]; then
        log_error "RAILWAY_TOKEN not set. Please set your Railway token."
        exit 1
    fi
    
    railway login --token "$RAILWAY_TOKEN"
    railway up --service "${PROJECT_NAME}"
    
    log_success "Deployed to Railway!"
}

# Deploy to Render
deploy_render() {
    log_info "Deploying to Render..."
    
    if [ -z "$RENDER_API_KEY" ] || [ -z "$RENDER_SERVICE_ID" ]; then
        log_error "RENDER_API_KEY or RENDER_SERVICE_ID not set"
        exit 1
    fi
    
    curl -X POST \
        "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
        -H "accept: application/json" \
        -H "authorization: Bearer ${RENDER_API_KEY}" \
        -H "content-type: application/json"
    
    log_success "Triggered deployment on Render!"
}

# Deploy to Fly.io
deploy_fly() {
    log_info "Deploying to Fly.io..."
    
    if ! command_exists flyctl; then
        log_info "Installing Fly.io CLI..."
        curl -L https://fly.io/install.sh | sh
        export PATH="$HOME/.fly/bin:$PATH"
    fi
    
    if [ -z "$FLY_API_TOKEN" ]; then
        log_error "FLY_API_TOKEN not set. Please set your Fly.io token."
        exit 1
    fi
    
    flyctl deploy --remote-only
    
    log_success "Deployed to Fly.io!"
}

# Deploy to all production environments
deploy_all() {
    log_info "Deploying to all production environments..."
    
    read -p "Are you sure you want to deploy to ALL production environments? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    build_docker
    
    # Deploy to each platform
    deploy_railway
    deploy_render
    deploy_fly
    deploy_vercel
    
    log_success "All deployments complete!"
}

# Main function
main() {
    # Parse arguments
    SKIP_TESTS=false
    BUILD_ONLY=false
    
    for arg in "$@"; do
        case $arg in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --build-only)
                BUILD_ONLY=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
        esac
    done
    
    # Get environment
    ENVIRONMENT="${1:-local}"
    
    echo "======================================"
    echo "FakePhoto.ai - Deployment"
    echo "Environment: $ENVIRONMENT"
    echo "======================================"
    echo ""
    
    # Validate environment
    case $ENVIRONMENT in
        local|staging|production|vercel|railway|render|fly|all)
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            show_usage
            exit 1
            ;;
    esac
    
    # Run tests (unless skipped)
    if [ "$SKIP_TESTS" = false ] && [ "$ENVIRONMENT" != "local" ]; then
        run_tests
    fi
    
    # Build Docker image
    if [ "$BUILD_ONLY" = true ]; then
        build_docker
        exit 0
    fi
    
    # Deploy based on environment
    case $ENVIRONMENT in
        local)
            deploy_local
            ;;
        staging)
            build_docker
            deploy_railway
            ;;
        production)
            build_docker
            deploy_railway
            deploy_render
            deploy_fly
            ;;
        vercel)
            deploy_vercel
            ;;
        railway)
            build_docker
            deploy_railway
            ;;
        render)
            deploy_render
            ;;
        fly)
            deploy_fly
            ;;
        all)
            deploy_all
            ;;
    esac
    
    echo ""
    echo "======================================"
    log_success "Deployment complete!"
    echo "======================================"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Run main function
main "$@"