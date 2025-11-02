@echo off
REM Build Docker Images for Kubernetes Deployment (Windows)
REM This script builds the backend and frontend Docker images locally

echo ==========================================
echo Building Docker Images for Barista App
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running!
    echo Please start Docker Desktop and try again.
    exit /b 1
)

echo Docker is running
echo.

REM Build Backend Image
echo Building Backend Image...
echo -------------------------------------------
docker build -t barista-backend:latest ./backend
if errorlevel 1 (
    echo Failed to build backend image
    exit /b 1
)
echo Backend image built successfully!
echo.

REM Build Frontend Image
echo Building Frontend Image...
echo -------------------------------------------
docker build -t barista-frontend:latest ./frontend
if errorlevel 1 (
    echo Failed to build frontend image
    exit /b 1
)
echo Frontend image built successfully!
echo.

REM Display built images
echo ==========================================
echo All Images Built Successfully!
echo ==========================================
echo.
echo Built images:
docker images | findstr "barista"
echo.
echo Next steps:
echo 1. Update k8s/backend-secret.yaml with your credentials
echo 2. Deploy to Kubernetes: kubectl apply -f k8s/
echo 3. Check status: kubectl get pods -n barista-app
echo.
