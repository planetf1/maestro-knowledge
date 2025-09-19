#!/bin/bash

# MCP E2E Tests Setup and Execution Script
# This script helps set up and run MCP E2E tests locally for both Milvus and Weaviate backends

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[MCP-E2E]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if docker/podman is available
check_container_runtime() {
    if command -v docker &> /dev/null; then
        CONTAINER_CMD="docker"
        log "Using Docker for container management"
    elif command -v podman &> /dev/null; then
        CONTAINER_CMD="podman"
        log "Using Podman for container management"
    else
        error "Neither Docker nor Podman is available. Please install one of them."
        exit 1
    fi
}

# Start Ollama container with model
start_ollama() {
    log "Starting Ollama container..."
    
    # Check if ollama container is already running
    if $CONTAINER_CMD ps --filter "name=ollama-mcp-e2e" --format "{{.Names}}" | grep -q "ollama-mcp-e2e"; then
        log "Ollama container already running"
    else
        $CONTAINER_CMD run -d --name ollama-mcp-e2e -p 11434:11434 ollama/ollama:latest
        
        # Wait for Ollama to be ready
        log "Waiting for Ollama to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                success "Ollama is ready"
                break
            fi
            echo -n "."
            sleep 2
        done
        echo
    fi
    
    # Pull the embedding model
    log "Pulling nomic-embed-text model..."
    curl -X POST http://localhost:11434/api/pull -d '{"name":"nomic-embed-text:latest"}' 2>/dev/null || true
    
    # Wait for model to be available
    log "Waiting for model to be available..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags | grep -q "nomic-embed-text"; then
            success "nomic-embed-text model is available"
            break
        fi
        echo -n "."
        sleep 5
    done
    echo
}

# Start Milvus stack
start_milvus() {
    log "Starting Milvus stack..."
    
    # Start etcd
    if ! $CONTAINER_CMD ps --filter "name=etcd-mcp-e2e" --format "{{.Names}}" | grep -q "etcd-mcp-e2e"; then
        $CONTAINER_CMD run -d --name etcd-mcp-e2e \
            -p 2379:2379 -p 2380:2380 \
            -e ETCD_AUTO_COMPACTION_MODE=revision \
            -e ETCD_AUTO_COMPACTION_RETENTION=1000 \
            -e ETCD_QUOTA_BACKEND_BYTES=4294967296 \
            -e ETCD_SNAPSHOT_COUNT=50000 \
            quay.io/coreos/etcd:v3.5.5
    fi
    
    # Start MinIO
    if ! $CONTAINER_CMD ps --filter "name=minio-mcp-e2e" --format "{{.Names}}" | grep -q "minio-mcp-e2e"; then
        $CONTAINER_CMD run -d --name minio-mcp-e2e \
            -p 9000:9000 -p 9001:9001 \
            -e MINIO_ACCESS_KEY=minioadmin \
            -e MINIO_SECRET_KEY=minioadmin \
            minio/minio:RELEASE.2023-03-20T20-16-18Z server /data --console-address ":9001"
    fi
    
    # Start Milvus
    if ! $CONTAINER_CMD ps --filter "name=milvus-mcp-e2e" --format "{{.Names}}" | grep -q "milvus-mcp-e2e"; then
        # Use host networking or proper container networking
        if [ "$CONTAINER_CMD" = "docker" ]; then
            # Docker: use host.docker.internal
            ETCD_HOST="host.docker.internal"
            MINIO_HOST="host.docker.internal"
        else
            # Podman: use host.containers.internal
            ETCD_HOST="host.containers.internal"
            MINIO_HOST="host.containers.internal"
        fi
        
        $CONTAINER_CMD run -d --name milvus-mcp-e2e \
            -p 19530:19530 \
            -e ETCD_ENDPOINTS="${ETCD_HOST}:2379" \
            -e MINIO_ADDRESS="${MINIO_HOST}:9000" \
            milvusdb/milvus:v2.3.3
    fi
    
    # Wait for services
    log "Waiting for Milvus services to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:19530 >/dev/null 2>&1; then
            success "Milvus is ready"
            break
        fi
        echo -n "."
        sleep 5
    done
    echo
}

# Start Weaviate
start_weaviate() {
    log "Starting Weaviate..."
    
    if ! $CONTAINER_CMD ps --filter "name=weaviate-mcp-e2e" --format "{{.Names}}" | grep -q "weaviate-mcp-e2e"; then
        $CONTAINER_CMD run -d --name weaviate-mcp-e2e \
            -p 8080:8080 \
            -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
            -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
            -e DEFAULT_VECTORIZER_MODULE=none \
            -e ENABLE_MODULES= \
            -e CLUSTER_HOSTNAME=node1 \
            semitechnologies/weaviate:1.27.0
    fi
    
    # Wait for Weaviate
    log "Waiting for Weaviate to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/v1/meta >/dev/null 2>&1; then
            success "Weaviate is ready"
            break
        fi
        echo -n "."
        sleep 3
    done
    echo
}

