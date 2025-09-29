# MCP E2E Testing

This directory contains end-to-end tests for the Maestro Knowledge MCP (Model Context Protocol) server with both Milvus and Weaviate vector database backends.

## Overview

The MCP E2E tests validate the complete integration between:
- MCP server endpoints and tools
- Vector database backends (Milvus/Weaviate)
- Embedding models (via Ollama)
- Document operations (CRUD)
- Query and search functionality

## Test Structure

### Test Files
- `test_mcp_milvus_e2e.py` - Milvus backend tests (9 tests)
- `test_mcp_weaviate_e2e.py` - Weaviate backend tests (8 tests)
- `test_mcp_weaviate_simple.py` - Simplified Weaviate tests (3 tests)
- `test_functions.py` - Shared test logic for backend-agnostic testing
- `test_functions_simple.py` - Simplified shared test functions
- `common.py` - Common fixtures and utilities
- `conftest.py` - Pytest configuration and fixture registration

### Test Categories

**Database Management**
- Create vector databases
- List databases and collections  
- Get database/collection information
- Cleanup operations

**Document Operations**
- Write documents with embeddings
- List and count documents
- Retrieve specific documents
- Delete individual and bulk documents
- Collection-specific document operations

**Query Operations**
- Semantic search across documents
- Intelligent query with reasoning
- Configuration discovery (embeddings, chunking strategies)

**Integration Tests**
- Full workflow testing
- Resync operations
- Error handling and recovery

## Running Tests

### Prerequisites

1. **Container Runtime**: Docker or Podman
2. **Python Environment**: Python 3.11+ with uv
3. **Network Ports**: 8080 (Weaviate), 19530 (Milvus), 11434 (Ollama), 2379 (etcd), 9000 (MinIO)

### ⚠️ Important: Pytest Configuration

**E2E tests require the `-m "e2e"` flag** because the default pytest configuration excludes them:

```bash
# ❌ This will select 0 tests (deselected by default config):
uv run pytest tests/e2e/test_mcp_weaviate_e2e.py -v

# ✅ This works (includes E2E marker):
uv run pytest tests/e2e/test_mcp_weaviate_e2e.py -v -m "e2e"
```

The `pyproject.toml` has `addopts = "-m 'unit or integration'"` which excludes E2E tests by default to keep regular test runs fast. Always include `-m "e2e"` when running E2E tests manually.

### Local Testing

#### Using the MCP E2E Script (Recommended)

```bash
# Complete test run for both backends
./tools/mcp-e2e.sh full-all

# Test only Milvus
./tools/mcp-e2e.sh full-milvus

# Test only Weaviate  
./tools/mcp-e2e.sh full-weaviate

# Setup services without running tests
./tools/mcp-e2e.sh setup-all

# Run tests (assumes services already running)
./tools/mcp-e2e.sh test-all

# Check service status
./tools/mcp-e2e.sh status

# Cleanup all containers
./tools/mcp-e2e.sh cleanup
```

#### Manual Testing

1. **Start Ollama and pull embedding model:**
```bash
podman run -d --name ollama-mcp-e2e -p 11434:11434 ollama/ollama:latest
curl -X POST http://localhost:11434/api/pull -d '{"name":"nomic-embed-text:latest"}'
```

2. **Start Milvus standalone with embedded etcd:**

```bash
# Milvus with embedded etcd (no separate etcd/MinIO needed) - ARM64 compatible
podman run -d --name milvus-mcp-e2e -p 19530:19530 -p 9091:9091 \
  -e ETCD_USE_EMBED=true \
  -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
  -e COMMON_STORAGETYPE=local \
  -e DEPLOY_MODE=STANDALONE \
  milvusdb/milvus:v2.6.1 /milvus/bin/milvus run standalone
```

3. **Start Weaviate:**
```bash
podman run -d --name weaviate-mcp-e2e -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES= \
  -e CLUSTER_HOSTNAME=node1 \
  semitechnologies/weaviate:1.27.0
```

