# Test Strategy for Maestro Knowledge

## Test Types and Classification

### Unit Tests (`@pytest.mark.unit`)

**Purpose:** Test individual components in complete isolation

**Assumptions:**
- No external dependencies (databases, APIs, file systems)
- All external calls are mocked
- Tests focus on single functions, classes, or models
- Fast execution (<1 second per test)

**What to test:**
- Pydantic model validation and serialization
- Individual function logic and edge cases
- Class method behavior in isolation
- Input validation and error handling

**Command:**
```bash
uv run pytest -m "unit" -v
```

**Example test structure:**
```python
@pytest.mark.unit
def test_query_input_validation():
    query_input = QueryInput(db_name="test-db", query="test", limit=5)
    assert query_input.db_name == "test-db"
```

### Integration Tests (`@pytest.mark.integration`)

**Purpose:** Test components working together with mocked external services

**Assumptions:**
- Internal components are real (MCP server, vector DB classes, business logic)
- External services are mocked (database connections, HTTP APIs)
- No actual network calls or database connections
- Medium execution time (1-10 seconds per test)

**What to test:**
- MCP server creation and configuration
- Tool registration and basic functionality
- Component interaction workflows
- Error handling across component boundaries

**Command:**
```bash
uv run pytest -m "integration" -v
```

**Example test structure:**
```python
@pytest.mark.integration
async def test_mcp_server_with_mocked_database():
    with mock_database_connections():
        server = await create_mcp_server()
        # Test server functionality with mocked DB responses
```

### Service Integration Tests (`@pytest.mark.service`)

**Purpose:** Test complete workflows with real external services

**Assumptions:**
- Real databases must be running and accessible
- Database connections will succeed
- Test data can be created and cleaned up
- Slow execution time (10-60 seconds per test)
- May require specific database configurations

**What to test:**
- End-to-end workflows with real databases
- Data persistence and retrieval
- Database-specific behavior and edge cases
- Performance characteristics with real data

**Prerequisites:**
- Milvus database running (if testing Milvus functionality)
- Weaviate database running (if testing Weaviate functionality)
- Appropriate environment variables set
- Network connectivity to database services

**Command:**
```bash
# Requires databases to be running
uv run pytest -m "service" -v
```

**Example test structure:**
```python
@pytest.mark.service
@pytest.mark.requires_milvus
async def test_real_milvus_operations():
    # Assumes Milvus is running and accessible
    server = await create_mcp_server()
    # Perform real database operations
```

### End-to-End Tests (`@pytest.mark.e2e`)

**Purpose:** Test complete user workflows in full environment

**Assumptions:**
- Full application environment is running
- All external dependencies are available
- Real CLI tools and binaries exist
- Very slow execution time (minutes per test)
- Complex setup and teardown requirements

**What to test:**
- Complete user journeys
- CLI tool integration
- Cross-system interactions
- Real-world scenarios and data flows

**Prerequisites:**
- All databases running
- CLI tools built and available
- Network services accessible
- Test data sets available

**Command:**
```bash
# Requires full environment setup
uv run pytest -m "e2e" -v
```

## Common Test Execution Patterns

### Development Workflow (Fast Feedback)
```bash
# Run only fast tests with no external dependencies
uv run pytest -m "unit or integration" -v
```

### Pre-commit Validation
```bash
# Include service tests if databases are available
uv run pytest -m "unit or integration or service" -v
```

### Full Test Suite
```bash
# Run all tests including end-to-end
uv run pytest -v
```

### Database-Specific Testing
```bash
# Test only Milvus-related functionality
uv run pytest -m "requires_milvus" -v

# Test only Weaviate-related functionality
uv run pytest -m "requires_weaviate" -v
```

### Performance-Conscious Testing
```bash
# Exclude slow tests
uv run pytest -m "not slow" -v

# Run only fast unit tests
uv run pytest -m "unit" -v
```

## Environment Setup for Service Tests

### Quick Reference: Database Configuration Matrix

| **Configuration** | **Milvus** | **Weaviate** | **Setup Time** | **Test Time** | **Containers** | **Use Case** |
|-------------------|------------|--------------|----------------|---------------|----------------|--------------|
| **Development** | Local File | None | 0 min | ~20s | 0 | Quick dev testing |
| **Mixed** | Local File | Container | 1 min | ~19s | 1 | Partial integration |
| **Full Remote** | Container v2.4.4 | Container | 2 min | ~8s | 2 | Production-like |
| **Timeout Test** | Fake URLs | Fake URLs | 0 min | ~8s | 0 | Robustness testing |

### Expected Test Results by Configuration

