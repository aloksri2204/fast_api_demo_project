#!/bin/bash
# Docker management helper script for development

case "$1" in
  start)
    echo "Starting Docker containers..."
    docker-compose up -d
    echo "✓ Containers started"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    ;;
  stop)
    echo "Stopping Docker containers..."
    docker-compose down
    echo "✓ Containers stopped"
    ;;
  restart)
    echo "Restarting Docker containers..."
    docker-compose restart
    echo "✓ Containers restarted"
    ;;
  build)
    echo "Building Docker images..."
    docker-compose build
    echo "✓ Build complete"
    ;;
  logs)
    docker-compose logs -f "${2:-}"
    ;;
  bash-backend)
    docker-compose exec backend bash
    ;;
  shell-frontend)
    docker-compose exec frontend sh
    ;;
  psql)
    docker-compose exec postgres psql -U user -d fastapi_db
    ;;
  clean)
    echo "Removing all containers and volumes..."
    docker-compose down -v
    echo "✓ Cleanup complete"
    ;;
  *)
    echo "Docker Management Script"
    echo "Usage: $0 {start|stop|restart|build|logs|bash-backend|shell-frontend|psql|clean}"
    echo ""
    echo "Commands:"
    echo "  start           - Start all containers"
    echo "  stop            - Stop all containers"
    echo "  restart         - Restart all containers"
    echo "  build           - Build Docker images"
    echo "  logs [service]  - View logs (optionally for specific service)"
    echo "  bash-backend    - Open bash shell in backend container"
    echo "  shell-frontend  - Open shell in frontend container"
    echo "  psql            - Connect to PostgreSQL database"
    echo "  clean           - Remove all containers and volumes"
    ;;
esac
