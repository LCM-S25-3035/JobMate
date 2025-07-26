#!/bin/bash

# JobMate Docker Setup Script
# This script sets up the entire development environment using Docker

set -e  # Exit on any error

echo "🐳 JobMate Docker Development Setup"
echo "==================================="

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

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d " " -f 3 | cut -d "," -f 1)
        print_status "Docker $DOCKER_VERSION found"
    else
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d " " -f 3 | cut -d "," -f 1)
        print_status "Docker Compose $COMPOSE_VERSION found"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check if Docker daemon is running
check_docker_daemon() {
    if docker info >/dev/null 2>&1; then
        print_status "Docker daemon is running"
    else
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
}

# Setup environment file
setup_env() {
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from template..."
        cp env.example .env
        print_status "Environment file created"
        print_warning "Please edit .env file with your API keys if needed"
    else
        print_warning ".env file already exists"
    fi
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    docker-compose build --no-cache
    print_status "Docker images built successfully"
}

# Start database services only
start_databases() {
    print_info "Starting database services..."
    docker-compose up -d postgres mongodb redis elasticsearch
    
    print_info "Waiting for databases to be ready..."
    sleep 10
    
    # Check PostgreSQL
    print_info "Checking PostgreSQL connection..."
    timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U jobmate_user -d jobmate_db; do sleep 2; done'
    print_status "PostgreSQL is ready"
    
    # Check MongoDB
    print_info "Checking MongoDB connection..."
    timeout 60 bash -c 'until docker-compose exec mongodb mongosh --eval "db.adminCommand(\"ping\")" --quiet; do sleep 2; done' || true
    print_status "MongoDB is ready"
    
    # Check Redis
    print_info "Checking Redis connection..."
    timeout 30 bash -c 'until docker-compose exec redis redis-cli ping; do sleep 2; done'
    print_status "Redis is ready"
    
    print_status "All databases are ready"
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    
    # Run migrations inside the web container
    docker-compose run --rm web flask db upgrade
    print_status "Database migrations completed"
}

# Seed database
seed_database() {
    print_info "Seeding database with test data..."
    docker-compose run --rm web python seed_database_docker.py migrate-seed
    print_status "Database seeding completed"
}

# Start all services
start_all_services() {
    print_info "Starting all services..."
    docker-compose up -d
    
    print_info "Waiting for web application to be ready..."
    timeout 120 bash -c 'until curl -f http://localhost:5002/health >/dev/null 2>&1; do sleep 3; done'
    print_status "Web application is ready"
}

# Show status
show_status() {
    echo ""
    print_status "JobMate is now running!"
    echo ""
    echo "🔗 Services:"
    echo "   Main App:      http://localhost:5002"
    echo "   Kibana:        http://localhost:5601"
    echo "   PostgreSQL:    localhost:5432"
    echo "   MongoDB:       localhost:27017"
    echo "   Redis:         localhost:6379"
    echo "   Elasticsearch: http://localhost:9200"
    echo ""
    echo "📋 Test Credentials:"
    echo "   Applicant: applicant@demo.com / password123"
    echo "   Recruiter: recruiter@demo.com / password123"
    echo ""
    echo "🐳 Docker Commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop all:      docker-compose down"
    echo "   Restart:       docker-compose restart"
    echo "   Shell access:  docker-compose exec web bash"
    echo ""
}

# Stop all services
stop_services() {
    print_info "Stopping all services..."
    docker-compose down
    print_status "All services stopped"
}

# Clean up everything
cleanup() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_info "Cleaning up Docker resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# View logs
view_logs() {
    service=${1:-web}
    print_info "Viewing logs for service: $service"
    docker-compose logs -f "$service"
}

# Execute command in container
exec_command() {
    service=${1:-web}
    shift
    command=${@:-bash}
    print_info "Executing command in $service: $command"
    docker-compose exec "$service" $command
}

# Seed only
seed_only() {
    print_info "Seeding database (services must be running)..."
    docker-compose exec web python seed_database_docker.py
    print_status "Database seeding completed"
}

# Reset database
reset_database() {
    print_warning "This will delete ALL data in the database!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_info "Resetting database..."
        docker-compose exec web python seed_database_docker.py reset
        print_status "Database reset completed"
    else
        print_info "Reset cancelled"
    fi
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup"|"build")
            check_docker
            check_docker_daemon
            setup_env
            build_images
            ;;
        "start-dbs")
            check_docker
            check_docker_daemon
            start_databases
            ;;
        "init-db")
            check_docker
            check_docker_daemon
            init_database
            ;;
        "seed")
            check_docker
            check_docker_daemon
            seed_only
            ;;
        "start")
            check_docker
            check_docker_daemon
            start_all_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_all_services
            show_status
            ;;
        "logs")
            view_logs "$2"
            ;;
        "exec")
            shift
            exec_command "$@"
            ;;
        "shell")
            exec_command web bash
            ;;
        "reset-db")
            reset_database
            ;;
        "cleanup")
            cleanup
            ;;
        "status")
            docker-compose ps
            ;;
        "full")
            check_docker
            check_docker_daemon
            setup_env
            build_images
            start_databases
            init_database
            seed_database
            start_all_services
            show_status
            ;;
        "help")
            echo "JobMate Docker Setup Script"
            echo ""
            echo "Usage: ./docker-setup.sh [command]"
            echo ""
            echo "Setup Commands:"
            echo "  setup        - Setup environment and build images"
            echo "  build        - Build Docker images"
            echo "  full         - Complete setup: build + start + init + seed"
            echo ""
            echo "Service Management:"
            echo "  start-dbs    - Start database services only"
            echo "  start        - Start all services"
            echo "  stop         - Stop all services"
            echo "  restart      - Restart all services"
            echo "  status       - Show service status"
            echo ""
            echo "Database Commands:"
            echo "  init-db      - Initialize database and run migrations"
            echo "  seed         - Seed database with test data"
            echo "  reset-db     - Reset database (WARNING: deletes all data)"
            echo ""
            echo "Utility Commands:"
            echo "  logs [service] - View logs (default: web)"
            echo "  shell        - Open shell in web container"
            echo "  exec [service] [cmd] - Execute command in container"
            echo "  cleanup      - Remove all containers and volumes"
            echo "  help         - Show this help"
            echo ""
            echo "Examples:"
            echo "  ./docker-setup.sh full        # Complete setup"
            echo "  ./docker-setup.sh start       # Start services"
            echo "  ./docker-setup.sh logs web    # View web logs"
            echo "  ./docker-setup.sh shell       # Open shell"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use './docker-setup.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Check if script is being run from the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -f "Dockerfile" ]; then
    print_error "This script must be run from the JobMateRefactor root directory"
    exit 1
fi

# Run main function with all arguments
main "$@"
