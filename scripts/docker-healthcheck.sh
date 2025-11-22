#!/bin/bash

echo "🔍 Checking Docker deployment health..."
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Please edit .env and add your OPENAI_API_KEY"
        exit 1
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

echo "✅ .env file exists"
echo ""

echo "🚀 Checking container status..."
BACKEND_STATUS=$(docker inspect -f '{{.State.Status}}' document-processor-backend 2>/dev/null)
FRONTEND_STATUS=$(docker inspect -f '{{.State.Status}}' document-processor-frontend 2>/dev/null)

if [ "$BACKEND_STATUS" == "running" ]; then
    echo "✅ Backend container is running"
    BACKEND_HEALTH=$(docker inspect -f '{{.State.Health.Status}}' document-processor-backend 2>/dev/null)
    echo "   Health: $BACKEND_HEALTH"
else
    echo "❌ Backend container is not running (Status: $BACKEND_STATUS)"
fi

if [ "$FRONTEND_STATUS" == "running" ]; then
    echo "✅ Frontend container is running"
    FRONTEND_HEALTH=$(docker inspect -f '{{.State.Health.Status}}' document-processor-frontend 2>/dev/null)
    echo "   Health: $FRONTEND_HEALTH"
else
    echo "❌ Frontend container is not running (Status: $FRONTEND_STATUS)"
fi

echo ""
echo "🌐 Testing endpoints..."

if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend API is responding (http://localhost:8000)"
else
    echo "❌ Backend API is not responding"
fi

if curl -s http://localhost/ > /dev/null; then
    echo "✅ Frontend is responding (http://localhost)"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "📊 Container logs (last 10 lines):"
echo ""
echo "=== Backend Logs ==="
docker logs --tail 10 document-processor-backend 2>/dev/null || echo "No logs available"
echo ""
echo "=== Frontend Logs ==="
docker logs --tail 10 document-processor-frontend 2>/dev/null || echo "No logs available"

echo ""
echo "✅ Health check complete!"