# Stop all containers
cleanup() {
    log "Cleaning up containers..."
    
    containers=(
        "ollama-mcp-e2e"
        "milvus-mcp-e2e" 
        "etcd-mcp-e2e"
        "minio-mcp-e2e"
        "weaviate-mcp-e2e"
    )
    
    for container in "${containers[@]}"; do
        if $CONTAINER_CMD ps -a --filter "name=${container}" --format "{{.Names}}" | grep -q "${container}"; then
            log "Removing container: ${container}"
            $CONTAINER_CMD rm -f "${container}" 2>/dev/null || true
        fi
    done
}

# Run Milvus E2E tests
run_milvus_tests() {
    log "Running Milvus MCP E2E tests..."
    
    cd "${PROJECT_ROOT}"
    
    export MILVUS_URI="http://localhost:19530"
    export CUSTOM_EMBEDDING_URL="http://localhost:11434/api/embeddings"
    export CUSTOM_EMBEDDING_MODEL="nomic-embed-text"
    export CUSTOM_EMBEDDING_VECTORSIZE="768"
    export E2E_BACKEND="milvus"
    export E2E_MILVUS="1"
    export E2E_MCP_PORT="8030"
    export PYTHONPATH="src"
    
    if timeout 600 uv run pytest tests/e2e/test_mcp_milvus_e2e.py -v --tb=short; then
        success "Milvus MCP E2E tests passed!"
    else
        error "Milvus MCP E2E tests failed!"
        return 1
    fi
}

# Run Weaviate E2E tests  
run_weaviate_tests() {
    log "Running Weaviate MCP E2E tests..."
    
    cd "${PROJECT_ROOT}"
    
    export WEAVIATE_URL="http://localhost:8080"
    export WEAVIATE_API_KEY="test-key"
    export E2E_BACKEND="weaviate"
    export E2E_WEAVIATE="1"
    export E2E_MCP_PORT="8031"
    export PYTHONPATH="src"
    
    if timeout 600 uv run pytest tests/e2e/test_mcp_weaviate_e2e.py -v --tb=short; then
        success "Weaviate MCP E2E tests passed!"
    else
        error "Weaviate MCP E2E tests failed!"
        return 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup-ollama    Start Ollama container and pull embedding model"
    echo "  setup-milvus    Start Milvus stack (etcd, MinIO, Milvus)"
    echo "  setup-weaviate  Start Weaviate container"
    echo "  setup-all       Start all required services"
    echo "  test-milvus     Run Milvus MCP E2E tests"
    echo "  test-weaviate   Run Weaviate MCP E2E tests"
    echo "  test-all        Run all MCP E2E tests"
    echo "  full-milvus     Setup Milvus services and run tests"
    echo "  full-weaviate   Setup Weaviate services and run tests"
    echo "  full-all        Setup all services and run all tests"
    echo "  cleanup         Stop and remove all containers"
    echo "  status          Show status of all containers"
    echo ""
    echo "Examples:"
    echo "  $0 full-all         # Complete MCP E2E test run for both backends"
    echo "  $0 full-milvus      # Setup and test only Milvus"
    echo "  $0 test-weaviate    # Run Weaviate tests (assumes services running)"
}

# Show container status
show_status() {
    log "Container status:"
    echo ""
    
    containers=(
        "ollama-mcp-e2e:Ollama (Embeddings)"
        "milvus-mcp-e2e:Milvus (Vector DB)"
        "etcd-mcp-e2e:etcd (Milvus dependency)"
        "minio-mcp-e2e:MinIO (Milvus storage)"
        "weaviate-mcp-e2e:Weaviate (Vector DB)"
    )
    
    for container_info in "${containers[@]}"; do
        IFS=':' read -r container desc <<< "$container_info"
        if $CONTAINER_CMD ps --filter "name=${container}" --format "{{.Names}}" | grep -q "${container}"; then
            echo -e "  ${GREEN}●${NC} ${desc} (${container})"
        else
            echo -e "  ${RED}○${NC} ${desc} (${container})"
        fi
    done
    echo ""
    
    # Show service endpoints
    log "Service endpoints:"
    echo "  Ollama:    http://localhost:11434"
    echo "  Milvus:    http://localhost:19530" 
    echo "  Weaviate:  http://localhost:8080"
    echo "  etcd:      http://localhost:2379"
    echo "  MinIO:     http://localhost:9000 (console: http://localhost:9001)"
}

# Main script logic
main() {
    check_container_runtime
    
    case "${1:-}" in
        setup-ollama)
            start_ollama
            ;;
        setup-milvus)
            start_ollama
            start_milvus
            ;;
        setup-weaviate)
            start_ollama
            start_weaviate
            ;;
        setup-all)
            start_ollama
            start_milvus
            start_weaviate
            ;;
        test-milvus)
            run_milvus_tests
            ;;
        test-weaviate)
            run_weaviate_tests
            ;;
        test-all)
            run_milvus_tests
            run_weaviate_tests
            ;;
        full-milvus)
            start_ollama
            start_milvus
            run_milvus_tests
            ;;
        full-weaviate)
            start_ollama
            start_weaviate
            run_weaviate_tests
            ;;
        full-all)
            start_ollama
            start_milvus
            start_weaviate
            run_milvus_tests
            run_weaviate_tests
            ;;
        cleanup)
            cleanup
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            usage
            ;;
        "")
            usage
            ;;
        *)
            error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"