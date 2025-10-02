#!/bin/bash
# Setup script for Weaviate E2E testing

echo "🚀 Setting up Weaviate for E2E testing..."

# Check if Docker/Podman is available
CONTAINER_CMD="docker"
if command -v podman >/dev/null 2>&1; then
    CONTAINER_CMD="podman"
    echo "📦 Using Podman for container management"
elif command -v docker >/dev/null 2>&1; then
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "📦 Using Docker for container management"
else
    echo "❌ Neither Docker nor Podman found. Please install one of them."
    exit 1
fi

echo "📦 Starting Weaviate container..."

# Stop existing container if running
$CONTAINER_CMD stop weaviate-test 2>/dev/null || true
$CONTAINER_CMD rm weaviate-test 2>/dev/null || true

# Start Weaviate with anonymous authentication enabled
$CONTAINER_CMD run -d \
  --name weaviate-test \
  -p 8080:8080 \
  -p 50051:50051 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES= \
  -e CLUSTER_HOSTNAME=node1 \
  semitechnologies/weaviate:1.27.0

echo "⏳ Waiting for Weaviate to start..."
sleep 15

# Check if Weaviate is responding
echo "🔍 Testing Weaviate connectivity..."
for i in {1..30}; do
    if curl -s http://localhost:8080/v1/meta >/dev/null 2>&1; then
        echo "✅ Weaviate container is responsive!"
        break
    fi
    echo "   ... waiting for container (${i}/30)"
    sleep 2
done

# Additional check - test the port
sleep 5
echo "🔍 Testing port connectivity..."
for i in {1..15}; do
    if nc -z localhost 8080 2>/dev/null; then
        echo "✅ Weaviate port 8080 is accessible!"
        break
    fi
    echo "   ... waiting for port (${i}/15)"
    sleep 2
done

# Verify services
echo ""
echo "🔍 Final Service Status:"
echo "Weaviate container:"
if $CONTAINER_CMD ps | grep weaviate-test | grep -q Up; then
    echo "  ✅ Container running"
    echo "     Image: semitechnologies/weaviate:1.27.0"
    echo "     Ports: 8080:8080 (HTTP), 50051:50051 (gRPC)"
else
    echo "  ❌ Container not running"
fi

echo "Weaviate HTTP port (8080):"
if nc -z localhost 8080 2>/dev/null; then
    echo "  ✅ Accessible"
else
    echo "  ❌ Not accessible"
fi

echo "Weaviate API Health:"
if curl -s http://localhost:8080/v1/meta >/dev/null 2>&1; then
    echo "  ✅ API responding"
    echo "  📊 $(curl -s http://localhost:8080/v1/meta | jq -r '.version // "Version info unavailable"' 2>/dev/null || echo 'Weaviate API active')"
else
    echo "  ❌ API not responding"
fi

echo ""
echo "🧪 Run E2E tests with:"
echo "WEAVIATE_URL=http://localhost:8080 \\"
echo "WEAVIATE_API_KEY=test-key \\"
echo "E2E_BACKEND=weaviate \\"
echo "E2E_WEAVIATE=1 \\"
echo "uv run pytest tests/e2e/test_mcp_weaviate_e2e.py -v -m \"e2e\""

echo ""
echo "📋 Container Management Commands:"
echo "  Stop:    $CONTAINER_CMD stop weaviate-test"
echo "  Start:   $CONTAINER_CMD start weaviate-test"
echo "  Remove:  $CONTAINER_CMD rm weaviate-test"
echo "  Logs:    $CONTAINER_CMD logs weaviate-test"
echo ""
echo "✅ Setup complete! Weaviate is ready for E2E testing."