#!/bin/bash

# Build Docker Images for Kubernetes Deployment
# This script builds the backend and frontend Docker images locally

set -e  # Exit on error

echo "=========================================="
echo "Building Docker Images for Barista App"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Build Backend Image
echo "📦 Building Backend Image..."
echo "-------------------------------------------"
docker build -t barista-backend:latest ./backend
if [ $? -eq 0 ]; then
    echo "✅ Backend image built successfully!"
else
    echo "❌ Failed to build backend image"
    exit 1
fi
echo ""

# Build Frontend Image
echo "📦 Building Frontend Image..."
echo "-------------------------------------------"
docker build -t barista-frontend:latest ./frontend
if [ $? -eq 0 ]; then
    echo "✅ Frontend image built successfully!"
else
    echo "❌ Failed to build frontend image"
    exit 1
fi
echo ""

# Display built images
echo "=========================================="
echo "✅ All Images Built Successfully!"
echo "=========================================="
echo ""
echo "Built images:"
docker images | grep -E "REPOSITORY|barista"
echo ""
echo "Next steps:"
echo "1. Update k8s/backend-secret.yaml with your credentials"
echo "2. Deploy to Kubernetes: kubectl apply -f k8s/"
echo "3. Check status: kubectl get pods -n barista-app"
echo ""
