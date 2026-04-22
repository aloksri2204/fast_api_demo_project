@echo off
REM Docker management helper script for Windows

setlocal enabledelayedexpansion

if "%1%"=="start" (
    echo Starting Docker containers...
    docker-compose up -d
    echo ✓ Containers started
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
) else if "%1%"=="stop" (
    echo Stopping Docker containers...
    docker-compose down
    echo ✓ Containers stopped
) else if "%1%"=="restart" (
    echo Restarting Docker containers...
    docker-compose restart
    echo ✓ Containers restarted
) else if "%1%"=="build" (
    echo Building Docker images...
    docker-compose build
    echo ✓ Build complete
) else if "%1%"=="logs" (
    if "%2%"=="" (
        docker-compose logs -f
    ) else (
        docker-compose logs -f %2%
    )
) else if "%1%"=="bash-backend" (
    docker-compose exec backend bash
) else if "%1%"=="shell-frontend" (
    docker-compose exec frontend sh
) else if "%1%"=="psql" (
    docker-compose exec postgres psql -U user -d fastapi_db
) else if "%1%"=="clean" (
    echo Removing all containers and volumes...
    docker-compose down -v
    echo ✓ Cleanup complete
) else (
    echo Docker Management Script
    echo Usage: %0% [start^|stop^|restart^|build^|logs^|bash-backend^|shell-frontend^|psql^|clean]
    echo.
    echo Commands:
    echo   start           - Start all containers
    echo   stop            - Stop all containers
    echo   restart         - Restart all containers
    echo   build           - Build Docker images
    echo   logs [service]  - View logs (optionally for specific service)
    echo   bash-backend    - Open bash shell in backend container
    echo   shell-frontend  - Open shell in frontend container
    echo   psql            - Connect to PostgreSQL database
    echo   clean           - Remove all containers and volumes
)

endlocal
