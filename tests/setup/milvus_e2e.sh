#!/bin/bash
# Setup script for Milvus E2E testing

echo "🚀 Setting up Milvus for E2E testing..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Starting Milvus container..."

# Stop existing container if running
docker stop milvus-standalone 2>/dev/null || true
docker rm milvus-standalone 2>/dev/null || true

# Start Milvus standalone
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  -v $(pwd)/volumes/milvus:/var/lib/milvus \
  milvusdb/milvus:latest

echo "⏳ Waiting for Milvus to start..."
sleep 10

# Check if Milvus is responding
for i in {1..30}; do
    if curl -s http://localhost:19530/health >/dev/null 2>&1; then
        echo "✅ Milvus is ready!"
        break
    fi
    echo "   ... waiting (${i}/30)"
    sleep 2
done

# Verify both services
echo ""
echo "🔍 Service Status:"
echo "Milvus (port 19530):"
if curl -s http://localhost:19530/health >/dev/null 2>&1; then
    echo "  ✅ Running"
else
    echo "  ❌ Not responding"
fi

echo "Embedding service (port 11434):"
if curl -s http://localhost:11434 >/dev/null 2>&1; then
    echo "  ✅ Running"
else
    echo "  ❌ Not running (start with: ollama serve)"
fi

echo ""
echo "🧪 Run E2E tests with:"
echo "E2E_BACKEND=milvus \\"
echo "MILVUS_URI=http://localhost:19530 \\"
echo "CUSTOM_EMBEDDING_URL=http://localhost:11434/v1 \\"
echo "CUSTOM_EMBEDDING_MODEL=nomic-embed-text \\"
echo "CUSTOM_EMBEDDING_VECTORSIZE=768 \\"
echo "uv run python -m pytest tests/e2e/test_mcp_milvus_e2e.py::test_full_milvus_flow -xvs"