# Test Classification for Maestro Knowledge

## Test Types and Requirements

### 1. Unit Tests (`@pytest.mark.unit`)
- **File pattern:** `test_unit_*.py`
- **Requirements:** NO external dependencies
- **Speed:** Fast (<1s per test)
- **What to test:**
  - Pydantic model validation (`QueryInput`, etc.)
  - Individual function logic
  - Class methods in isolation
- **Mocking:** Mock ALL external dependencies
- **Example:**
  ```python
  @pytest.mark.unit
  def test_query_input_validation():
      """Test QueryInput model validation."""
      query_input = QueryInput(db_name="test-db", query="test", limit=5)
      assert query_input.db_name == "test-db"
  ```

### 2. Component Integration Tests (`@pytest.mark.integration`)
- **File pattern:** `test_integration_*.py` 
- **Requirements:** NO external services running
- **Speed:** Medium (1-5s per test)
- **What to test:**
  - MCP server creation and tool registration
  - Components working together with mocked external services
  - Tool invocation with mocked databases
- **Mocking:** Mock external services (database connections) but use real internal components
- **Example:**
  ```python
  @pytest.mark.integration
  async def test_mcp_server_query_workflow():
      """Test complete query workflow with mocked database."""
      with mock_database_responses():
          server = await create_mcp_server()
          result = await invoke_tool(server, "query", {...})
          assert "expected response" in result
  ```

### 3. Service Integration Tests (`@pytest.mark.service` or `@pytest.mark.requires_db`)
- **File pattern:** `test_service_*.py`
- **Requirements:** Real databases must be running (Milvus, Weaviate)
- **Speed:** Slow (5-30s per test)
- **What to test:**
  - Full workflows with real database connections
  - Data persistence and retrieval
  - Database-specific behavior
- **Mocking:** Minimal - only external APIs, not databases
- **Setup:** Requires database containers or services
- **Example:**
  ```python
  @pytest.mark.service
  @pytest.mark.requires_milvus
  async def test_real_milvus_query():
      """Test with real Milvus database."""
      # Assumes Milvus is running
      server = await create_mcp_server()
      # Real database operations
  ```

### 4. End-to-End Tests (`@pytest.mark.e2e`)
- **File pattern:** `test_e2e_*.py`
- **Requirements:** Full environment (databases, CLI tools, etc.)
- **Speed:** Very slow (30s+ per test)
- **What to test:**
  - Complete user workflows
  - CLI interactions
  - Cross-system integration
- **Mocking:** None - everything real

## Test Execution Strategy

### Default (CI/Local development)
```bash
pytest -m "unit or integration"  # Fast tests only
```

### With Services (Local development with databases)
```bash
pytest -m "unit or integration or service"
```

### Full Suite (CI with full environment)
```bash
pytest  # All tests including e2e
```

## Current Test Analysis

### Files to Refactor:
1. `test_mcp_server.py` → Split into unit + integration
2. `test_mcp_query.py` → Mostly unit tests 
3. `test_query_integration.py` → True integration tests

### Proposed New Structure:
```
tests/
├── unit/
│   ├── test_unit_models.py          # QueryInput validation
│   ├── test_unit_server_components.py
│   └── test_unit_utilities.py
├── integration/
│   ├── test_integration_mcp_server.py    # Server + mocked DB
│   ├── test_integration_query_workflow.py
│   └── test_integration_tools.py
├── service/
│   ├── test_service_milvus.py        # Requires Milvus running
│   ├── test_service_weaviate.py     # Requires Weaviate running
│   └── test_service_full_workflow.py
└── e2e/
    └── test_e2e_cli.py              # CLI integration tests
```