# Maestro Knowledge

A modular vector database interface supporting multiple backends (Weaviate, Milvus) with a unified API.

## Features

- **Multi-backend support**: Weaviate and Milvus vector databases
- **Unified API**: Consistent interface across different vector database implementations
- **Factory pattern**: Easy creation and switching between database types
- **MCP Server**: Model Context Protocol server for AI agent integration
- **Document management**: Write, read, delete, and query documents
- **Metadata support**: Rich metadata handling for documents

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd maestro-knowledge

# Install dependencies
uv sync
```

### Basic Usage

```python
from src.vector_db import create_vector_database

# Create a vector database (defaults to Weaviate)
db = create_vector_database("weaviate", "MyCollection")

# Set up the database
db.setup()

# Write documents
documents = [
    {
        "url": "https://example.com/doc1",
        "text": "This is a document about machine learning.",
        "metadata": {"topic": "ML", "author": "Alice"}
    }
]
db.write_documents(documents)

# List documents
docs = db.list_documents(limit=10)
print(f"Found {len(docs)} documents")

# Clean up
db.cleanup()
```

## MCP Server

The project includes a Model Context Protocol (MCP) server that exposes vector database functionality to AI agents through a standardized interface.

### Running the MCP Server

```bash
# Start the MCP server
./start.sh

# Stop the MCP server
./stop.sh

# Check server status
./stop.sh status

# Restart the server
./stop.sh restart
```

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

- **create_vector_database**: Create a new vector database instance
- **setup_database**: Set up the current vector database
- **write_document**: Write a single document
- **write_documents**: Write multiple documents
- **list_documents**: List documents from the database
- **count_documents**: Get document count
- **delete_document**: Delete a single document
- **delete_documents**: Delete multiple documents
- **delete_collection**: Delete an entire collection
- **cleanup**: Clean up resources
- **get_database_info**: Get database information

For more details, see [src/maestro_mcp/README.md](src/maestro_mcp/README.md).

## Examples

See the [examples/](examples/) directory for usage examples:

- [Weaviate Example](examples/weaviate_example.py)
- [Milvus Example](examples/milvus_example.py)
- [MCP Server Example](examples/mcp_example.py)

## Testing

```bash
# Run tests
./tests.sh

# Or run individual test files
python -m pytest tests/
```

## Project Structure

```
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
├── start.sh                 # MCP server start script
├── stop.sh                  # MCP server stop script
├── tests/                   # Test suite
│   ├── test_vector_db_*.py  # Vector database tests
│   ├── test_mcp_server.py   # MCP server tests
│   └── test_integration_*.py # Integration tests
├── examples/                # Usage examples
│   ├── weaviate_example.py  # Weaviate usage
│   ├── milvus_example.py    # Milvus usage
│   └── mcp_example.py       # MCP server usage
└── docs/                    # Documentation
    └── CONTRIBUTING.md      # Contribution guidelines
```

## Environment Variables

- `VECTOR_DB_TYPE`: Default vector database type (defaults to "weaviate")
- Database-specific environment variables for Weaviate and Milvus connections

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
