#!/bin/bash

# JobMate Setup Script
# Automatically detects Docker availability and environment

set -e  # Exit on any error

echo "🚀 JobMate Setup"
echo "================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}🔄 $1${NC}"
}

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        if docker ps &> /dev/null; then
            print_status "Docker is available and running"
            return 0
        else
            print_warning "Docker is installed but not running"
            return 1
        fi
    else
        print_warning "Docker is not available"
        return 1
    fi
}

# Check if we're in Docker container
is_docker_container() {
    if [ -f /.dockerenv ] || [ "${container:-}" != "" ]; then
        return 0
    else
        return 1
    fi
}

# Docker-based setup
setup_docker() {
    print_info "Setting up with Docker..."
    
    # Use docker-setup.sh if it exists
    if [ -f "./docker-setup.sh" ]; then
        ./docker-setup.sh "$@"
    else
        print_error "docker-setup.sh not found"
        return 1
    fi
}

# Manual setup
setup_manual() {
    print_info "Setting up manually..."
    
    # Check if Python is installed
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi

    # Setup virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated"

    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Dependencies installed"

    # Setup environment file
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from template..."
        cp env.example .env
        print_status "Environment file created"
        print_warning "Please edit .env file with your database credentials and API keys"
    else
        print_warning ".env file already exists"
    fi

    # Check database connectivity
    print_info "Checking database connectivity..."
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL client found"
    else
        print_warning "PostgreSQL client not found. Please install PostgreSQL"
    fi
    
    if command -v mongosh &> /dev/null; then
        print_status "MongoDB client found"
    elif command -v mongo &> /dev/null; then
        print_status "MongoDB client (legacy) found"
    else
        print_warning "MongoDB client not found. Please install MongoDB"
    fi

    # Initialize database
    case "${1:-setup}" in
        "init-db"|"full")
            print_info "Initializing database..."
            if [ -d "migrations" ]; then
                print_info "Running database migrations..."
                flask db upgrade
                print_status "Database migrations completed"
            else
                print_info "Initializing Flask migrations..."
                flask db init
                flask db migrate -m "Initial migration"
                flask db upgrade
                print_status "Database initialized"
            fi
            ;;
    esac

    # Seed database
    case "${1:-setup}" in
        "seed"|"full")
            print_info "Seeding database with test data..."
            python seed.py
            print_status "Database seeding completed"
            ;;
    esac

    # Run application
    case "${1:-setup}" in
        "run"|"full")
            print_info "Starting JobMate application..."
            echo ""
            echo "🔗 Access the application at: http://localhost:5002"
            echo ""
            echo "📋 Test Credentials:"
            echo "   Applicant: applicant@demo.com / password123"
            echo "   Recruiter: recruiter@demo.com / password123"
            echo ""
            echo "Press Ctrl+C to stop the application"
            echo ""
            
            python run.py
            ;;
    esac
}

# Main execution
main() {
    # Check if script is being run from the right directory
    if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "This script must be run from the JobMateRefactor root directory"
        exit 1
    fi

    # Check if we're inside a Docker container
    if is_docker_container; then
        print_info "Running inside Docker container"
        setup_manual "$@"
        return
    fi

    # Parse command and decide environment
    COMMAND="${1:-setup}"
    USE_DOCKER="${USE_DOCKER:-auto}"

    # Force Docker or manual mode
    if [ "$USE_DOCKER" = "true" ] || [ "$COMMAND" = "docker" ]; then
        if check_docker; then
            setup_docker "$@"
        else
            print_error "Docker was requested but is not available"
            exit 1
        fi
    elif [ "$USE_DOCKER" = "false" ] || [ "$COMMAND" = "manual" ]; then
        setup_manual "$@"
    else
        # Auto-detect
        if check_docker && [ -f "docker-compose.yml" ]; then
            print_info "Docker detected, using Docker setup"
            setup_docker "$@"
        else
            print_info "Using manual setup"
            setup_manual "$@"
        fi
    fi
}

# Show help
show_help() {
    echo "JobMate Setup Script"
    echo "Automatically detects Docker availability and environment"
    echo ""
    echo "Usage: ./setup.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup environment and dependencies (default)"
    echo "  init-db   - Initialize database and run migrations"
    echo "  seed      - Seed database with test data"
    echo "  run       - Start the application"
    echo "  full      - Complete setup: env + deps + db + seed + run"
    echo "  docker    - Force Docker mode"
    echo "  manual    - Force manual mode"
    echo "  help      - Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  USE_DOCKER=true   - Force Docker mode"
    echo "  USE_DOCKER=false  - Force manual mode"
    echo "  USE_DOCKER=auto   - Auto-detect (default)"
    echo ""
    echo "Examples:"
    echo "  ./setup.sh          # Auto-detect and setup"
    echo "  ./setup.sh full     # Complete setup"
    echo "  USE_DOCKER=true ./setup.sh full  # Force Docker"
    echo "  ./setup.sh manual full  # Force manual setup"
}

# Handle help command
if [ "${1:-}" = "help" ]; then
    show_help
    exit 0
fi

# Run main function
main "$@"
