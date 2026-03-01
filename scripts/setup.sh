#!/bin/bash
#
# FakePhoto.ai - Local Development Setup Script
# Usage: ./scripts/setup.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    REQUIRED_VERSION="3.11"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        log_error "Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION is installed"
}

# Check and install pip
check_pip() {
    log_info "Checking pip installation..."
    
    if ! command_exists pip3; then
        log_warning "pip not found. Installing pip..."
        python3 -m ensurepip --upgrade || {
            log_error "Failed to install pip. Please install pip manually."
            exit 1
        }
    fi
    
    pip3 install --upgrade pip
    log_success "pip is ready"
}

# Create virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        log_warning "Virtual environment already exists. Removing old environment..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    log_success "Virtual environment created"
}

# Install dependencies
install_deps() {
    log_info "Installing dependencies..."
    
    source venv/bin/activate
    
    pip install -r requirements.txt || {
        log_error "Failed to install requirements"
        exit 1
    }
    
    if [ -f "requirements-dev.txt" ]; then
        log_info "Installing development dependencies..."
        pip install -r requirements-dev.txt || {
            log_warning "Failed to install some development dependencies"
        }
    fi
    
    log_success "Dependencies installed"
}

# Install package in editable mode
install_package() {
    log_info "Installing FakePhoto.ai package..."
    
    source venv/bin/activate
    pip install -e . || {
        log_error "Failed to install package"
        exit 1
    }
    
    log_success "Package installed in editable mode"
}

# Setup environment file
setup_env() {
    log_info "Setting up environment configuration..."
    
    if [ -f ".env" ]; then
        log_warning ".env file already exists. Skipping..."
    else
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env from .env.example"
        else
            cat > .env << EOF
# API Keys (Required - at least one)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=debug
MAX_FILE_SIZE=50

# Optional: Redis URL for caching
# REDIS_URL=redis://localhost:6379/0
EOF
            log_success "Created .env file"
        fi
        
        log_warning "Please edit .env and add your API keys"
    fi
}

# Setup pre-commit hooks
setup_precommit() {
    if [ -f ".pre-commit-config.yaml" ]; then
        log_info "Setting up pre-commit hooks..."
        
        source venv/bin/activate
        
        if pip install pre-commit; then
            pre-commit install
            log_success "Pre-commit hooks installed"
        else
            log_warning "Could not install pre-commit"
        fi
    fi
}

# Create necessary directories
create_dirs() {
    log_info "Creating necessary directories..."
    
    mkdir -p uploads
    mkdir -p logs
    mkdir -p temp
    
    log_success "Directories created"
}

# Setup landing page (if Node.js is available)
setup_landing() {
    if [ -d "landing" ]; then
        log_info "Setting up landing page..."
        
        if command_exists node && command_exists npm; then
            cd landing
            npm install
            cd ..
            log_success "Landing page dependencies installed"
        else
            log_warning "Node.js not found. Landing page setup skipped."
        fi
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    source venv/bin/activate
    
    if pytest --version >/dev/null 2>&1; then
        if pytest -xvs; then
            log_success "All tests passed!"
        else
            log_warning "Some tests failed. Check the output above."
        fi
    else
        log_warning "pytest not found, skipping tests"
    fi
}

# Main function
main() {
    echo "======================================"
    echo "FakePhoto.ai - Development Setup"
    echo "======================================"
    echo ""
    
    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
    
    cd "$PROJECT_ROOT"
    
    # Run setup steps
    check_python
    check_pip
    setup_venv
    install_deps
    install_package
    setup_env
    setup_precommit
    create_dirs
    setup_landing
    
    # Optional: run tests
    read -p "Run tests? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    echo ""
    echo "======================================"
    log_success "Setup complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env and add your API keys"
    echo "  2. Activate virtual environment: source venv/bin/activate"
    echo "  3. Run the web interface: streamlit run src/app.py"
    echo "  4. Or use the CLI: python -m fakephoto --help"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"