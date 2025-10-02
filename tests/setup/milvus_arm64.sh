#!/bin/bash
# Start ARM64-compatible Milvus for E2E testing

echo "🚀 Starting ARM64-compatible Milvus container..."

# Stop and remove existing container if running
podman stop milvus-simple 2>/dev/null || true
podman rm milvus-simple 2>/dev/null || true

# Create data directory
mkdir -p "$(pwd)/volumes/milvus/etcd"
mkdir -p "$(pwd)/volumes/milvus/data"

echo "📦 Starting Milvus standalone container..."

# Start the ARM64-compatible Milvus container (public image)
podman run -d \
  --name milvus-simple \
  -p 19530:19530 \
  -p 9091:9091 \
  -v "$(pwd)/volumes/milvus":/var/lib/milvus \
  -e ETCD_USE_EMBED=true \
  -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
  -e COMMON_STORAGETYPE=local \
  -e DEPLOY_MODE=STANDALONE \
  milvusdb/milvus:v2.6.2-20250918-d1b40b77-arm64 \
  /milvus/bin/milvus run standalone

echo "⏳ Waiting for Milvus to start..."
sleep 15

# Check if Milvus is responding on the HTTP port (9091)
echo ""
echo "🔍 Service Status:"
for i in {1..30}; do
    if curl -s http://localhost:9091/healthz >/dev/null 2>&1; then
        echo "✅ Milvus HTTP endpoint (port 9091) is responding"
        break
    fi
    echo "   ... waiting for HTTP health check (${i}/30)"
    sleep 2
done

# Test gRPC connection using Python
echo "Testing gRPC connection (port 19530)..."
python3 -c "
try:
    from pymilvus import connections, utility
    connections.connect('test', host='localhost', port='19530', timeout=10)
    collections = utility.list_collections(using='test')
    connections.disconnect('test')
    print('✅ Milvus gRPC endpoint (port 19530) is responding')
    print(f'   Found {len(collections)} existing collections')
except Exception as e:
    print(f'⚠ Milvus gRPC connection failed: {e}')
" 2>/dev/null || echo "⚠ Python pymilvus not available for gRPC test"

echo ""
echo "📋 Container status:"
podman ps --filter name=milvus-simple

echo ""
echo "🧪 Run E2E tests from project root with:"
echo "E2E_BACKEND=milvus \\"
echo "MILVUS_URI=http://localhost:19530 \\"
echo "CUSTOM_EMBEDDING_URL=http://localhost:11434/v1 \\"
echo "CUSTOM_EMBEDDING_MODEL=nomic-embed-text \\"
echo "CUSTOM_EMBEDDING_VECTORSIZE=768 \\"
echo "uv run python -m pytest tests/e2e/test_mcp_milvus_e2e.py::test_full_milvus_flow -xvs"