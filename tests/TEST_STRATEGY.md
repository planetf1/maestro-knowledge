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
# Or simply (uses default configuration)
uv run pytest
```

### Pre-commit Validation
```bash
# Run standard tests (unit + integration)
uv run pytest -m "unit or integration" -v
```

### Full Test Suite
```bash
# Run all tests including end-to-end
uv run pytest -v --no-markers
# Or explicitly
uv run pytest -m "unit or integration or e2e" -v
```

### Default Configuration
The project is configured to discover all tests when running `uv run pytest`. E2E tests will be skipped if milvus/weaviate is not available and report reason.

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

## Environment Setup for E2E Tests

For E2E testing setup, see the detailed documentation in `tests/e2e/README.md` which covers container setup scripts, environment configuration, and running comprehensive E2E test suites.

### Basic Test Categories

```bash



## Enhanced Test.sh Script Usage

The `./test.sh` script has been simplified to support intuitive test execution:

### Basic Test Categories
```bash
# Fast, isolated tests with no external dependencies
./test.sh unit         # ~5 seconds

# Component integration tests with mocked external services
./test.sh integration  # ~5 seconds

# End-to-end tests requiring external dependencies  
./test.sh e2e          # See e2e/README.md for setup

# End-to-end tests requiring full environment
./test.sh e2e          # (currently no tests marked with e2e)
```

### Combined Test Categories

```bash
# Standard tests (unit + integration) - no external dependencies
./test.sh standard     # ~10 seconds

# Everything: all tests including those with external dependencies
./test.sh all          # ~30 seconds (with databases available)

# Default behavior (runs standard tests)
./test.sh              # ~10 seconds (equivalent to ./test.sh standard)
```

### Development Workflow Examples

```bash
# Quick development cycle
./test.sh unit         # Fast unit tests for quick feedback (~5s)

# Standard development testing
./test.sh standard     # Standard tests (unit + integration) (~10s)
# Or simply
./test.sh              # Same as standard (default)

# Before committing
./test.sh standard     # Ensure standard tests pass

# Testing with external dependencies (when available)
./test.sh service      # Service tests with external databases (~20s)
./test.sh e2e          # End-to-end tests with external dependencies

# Full validation (when external services are available)
./test.sh all          # Complete system validation

# Help and documentation
./test.sh help         # Detailed usage information
```

### CI/CD Integration

```bash
# Standard CI validation
./test.sh standard     # Standard tests for CI pipelines (no external deps)

# Comprehensive validation (when external services are available)
./test.sh all          # Complete validation including external dependencies
```

### Consistency with pytest

The test script behavior is consistent with direct pytest usage:

```bash
# These commands are equivalent:
./test.sh standard
uv run pytest          # Uses default configuration from pyproject.toml

# These commands are equivalent:
./test.sh unit
uv run pytest -m "unit"

# These commands are equivalent:
./test.sh all
uv run pytest --no-markers
```
