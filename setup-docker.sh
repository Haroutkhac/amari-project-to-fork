#!/bin/bash

set -e

echo "🐳 Docker Deployment Setup Script"
echo "=================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
        echo ""
        read -p "Do you want to edit .env now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "OPENAI_API_KEY=your_key_here" > .env
        echo "⚠️  .env file created. Please add your OPENAI_API_KEY"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
if grep -q "your_openai_api_key_here\|your_key_here" .env; then
    echo "⚠️  Warning: Default API key detected in .env"
    echo "Please update .env with your actual OPENAI_API_KEY"
    exit 1
fi

echo "✅ API key configured"
echo ""

read -p "Start deployment now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Building and starting containers..."
    docker-compose up --build -d
    
    echo ""
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    echo ""
    ./scripts/docker-healthcheck.sh
    
    echo ""
    echo "🎉 Deployment complete!"
    echo ""
    echo "Access the application at:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  make logs      - View logs"
    echo "  make down      - Stop services"
    echo "  make restart   - Restart services"
fi

