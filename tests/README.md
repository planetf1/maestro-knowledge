# Tests Directory Structure

This directory contains all test-related files and documentation for the maestro-knowledge project.

## Directory Structure

```
tests/
├── docs/           # Test-related documentation
│   └── e2e_testing.md    # End-to-end testing guide
├── setup/          # Test environment setup scripts
│   ├── milvus_arm64.sh   # ARM64 Milvus setup for Apple Silicon
│   └── milvus_e2e.sh     # Generic Milvus E2E setup
├── e2e/            # End-to-end tests
│   ├── test_mcp_milvus_e2e.py
│   └── test_mcp_weaviate_e2e.py
├── chunking/       # Chunking strategy tests
├── helpers.py      # Test utilities
└── test_*.py       # Unit and integration tests
```

## Running Tests

### Unit Tests
```bash
uv run python -m pytest tests/test_*.py -v
```

### Integration Tests  
```bash
uv run python -m pytest tests/ -m integration -v
```

### End-to-End Tests
See `docs/e2e_testing.md` for detailed setup instructions.

For Milvus E2E tests:
1. Set up services: `./tests/setup/milvus_arm64.sh`
2. Run tests: `uv run python -m pytest tests/e2e/test_mcp_milvus_e2e.py -xvs`

## Test Categories

- **Unit**: Fast tests with no external dependencies
- **Integration**: Component interaction tests with mocked externals  
- **E2E**: Full end-to-end workflow tests with real databases

Use pytest markers to run specific categories:
```bash
uv run python -m pytest -m "unit"
uv run python -m pytest -m "e2e and requires_milvus"
```