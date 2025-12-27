#!/bin/bash

echo "================================================"
echo "  PDF RAG Chatbot System - Quick Start"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it to add your API keys:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - UPSTAGE_API_KEY (optional, for Upstage parser)"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

# Check MinIO
if curl -s http://localhost:9000/minio/health/live > /dev/null; then
    echo "✅ MinIO is ready"
else
    echo "⚠️  MinIO is not ready yet"
fi

# Check Redis
if docker exec pdf-rag-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis is not ready yet"
fi

# Check Elasticsearch
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "✅ Elasticsearch is ready"
else
    echo "⚠️  Elasticsearch is not ready yet (may take 1-2 minutes)"
fi

# Check Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "⚠️  Backend API is not ready yet"
fi

# Check Frontend
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "⚠️  Frontend is not ready yet"
fi

echo ""
echo "================================================"
echo "  🎉 System Started!"
echo "================================================"
echo ""
echo "Access the services:"
echo "  📱 Streamlit UI:    http://localhost:8501"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo "  🗄️  MinIO Console:   http://localhost:9001"
echo "     (minioadmin / minioadmin)"
echo ""
echo "Useful commands:"
echo "  View logs:          docker-compose logs -f"
echo "  Stop system:        docker-compose down"
echo "  Restart service:    docker-compose restart <service>"
echo ""
echo "For detailed documentation, see README.md"
echo "================================================"
