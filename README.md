# Maestro Knowledge

A modular vector database interface supporting multiple backends (Weaviate, Milvus) with a unified API and flexible embedding strategies.

## Features

- **Multi-backend support**: Weaviate and Milvus vector databases
- **Flexible embedding strategies**: Support for pre-computed vectors and multiple embedding models
- **Unified API**: Consistent interface across different vector database implementations
- **Factory pattern**: Easy creation and switching between database types
- **MCP Server**: Model Context Protocol server for AI agent integration with multi-database support
- **CLI Tool**: Command-line interface for vector database operations with YAML configuration
- **Document management**: Write, read, delete, and query documents
- **Collection management**: List and manage collections across vector databases
- **Query functionality**: Natural language querying with semantic search across documents
- **Metadata support**: Rich metadata handling for documents
- **Environment variable substitution**: Dynamic configuration with `{{ENV_VAR_NAME}}` syntax

## Quick Start

### Installation

First, clone the repository and navigate into the directory:

```bash
git clone https://github.com/AI4quantum/maestro-knowledge.git
cd maestro-knowledge
```

You will need [Python](https://www.python.org/) 3.11+ and [uv](https://docs.astral.sh/uv/#highlights).

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Next, install the required dependencies:

```bash
uv sync
```

This should be rerun after pulling changes to ensure all dependencies are up-to-date.

### Basic Usage

```python
from src.vector_db import create_vector_database

# Create a vector database (defaults to Weaviate)
db = create_vector_database("weaviate", "MyCollection")

# Set up the database
db.setup()

# Write documents with default embedding
documents = [
    {
        "url": "https://example.com/doc1",
        "text": "This is a document about machine learning.",
        "metadata": {"topic": "ML", "author": "Alice"}
    }
]
db.write_documents(documents, embedding="default")

# List documents
docs = db.list_documents(limit=10)
print(f"Found {len(docs)} documents")

# Query documents using natural language
results = db.query("What is the main topic of the documents?", limit=5)
print(f"Query results: {results}")

# Clean up
db.cleanup()
```

## Embedding Strategies

The library supports flexible embedding strategies for both vector databases. For detailed embedding model support and usage examples, see [src/maestro_mcp/README.md](src/maestro_mcp/README.md).

### Quick Overview

- **Weaviate**: Supports built-in vectorizers and external embedding models
- **Milvus**: Supports pre-computed vectors and OpenAI embedding models
- **Environment Variables**: Set `OPENAI_API_KEY` for OpenAI embedding models

### Basic Usage

```python
# Check supported embeddings
supported = db.supported_embeddings()
print(f"Supported embeddings: {supported}")

# Write documents with specific embedding
db.write_documents(documents, embedding="text-embedding-3-small")
```

## CLI Tool

The project includes a Go-based CLI tool for managing vector databases through the MCP server with support for YAML configuration and environment variable substitution.

### Installation

```bash
# Build the CLI tool
cd cli
go build -o maestro-k src/*.go

# Or use the build script
./build.sh
```

### Basic Usage

The CLI provides concise error output by default and detailed verbose output when needed. For comprehensive CLI usage examples and detailed command reference, see [cli/README.md](cli/README.md).

```bash
# List vector databases (using plural form)
./maestro-k list vector-dbs

# List embeddings for a specific database
./maestro-k list embeds my-database

# List collections for a specific database
./maestro-k list cols my-database

# List documents in a collection
./maestro-k list docs my-database my-collection

# Query documents using natural language
./maestro-k query my-database "What is the main topic of the documents?"

# Create vector database from YAML
./maestro-k create vector-db config.yaml

# Validate YAML configuration
./maestro-k validate config.yaml
```

### Configuration

The CLI supports multiple configuration methods including environment variables, command-line flags, and `.env` files. For detailed configuration options and environment variable substitution examples, see [cli/README.md](cli/README.md).

## MCP Server

The project includes a Model Context Protocol (MCP) server that exposes vector database functionality to AI agents through a standardized interface with support for multiple simultaneous databases.

### Running the MCP Server

```bash
# Start the MCP server
./start.sh

# Stop the MCP server
./stop.sh

# Check server status with detailed information
./stop.sh status

# Restart the server
./stop.sh restart

# Restart HTTP server specifically
./stop.sh restart-http

# Clean up stale files
./stop.sh cleanup
```

### MCP Server Features

The MCP server includes enhanced process management with:

- **✅ Visual status indicators** - Green checkmarks and red X marks for clear status display
- **📄 PID file management** - Automatic cleanup of stale process IDs
- **🌐 Port monitoring** - Real-time port availability checking
- **🔄 Graceful restarts** - Proper process cleanup and restart sequencing
- **🧹 Automatic cleanup** - Removal of stale files and processes

### MCP Configuration

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "maestro-vector-db": {
      "command": "python",
      "args": ["-m", "src.maestro_mcp.server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### Available MCP Tools

The MCP server provides comprehensive tools for database management, document operations, and querying. For detailed tool descriptions and usage examples, see [src/maestro_mcp/README.md](src/maestro_mcp/README.md).

**Key Tool Categories:**
- **Database Management**: Create, setup, and manage vector databases
- **Document Operations**: Write, list, and delete documents with flexible embedding strategies
- **Query Functionality**: Natural language querying with semantic search
- **Collection Management**: List and manage collections across databases

### Multi-Database Support

The MCP server supports managing multiple vector databases simultaneously. Each database is identified by a unique name, allowing you to:

- Create and manage multiple databases of different types (Weaviate, Milvus)
- Use different databases for different purposes or projects
- Operate on specific databases by providing the database name in tool calls
- List all available databases and their status

For more details, see [src/maestro_mcp/README.md](src/maestro_mcp/README.md).

## Examples

See the [examples/](examples/) directory for usage examples:

- [Weaviate Example](examples/weaviate_example.py) - Demonstrates Weaviate with different embedding models and querying
- [Milvus Example](examples/milvus_example.py) - Shows Milvus with pre-computed vectors, embedding models, and querying
- [MCP Server Example](examples/mcp_example.py) - Demonstrates MCP server integration including query functionality

## Available Scripts

The project includes several utility scripts for development and testing:

```bash
# Code quality and formatting
./tools/lint.sh              # Run linting and formatting checks

# MCP server management
./start.sh                   # Start the MCP server
./stop.sh                    # Stop the MCP server

# Testing
./test.sh [COMMAND]          # Run tests with options: cli, mcp, all, help
./test-integration.sh        # Run CLI integration tests
./tools/e2e.sh all          # Run end-to-end tests

# CLI tool
cd cli && ./build.sh         # Build the CLI tool
```

## Testing

```bash
# Run all tests (CLI + MCP + Integration)
./test.sh all

# Run specific test suites
./test.sh cli                # Run only CLI tests
./test.sh mcp                # Run only MCP server tests
./test.sh help               # Show test command help

# Run comprehensive test suite (recommended before PR)
./tools/lint.sh && ./test.sh all

# Run integration and end-to-end tests
./test-integration.sh        # CLI integration tests
./tools/e2e.sh all          # Complete e2e workflows

# Monitor logs in real-time
./tools/tail-logs.sh status  # Show service status
./tools/tail-logs.sh all     # Tail all service logs
```

## Project Structure

```text
maestro-knowledge/
├── src/                     # Source code
│   ├── db/                  # Vector database implementations
│   │   ├── vector_db_base.py      # Abstract base class
│   │   ├── vector_db_weaviate.py  # Weaviate implementation
│   │   ├── vector_db_milvus.py    # Milvus implementation
│   │   └── vector_db_factory.py   # Factory function
│   ├── maestro_mcp/         # MCP server implementation
│   │   ├── server.py        # Main MCP server
│   │   ├── mcp_config.json  # MCP client configuration
│   │   └── README.md        # MCP server documentation
│   └── vector_db.py         # Main module exports
├── cli/                     # Go CLI tool
│   ├── src/                 # Go source code
│   ├── tests/               # CLI tests
│   ├── examples/            # CLI usage examples
│   ├── build.sh             # Build script
│   └── README.md            # CLI documentation
├── start.sh                 # MCP server start script
├── stop.sh                  # MCP server stop script
├── tools/                   # Development tools
│   ├── lint.sh              # Code linting and formatting
│   ├── e2e.sh               # End-to-end testing script
│   ├── test-integration.sh  # Integration tests
│   └── tail-logs.sh        # Real-time log monitoring script
├── test.sh                  # Test runner script (CLI, MCP, Integration)
├── tests/                   # Test suite
│   ├── test_vector_db_*.py  # Vector database tests
│   ├── test_mcp_server.py   # MCP server tests
│   ├── test_query_*.py      # Query functionality tests
│   ├── test_integration_*.py # Integration tests
│   ├── test_vector_database_yamls.py # YAML schema validation tests
│   └── yamls/               # YAML configuration examples
│       ├── test_local_milvus.yaml
│       └── test_remote_weaviate.yaml
├── examples/                # Usage examples
│   ├── weaviate_example.py  # Weaviate usage
│   ├── milvate_example.py   # Milvus usage
│   └── mcp_example.py       # MCP server usage
├── schemas/                 # JSON schemas
│   ├── vector-database-schema.json # Vector database configuration schema
│   └── README.md            # Schema documentation
└── docs/                    # Documentation
    ├── CONTRIBUTING.md      # Contribution guidelines
    └── PRESENTATION.md      # Project presentation
```

## Environment Variables

- `VECTOR_DB_TYPE`: Default vector database type (defaults to "weaviate")
- `OPENAI_API_KEY`: Required for OpenAI embedding models
- `MAESTRO_KNOWLEDGE_MCP_SERVER_URI`: MCP server URI for CLI tool
- `MILVUS_URI`: Milvus connection URI. **Important**: Do not use quotes around the URI value in your `.env` file (e.g., `MILVUS_URI=http://localhost:19530` instead of `MILVUS_URI="http://localhost:19530"`).
- Database-specific environment variables for Weaviate and Milvus connections

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

### Pre-Pull Request Checklist

Before submitting a pull request, run the comprehensive test suite:

```bash
./tools/lint.sh && ./test.sh all
```

This ensures code quality, functionality, and integration with the CLI tool.

### Recommended Development Workflow

For a complete development workflow that tests everything end-to-end:

```bash
./start.sh && ./tools/e2e.sh fast && ./stop.sh
```

This workflow:

1. Starts the MCP server
2. Runs the fast end-to-end test suite
3. Stops the MCP server

This is useful for quickly validating that your changes work correctly in a real environment.

### Log Monitoring

The project includes comprehensive log monitoring capabilities:

```bash
# Show service status with visual indicators
./tools/tail-logs.sh status

# Monitor all logs in real-time
./tools/tail-logs.sh all

# Monitor specific service logs
./tools/tail-logs.sh mcp    # MCP server logs
./tools/tail-logs.sh cli    # CLI logs

# View recent logs
./tools/tail-logs.sh recent
```

**Log Monitoring Features:**
- **📡 Real-time tailing** - Monitor logs as they're generated
- **✅ Visual status indicators** - Clear service status with checkmarks and X marks
- **🌐 Port monitoring** - Check service availability on ports
- **📄 Log file management** - Automatic detection and size tracking
- **🔍 System integration** - macOS system log monitoring for debugging
- **🎯 Service-specific monitoring** - Tail individual service logs or all at once

## License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.
