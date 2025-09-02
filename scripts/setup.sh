#!/bin/bash

# H4WK5INT Setup Script
set -e

echo "🚀 Setting up H4WK5INT OSINT Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating environment file..."
    cp .env.example .env
    echo "✅ Environment file created. Please edit .env with your settings."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/reports/generated
mkdir -p docker/ssl
mkdir -p shared/data

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo "✅ H4WK5INT setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/api/docs"
echo ""
echo "🔐 Default credentials will be created on first run."
echo "📚 Check the documentation in the docs/ folder for more information."
echo ""
echo "🛑 To stop the application: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📄 To view logs: docker-compose logs -f"