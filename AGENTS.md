# AGENTS.md

This document provides AI agents with instructions and guidelines for interacting with and contributing to the Maestro Knowledge repository.

## 1. Project Overview

Maestro Knowledge is a modular vector database interface. It consists of two main components:

1.  **Python Backend (MCP Server)**: A server written in Python using FastAPI that provides a unified API (Model Context Protocol) for interacting with multiple vector database backends (e.g., Weaviate, Milvus).
2.  **Go CLI**: A command-line interface written in Go that allows users to interact with the MCP server to manage vector databases, collections, and documents.

The goal of this project is to provide a flexible and consistent way to work with different vector stores, abstracting away their specific implementations.

- **Python source code:** `src/`
- **Go CLI source code:** `cli/src/`
- **Python dependencies:** `pyproject.toml` and `uv.lock`
- **Go dependencies:** `cli/go.mod` and `cli/go.sum`

## 2. Getting Started & Environment Setup

### Python Environment

The Python environment is managed using `uv`.

1.  **Create a virtual environment:**
    ```bash
    uv venv
    ```
2.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    uv sync
    ```
    Run `uv sync` after pulling new changes to keep dependencies up-to-date.

### Go Environment

The Go CLI requires Go version 1.21 or later. Ensure Go is installed and available in your `PATH`.

### Environment Variables

The project uses a `.env` file in the root directory for configuration. You can copy `.env.example` to `.env` and fill in the required values.

Key environment variables:
- `WEAVIATE_API_KEY`: API key for Weaviate Cloud.
- `WEAVIATE_URL`: URL for your Weaviate cluster.
- `OPENAI_API_KEY`: API key for OpenAI, used for certain embedding models.
- `MAESTRO_KNOWLEDGE_MCP_SERVER_URI`: The URI for the MCP server, used by the CLI. Defaults to `http://localhost:8030`.

## 3. How to Build

### Building the Go CLI

The Go CLI is the only component that requires an explicit build step.

To build the CLI binary (`maestro-k`):
```bash
cd cli
./build.sh
```
This script runs `go build` and places the executable in the `cli/` directory.

### Python Backend

The Python backend does not require a build step. It can be run directly after installing dependencies.

To start the MCP server:
```bash
./start.sh
```

To stop the server:
```bash
./stop.sh
```

## 4. How to Test

This project has separate test suites for the Python backend and the Go CLI. There is also a master script to run all tests.

### Running All Tests

To run the complete test suite for both Python and Go:
```bash
./test.sh all
```

### Python (MCP Server) Tests

To run only the Python tests:
```bash
./test.sh mcp
```
This command executes `PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -v`.

### Go (CLI) Tests

To run the Go tests, navigate to the `cli` directory. The test script has options for unit and integration tests.

1.  **Run unit tests:**
    ```bash
    cd cli
    ./test.sh unit
    ```
    This runs a series of `go test` commands with flags for verbosity, coverage, and race detection.

2.  **Run integration tests:**
    ```bash
    cd cli
    ./test.sh integration
    ```
    **Note:** The integration tests require the MCP server to be running. Start it with `./start.sh` from the root directory before running these tests.

## 5. How to Lint

The project uses `ruff` for Python and a collection of Go tools for linting. There is a master script to run all linters.

### Running All Linters

To run all linting checks for both Python and Go:
```bash
./tools/lint.sh
```

### Python Linting

The Python linter is `ruff`. The script runs both `check` and `format --check`.

To run Python linting manually:
```bash
# Check for linting errors
uv run ruff check src/ tests/ examples/

# Check for formatting issues
uv run ruff format --check src/ tests/ examples/
```

### Go Linting

The Go linter script is comprehensive. To run it:
```bash
cd cli
./lint.sh
```
This script executes a series of checks, including:
- `go fmt` (formatting)
- `go vet` (static analysis)
- `go mod tidy/verify` (dependency health)
- `golangci-lint` (advanced linting)
- `staticcheck` (unused code detection)
- `go test -race` (race condition detection)

## 6. Development Workflow & Coding Standards

### General Workflow

1.  Create a feature branch.
2.  Make your code changes.
3.  **Ensure code quality:**
    - Run linters: `./tools/lint.sh`
    - Run tests: `./test.sh all`
4.  Commit your changes.
5.  Push to your branch and open a Pull Request.

The pre-PR checklist in `docs/CONTRIBUTING.md` requires the following command to pass: `./tools/lint.sh && ./test.sh all && ./test-integration.sh`.

### Python Standards

- Follow PEP 8 guidelines.
- Use `ruff` for formatting.
- All new functionality should be covered by tests.
- When adding a new vector database backend, implement the `VectorDatabase` abstract base class from `src/db/vector_db_base.py`.

### Go Standards

- Follow standard Go conventions.
- Use `go fmt` for formatting.
- All new functionality should be covered by tests.
- CLI commands should be added in their own files in `cli/src/`.

Refer to `docs/CONTRIBUTING.md` for more detailed guidelines on adding new features, database backends, and MCP server tools.