4. **Run tests:**
```bash
# Milvus tests
MILVUS_URI=http://localhost:19530 \
CUSTOM_EMBEDDING_URL=http://localhost:11434/api/embeddings \
CUSTOM_EMBEDDING_MODEL=nomic-embed-text \
CUSTOM_EMBEDDING_VECTORSIZE=768 \
E2E_BACKEND=milvus E2E_MILVUS=1 \
uv run pytest tests/e2e/test_mcp_milvus_e2e.py -v -m "e2e"

# Weaviate tests  
WEAVIATE_URL=http://localhost:8080 \
WEAVIATE_API_KEY=test-key \
E2E_BACKEND=weaviate E2E_WEAVIATE=1 \
uv run pytest tests/e2e/test_mcp_weaviate_e2e.py -v -m "e2e"
```

### CI/CD Testing

The E2E tests run automatically in GitHub Actions via the `.github/workflows/e2e.yml` workflow:

- **Triggers**: Push to main/develop, PRs, manual dispatch
- **Matrix**: Separate jobs for Milvus and Weaviate backends
- **Services**: Ollama, vector DB containers, dependencies
- **Timeout**: 30 minutes per job, 10 minutes per test
- **Artifacts**: Test results and logs on failure

## Environment Variables

### Backend Selection
```bash
E2E_BACKEND=milvus|weaviate    # Backend selector (preferred)
E2E_MILVUS=1                   # Enable Milvus tests (legacy)
E2E_WEAVIATE=1                 # Enable Weaviate tests (legacy)
```

### Milvus Configuration
```bash
MILVUS_URI=http://localhost:19530                      # Milvus endpoint
CUSTOM_EMBEDDING_URL=http://localhost:11434/api/embeddings  # Ollama embeddings
CUSTOM_EMBEDDING_MODEL=nomic-embed-text               # Model name
CUSTOM_EMBEDDING_VECTORSIZE=768                       # Vector dimensions
```

### Weaviate Configuration  
```bash
WEAVIATE_URL=http://localhost:8080    # Weaviate endpoint
WEAVIATE_API_KEY=test-key             # API key (test-key for local)
```

### Test Configuration
```bash
E2E_MCP_PORT=8030              # MCP server port (8030 for Milvus, 8031 for Weaviate)
PYTHONPATH=src                 # Python path for imports
LOG_LEVEL=info                 # Logging level
VDB_LOG_LEVEL=debug           # Vector DB logging level
```

## Architecture

### Test Fixtures

**Function-scoped MCP Server** (`mcp_http_server`)
- Each test gets a fresh MCP server instance
- Prevents state accumulation between tests
- Includes health checks and proper teardown
- Located in `common.py`

**Backend Configuration** (`get_backend_config`)
- Provides backend-specific parameters
- Handles environment variable validation
- Service availability checking

### Shared Test Logic

The `test_functions.py` module contains backend-agnostic test implementations:
- `run_database_management_tests()`
- `run_document_operations_tests()`
- `run_query_operations_tests()`
- `run_configuration_discovery_tests()`
- `run_bulk_operations_tests()`
- `run_collection_specific_tests()`
- `run_resync_operations_tests()`
- `run_full_flow_test()`

Test entrypoints (`test_mcp_*_e2e.py`) simply call these shared functions with the appropriate backend name.

### Error Handling

Tests implement robust error handling:
- **Graceful skipping** when services unavailable
- **Timeout protection** for hanging operations  
- **Cleanup in finally blocks** for resource management
- **Clear error messages** with context

## Troubleshooting

### Common Issues

**Tests hang or timeout:**
- Check container logs: `docker logs <container-name>`  
- Verify service endpoints are responding
- Increase timeout values if needed

**Collection/database not found:**
- Ensure embedding model is loaded in Ollama
- Check vector dimensions match (768 for nomic-embed-text)
- Verify backend service health

**Port conflicts:**
- Use different ports via environment variables
- Stop conflicting services
- Check with `netstat -ln | grep <port>`

**Container startup failures:**
- Check available resources (memory, disk)
- Verify container runtime (Docker/Podman)
- Review container logs for specific errors

### Debugging

Enable verbose logging:
```bash
LOG_LEVEL=debug VDB_LOG_LEVEL=debug uv run pytest tests/e2e/ -v -s --tb=long -m "e2e"
```

Check service health:
```bash
# Ollama
curl http://localhost:11434/api/tags

# Milvus  
curl http://localhost:19530

# Weaviate
curl http://localhost:8080/v1/meta

# Test embedding
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","prompt":"test"}'
```

Show container status:
```bash
./tools/mcp-e2e.sh status
```