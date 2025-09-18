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

### Milvus Setup
```bash
# Using Docker
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -e ETCD_USE_EMBED=true \
  milvusdb/milvus:latest standalone

# Set environment variables
export MILVUS_URI="http://localhost:19530"
```

### Weaviate Setup
```bash
# Using Docker
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  semitechnologies/weaviate:latest

# Set environment variables
export WEAVIATE_URL="http://localhost:8080"
export WEAVIATE_API_KEY="your-api-key"
```

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
# All Python tests (legacy mode - equivalent to pytest -v)
./test.sh mcp          # ~30 seconds

# Full system integration: CLI + MCP server + databases
./test.sh system-e2e   # ~2-5 minutes (requires external CLI)

# Everything: all Python tests + system integration
./test.sh all          # ~2-5 minutes

# Default behavior (runs all Python tests)
./test.sh              # ~30 seconds
```

### Development Workflow Examples
```bash
# Quick development cycle
./test.sh fast         # Fast feedback during coding

# Before committing  
./test.sh mcp          # Ensure all Python tests pass

# Full validation
./test.sh all          # Complete system validation

# Help and documentation
./test.sh help         # Detailed usage information
```

### CI/CD Integration
```bash
# Fast CI feedback
./test.sh fast

# Comprehensive CI validation
./test.sh all

# Production deployment validation
./test.sh system-e2e
```