| **Configuration** | **Expected Outcome** | **Warnings** | **Skip Reason** |
|-------------------|---------------------|--------------|-----------------|
| **Development** | ✅ 3 passed, 2 skipped | None | No external services |
| **Mixed** | ✅ 3 passed, 2 skipped | Minor connection logs | Partial setup |
| **Full Remote** | ✅ 3 passed, 2 skipped | None | Both services working |
| **Timeout Test** | ✅ 3 passed, 2 skipped | Timeout warnings | Unreachable services |

### Container Commands Quick Reference

| **Service** | **Working Command** | **Status** | **Notes** |
|-------------|-------------------|------------|-----------|
| **Milvus v2.4.4** | `podman run -d --name milvus-remote -p 19530:19530 -e ETCD_USE_EMBED=true milvusdb/milvus:v2.4.4 /milvus/bin/milvus run standalone` | ✅ **WORKS** | Embedded etcd |
| **Milvus latest** | `podman run -d --name milvus-latest -p 19530:19530 milvusdb/milvus:latest standalone` | ❌ **BROKEN** | Exec failed |
| **Weaviate** | `podman run -d --name weaviate-test -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:latest` | ✅ **WORKS** | Anonymous auth |

### Environment Variables by Configuration

| **Configuration** | **MILVUS_URI** | **WEAVIATE_URL** | **WEAVIATE_API_KEY** | **Additional** |
|-------------------|----------------|------------------|---------------------|----------------|
| **Development** | *(unset)* | *(unset)* | *(unset)* | Uses local file |
| **Mixed** | *(unset)* | `http://localhost:8080` | `test-key` | Local + Remote |
| **Full Remote** | `http://localhost:19530` | `http://localhost:8080` | `test-key` | Both remote |
| **Timeout Test** | `http://fake:19530` | `http://fake:8080` | `fake` | Unreachable hosts |

### Step-by-Step Setup Guide

| **Step** | **Development** | **Mixed** | **Full Remote** | **Timeout Test** |
|----------|----------------|-----------|-----------------|------------------|
| **1. Milvus** | Nothing needed | Nothing needed | `podman run -d --name milvus-remote -p 19530:19530 -e ETCD_USE_EMBED=true milvusdb/milvus:v2.4.4 /milvus/bin/milvus run standalone` | Nothing needed |
| **2. Weaviate** | Nothing needed | `podman run -d --name weaviate-test -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:latest` | `podman run -d --name weaviate-test -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:latest` | Nothing needed |
| **3. Environment** | `unset MILVUS_URI WEAVIATE_URL WEAVIATE_API_KEY` | `unset MILVUS_URI && export WEAVIATE_URL="http://localhost:8080" WEAVIATE_API_KEY="test-key"` | `export MILVUS_URI="http://localhost:19530" WEAVIATE_URL="http://localhost:8080" WEAVIATE_API_KEY="test-key"` | `export MILVUS_URI="http://fake:19530" WEAVIATE_URL="http://fake:8080" WEAVIATE_API_KEY="fake"` |
| **4. Run Tests** | `./test.sh service` | `./test.sh service` | `./test.sh service` | `./test.sh service` |
| **5. Expected Time** | ~20 seconds | ~19 seconds | ~8 seconds | ~8 seconds |

### Troubleshooting Quick Reference

| **Problem** | **Symptom** | **Solution** |
|-------------|-------------|--------------|
| **Tests hang indefinitely** | No output, terminal stuck | Check for `milvus:latest` container - use `v2.4.4` instead |
| **"exec standalone failed"** | Container exits immediately | Use `/milvus/bin/milvus run standalone` command format |
| **"Invalid port: 8080:443"** | Weaviate connection error | Ensure `WEAVIATE_URL="http://localhost:8080"` (http, not https) |
| **"Client is closed"** | Weaviate warnings | Normal - fixed in timeout protection code |
| **All tests skip** | No services detected | Check environment variables are set correctly |

**✅ Option 1: Local File Database (RECOMMENDED)**
```bash
# No container needed - uses local file
# Milvus Lite automatically creates a local database file
unset MILVUS_URI  # Uses default: milvus_demo.db

# Optional: Use custom file location
export MILVUS_URI="file:///path/to/my_test.db"

# Optional: Set timeout for operations
export MILVUS_TIMEOUT=10
export MILVUS_RESYNC_TIMEOUT=15
```

**✅ Option 2: Container Mode (WORKING)**
```bash
# ✅ WORKING: Use specific version v2.4.4 with embedded etcd
docker run -d \
  --name milvus-remote \
  -p 19530:19530 \
  -e ETCD_USE_EMBED=true \
  milvusdb/milvus:v2.4.4 \
  /milvus/bin/milvus run standalone

# Set environment variables for remote connection
export MILVUS_URI="http://localhost:19530"
export MILVUS_TIMEOUT=10
export MILVUS_RESYNC_TIMEOUT=15
```

