# Running E2E Tests with Milvus

This document explains how to run end-to-end tests against a real Milvus vector database.

## Prerequisites

1. **Podman/Docker** - Container runtime
2. **Ollama** - For embedding service (should be running on port 11434)

## Setup ARM64 Milvus (Apple Silicon)

For Apple Silicon Macs, use the provided setup script:

```bash
./tests/setup/milvus_arm64.sh
```

This script:
- Stops any existing Milvus containers
- Starts ARM64-compatible Milvus container: `milvusdb/milvus:v2.6.2-20250918-d1b40b77-arm64`
- Exposes ports 19530 (gRPC) and 9091 (HTTP)
- Sets up persistent storage in `./volumes/milvus`
- Verifies the container is healthy

## Running E2E Tests

Once Milvus is running, execute the E2E test:

```bash
E2E_BACKEND=milvus \
MILVUS_URI=http://localhost:19530 \
CUSTOM_EMBEDDING_URL=http://localhost:11434/v1 \
CUSTOM_EMBEDDING_MODEL=nomic-embed-text \
CUSTOM_EMBEDDING_VECTORSIZE=768 \
uv run python -m pytest tests/e2e/test_mcp_milvus_e2e.py::test_full_milvus_flow -xvs
```

## What the E2E Test Does

The test performs a complete workflow:

1. **Server Setup** - Starts MCP HTTP server on port 8030
2. **Service Validation** - Verifies Milvus and embedding services are available
3. **Database Creation** - Creates a Milvus vector database instance
4. **Collection Setup** - Creates collection with custom embedding configuration
5. **Document Ingestion** - Writes test documents with chunking and embedding
6. **Search Testing** - Performs vector similarity search
7. **Cleanup** - Removes test data and resources

## Troubleshooting

### Container Issues
```bash
# Check container status
podman ps -a | grep milvus

# View container logs
podman logs milvus-simple

# Restart container
podman restart milvus-simple
```

### Service Connectivity
```bash
# Test HTTP endpoint
curl http://localhost:9091/healthz

# Test embedding service
curl http://localhost:11434
```

## Docker Alternative

For Intel systems or standard Docker, use:

```bash
docker run -d \
  --name milvus-simple \
  -p 19530:19530 \
  -p 9091:9091 \
  -v $(pwd)/volumes/milvus:/var/lib/milvus \
  -e ETCD_USE_EMBED=true \
  -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
  -e COMMON_STORAGETYPE=local \
  -e DEPLOY_MODE=STANDALONE \
  milvusdb/milvus:v2.6.2 \
  /milvus/bin/milvus run standalone
```

## Expected Results

A successful E2E test will show:
- ✓ MCP server responding
- ✓ Milvus service available
- ✓ Vector database created
- ✓ Collection created with custom embedding
- ✓ Test documents written
- ✓ Document count verified
- ✓ Search operations completed
- ✓ Cleanup successful
- 🎉 Full Milvus E2E test completed successfully!