**❌ Option 3: Container Mode (BROKEN VERSIONS)**
```bash
# Known Issue: Latest version has startup problems
# These commands fail with various errors:

# Doesn't work - exec standalone failed:
docker run -d --name milvus-latest \
  -p 19530:19530 \
  -e ETCD_USE_EMBED=true \
  milvusdb/milvus:latest standalone

# Doesn't work - missing dependencies:
docker run -d --name milvus-simple \
  -p 19530:19530 \
  milvusdb/milvus:latest \
  milvus run standalone
```

### Weaviate Setup

**✅ Container Mode (WORKING)**
```bash
# Using Docker/Podman
docker run -d \
  --name weaviate-test \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:latest

# Set environment variables
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="test-key"  # Any value works with anonymous access
export WEAVIATE_RESYNC_TIMEOUT=10
```

### Recommended Configurations

**🎯 Quick Development Testing:**
```bash
# Local Milvus only - fastest setup
unset MILVUS_URI WEAVIATE_URL WEAVIATE_API_KEY
./test.sh service  # ~20s, no containers
```

**🎯 Mixed Local/Remote Testing:**
```bash
# Local Milvus + Containerized Weaviate
podman run -d --name weaviate-test -p 8080:8080 [full-weaviate-command]
unset MILVUS_URI  # Use local file
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="test-key"
./test.sh service  # ~19s
```

**🎯 Full Remote Testing (BOTH CONTAINERIZED):**
```bash
# Both Milvus and Weaviate in containers
podman run -d --name milvus-remote -p 19530:19530 -e ETCD_USE_EMBED=true milvusdb/milvus:v2.4.4 /milvus/bin/milvus run standalone
podman run -d --name weaviate-test -p 8080:8080 [full-weaviate-command]

export MILVUS_URI="http://localhost:19530"
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="test-key"
./test.sh service  # ~8s, both databases remote
```

**🎯 Timeout/Robustness Testing:**
```bash
# Test with unreachable databases
export MILVUS_URI="http://fake:19530"
export WEAVIATE_URL="http://fake:8080"
export WEAVIATE_API_KEY="fake"
export MILVUS_RESYNC_TIMEOUT=3
export WEAVIATE_RESYNC_TIMEOUT=3
./test.sh service  # ~8s, tests timeout handling
```

### Verification Commands
```bash
# Check containers are running
docker ps | grep -E "(milvus|weaviate)"

# Test Weaviate API
curl http://localhost:8080/v1/meta

# Test Milvus (if using container)
curl http://localhost:19530/health  # May not work - Milvus uses gRPC

# Run service tests
./test.sh service
```

### Troubleshooting

**Milvus Issues:**
- If container fails with "exec standalone failed", try without the `standalone` argument
- For simple testing, use local file option (no container needed)
- Local files are created automatically in the working directory

**Weaviate Issues:**  
- If you see "Invalid port" errors, ensure URL format is exactly `http://localhost:8080`
- Anonymous access must be enabled for tests to work
- Container needs a few seconds to start up completely

## Enhanced Test.sh Script Usage

The `./test.sh` script has been enhanced to support granular test execution:

### Python Test Categories (New)
```bash
# Fast, isolated tests with no external dependencies
./test.sh unit         # ~5-10 seconds

# Component integration tests with mocked external services  
./test.sh integration  # ~10-15 seconds

# Service tests with mocked external APIs
./test.sh service      # ~5-10 seconds

# Full Python stack end-to-end tests
./test.sh e2e          # ~10-15 seconds

# Combination of unit + integration for fast feedback
./test.sh fast         # ~15-20 seconds
```

### Legacy/Comprehensive Categories
```bash
# All Python tests (unit + integration + service + e2e)
./test.sh python       # ~30 seconds

# System integration tests only (CLI + MCP end-to-end)
./test.sh system       # ~2-5 minutes (requires external CLI)

# Everything: all Python tests + system integration
./test.sh all          # ~2-5 minutes

# Legacy mode (deprecated) - all Python tests without markers
./test.sh mcp          # ~30 seconds (consider using python instead)

# Default behavior (runs all Python tests)
./test.sh              # ~30 seconds (equivalent to ./test.sh python)

# CI-optimized test sequence (fast tests first, then comprehensive)
./test.sh ci           # ~2-5 minutes (fast feedback for failures)
```

### Development Workflow Examples
```bash
# Quick development cycle
./test.sh fast         # Fast feedback during coding (unit + integration)

# Before committing
./test.sh python       # Ensure all Python tests pass

# Full validation
./test.sh all          # Complete system validation

# Help and documentation
./test.sh help         # Detailed usage information
```

### CI/CD Integration
```bash
# Fast CI feedback
./test.sh fast         # Quick feedback for rapid iterations

# Optimized CI pipeline
./test.sh ci           # Runs fast tests first, then comprehensive tests

# Comprehensive CI validation
./test.sh all          # Complete validation including system tests

# Production deployment validation
./test.sh system       # System integration tests
```