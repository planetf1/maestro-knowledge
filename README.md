# Maestro Knowledge

A modular vector database interface supporting multiple backends (Weaviate, Milvus) with a unified API and flexible embedding strategies.

## Features

- **Multi-backend support**: Weaviate and Milvus vector databases
- **Flexible embedding strategies**: Support for pre-computed vectors and multiple embedding models
- **Pluggable document chunking**: None (default), Fixed (size/overlap), Sentence-aware, Semantic (AI-powered)
- **Unified API**: Consistent interface across different vector database implementations
- **Factory pattern**: Easy creation and switching between database types
- **MCP Server**: Model Context Protocol server for AI agent integration with multi-database support
- **CLI Tool**: Command-line interface for vector database operations (separate repository: AI4quantum/maestro-k-cli)
- **Document management**: Write, read, delete, and query documents
- **Collection management**: List and manage collections across vector databases
- **Query functionality**: Natural language querying with semantic search across documents
- **Metadata support**: Rich metadata handling for documents
- **Environment variable substitution**: Dynamic configuration with `{{ENV_VAR_NAME}}` syntax
- **Safety features**: Confirmation prompts for destructive operations with `--force` flag bypass

## Chunking Strategies

Maestro Knowledge supports multiple document chunking strategies to optimize how your documents are split for vector search:

### Available Strategies

- **None**: No chunking performed (default)
- **Fixed**: Split documents into fixed-size chunks with optional overlap
- **Sentence**: Split documents at sentence boundaries with size limits  
- **Semantic**: Identifies semantic boundaries using sentence embeddings

### Semantic Chunking

The semantic chunking strategy uses sentence transformers to intelligently split documents:

```python
from src.chunking import ChunkingConfig, chunk_text

# Configure semantic chunking
config = ChunkingConfig(
    strategy="Semantic",
    parameters={
        "chunk_size": 768,      # Default for semantic (vs 512 for others)
        "overlap": 0,           # Optional overlap between chunks
        "window_size": 1,       # Context window for similarity calculation
        "threshold_percentile": 90.0,  # Percentile threshold for splits
        "model_name": "all-MiniLM-L6-v2"  # Sentence transformer model
    }
)

# Chunk your text
chunks = chunk_text("Your document text here...", config)
```

**Key Benefits**:
- Preserves semantic meaning across chunk boundaries
- Automatically finds natural break points in text
- Respects size limits while maintaining context
- Uses 768 character default (optimal for semantic understanding)

**Note**: Semantic chunking uses sentence-transformers for chunking decisions, but the resulting chunks are embedded using your collection's embedding model (e.g., nomic-embed-text) for search operations.

### Testing Semantic Chunking

You can test the semantic chunking functionality using the CLI:

```bash
# Check collection information to see chunking strategy
cli/maestro-k-k collection info --vdb "Qiskit_studio_algo" --name "Qiskit_studio_algo"

# Search with semantic chunking to see results
./cli/maestro-k-k search "quantum circuit" --vdb qiskit_studio_algo --collection qiskit_studio_algo --doc-limit 1
```

**Note**: The semantic chunking strategy uses sentence-transformers for chunking decisions, while the collection's own embedding model is used for search operations.

## Quick Start

### Installation

First, clone the repository and navigate into the directory:

```bash
git clone https://github.com/AI4quantum/maestro-k-knowledge.git
cd maestro-k-knowledge
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

### Weaviate Quick Start
#### 1. Set Up Weaviate Cloud

Get free account at weaviate.io, create a cluster/credentials and put into .env file in project root.

```bash
WEAVIATE_API_KEY=your-api-key-here
WEAVIATE_URL=https://your-cluster-name.weaviate.network
```

#### 2. Install CLI and Start Services
```bash
# Install maestro-k CLI (from separate repository)
# See: https://github.com/AI4quantum/maestro-cli for installation instructions
# Build the CLI: cd /path/to/maestro-cli && ./build.sh
# The CLI binary will be available as 'maestro' in the maestro-cli directory

# Start MCP server
./start.sh
```

#### 3. Create Your First Database
```bash
# Create config file (my_database.yaml)
apiVersion: maestro-k/v1alpha1
kind: VectorDatabase
metadata:
  name: my_first_database
spec:
  type: weaviate
  uri: your-cluster-name.weaviate.network
  collection_name: my_documents
  embedding: default
  mode: remote

# Create the database (using full path to CLI binary)
/path/to/maestro-cli/commands vectordb create my_database.yaml

# Verify creation
/path/to/maestro-cli/commands vectordb list
```

#### 4. Add and Query Documents

As of now, document ingestion process is manual. This will be updated in the future.

```
#### Create a text file with your content
echo "Your document content here" > my_doc.txt

# Add document to database
/path/to/maestro-cli/commands document create --vdb=my_first_database --collection=My_documents --name=my_doc --file=my_doc.txt

# Query your documents
/path/to/maestro-cli/commands query "What is your question?" --vdb=my_first_database --collection=My_documents

# List all documents
/path/to/maestro-cli/commands document list --vdb=my_first_database --collection=My_documents
```

#### 5. Test Your Setup
```bash
# Verify everything is working
/path/to/maestro-cli/commands vectordb list                    # Should show your database
/path/to/maestro-cli/commands collection list --vdb=my_first_database  # Should show collections
/path/to/maestro-cli/commands document list --vdb=my_first_database --collection=My_documents  # Should show your documents

# Try a semantic search query
/path/to/maestro-cli/commands query "What is machine learning?" --vdb=my_first_database --collection=My_documents
```

## Components

### CLI Tool

The CLI tool has been moved to a separate repository: [AI4quantum/maestro-k-cli](https://github.com/AI4quantum/maestro-k-cli). This Go-based CLI tool manages vector databases through the MCP server.

**Prerequisites:**
- Install the maestro CLI from the separate repository: [AI4quantum/maestro-cli](https://github.com/AI4quantum/maestro-cli)
- Build the CLI: `cd /path/to/maestro-cli && ./build.sh`
- Add the CLI to your PATH or place it in a relative path from your project

**Quick CLI Examples:**
 
```bash
# List vector databases (if in PATH)
maestro vectordb list

# Or using relative path
../maestro-cli/maestro vectordb list

# Create vector database from YAML
maestro vectordb create config.yaml

# Query documents
maestro query "What is the main topic?" --vdb=my-database

# Resync any Milvus collections into the MCP server's in-memory registry (use after server restart)
maestro resync-databases
```

### MCP Server

The project includes a Model Context Protocol (MCP) server that exposes vector database functionality to AI agents. For detailed MCP server documentation, configuration, and examples, see [src/maestro-k_mcp/README.md](src/maestro-k_mcp/README.md).

**Quick MCP Server Usage:**
```bash
# Start the MCP server
./start.sh

# Stop the MCP server
./stop.sh

# Check server status
./stop.sh status

# Manual resync tool (available as an MCP tool and through the CLI `resync-databases` command):
# After restarting the MCP server, run the resync to register existing Milvus collections:
/path/to/maestro-cli/commands resync-databases
```

### Search and Query Output

- Search returns JSON results suitable for programmatic use.
- Query returns a human-readable text summary (no JSON flag).

Search result schema (normalized across Weaviate and Milvus):

- id: unique chunk identifier
- url: source URL or file path
- text: chunk text
- metadata:
    - doc_name: original document name/slug
    - chunk_sequence_number: 1-based chunk index within the document
    - total_chunks: total chunks for the document
    - offset_start / offset_end: character offsets in the original text
    - chunk_size: size of the chunk in characters
- similarity: canonical relevance score in [0..1]
- distance: cosine distance (approximately 1 − similarity); included for convenience
- rank: 1-based rank in the current result set
- _metric: similarity metric name (e.g., "cosine")
- _search_mode: "vector" (vector similarity) or "keyword" (fallback)


## Embedding Strategies

The library supports flexible embedding strategies for both vector databases. For detailed embedding model support and usage examples, see [src/maestro-k_mcp/README.md](src/maestro-k_mcp/README.md).

### Quick Overview

- **Weaviate**: Supports built-in vectorizers and external embedding models
- **Milvus**: Supports pre-computed vectors and OpenAI embedding models
- **Environment Variables**: Set `OPENAI_API_KEY` for OpenAI embedding models

### Embedding Usage

```python
# Check supported embeddings
supported = db.supported_embeddings()
print(f"Supported embeddings: {supported}")

# Write documents with specific embedding
(Deprecated) Embedding is configured per collection. Any per-document embedding specified in writes is ignored.
db.write_documents(documents, embedding="text-embedding-3-small")
```

## Examples

See the [examples/](examples/) directory for usage examples:

- [Weaviate Example](examples/weaviate_example.py) - Demonstrates Weaviate with different embedding models and querying
- [Milvus Example](examples/milvus_example.py) - Shows Milvus with pre-computed vectors, embedding models, and querying
- [MCP Server Example](examples/mcp_example.py) - Demonstrates MCP server integration including query functionality

## Available Scripts

The project includes several utility scripts for development and testing:

```bash
# Code quality and formatting
./tools/lint.sh              # Run Python linting and formatting checks
# Go linting is now in the separate CLI repository: AI4quantum/maestro-k-cli

# MCP server management
./start.sh                   # Start the MCP server
./stop.sh                    # Stop the MCP server

# Testing
./test.sh [COMMAND]          # Run tests with options: cli, mcp, all, help
./test-integration.sh        # Run CLI integration tests (requires maestro-k CLI in PATH)
./tools/e2e.sh all          # Run end-to-end tests (requires maestro-k CLI in PATH)

# CLI tool
# CLI is now in separate repository: AI4quantum/maestro-k-cli
```

## Testing

```bash
# Run all tests (MCP + Integration)
./test.sh all

# Run specific test suites
./test.sh cli                # CLI tests (redirected to separate repository)
./test.sh mcp                # Run only MCP server tests
./test.sh help               # Show test command help

# Run comprehensive test suite (recommended before PR)
./tools/lint.sh && ./test.sh all

# Run integration and end-to-end tests (requires maestro-k CLI in PATH)
./test-integration.sh        # CLI integration tests
./tools/e2e.sh all          # Complete e2e workflows

# Monitor logs in real-time
./tools/tail-logs.sh status  # Show service status
./tools/tail-logs.sh all     # Tail all service logs
```

## Code Quality

The project maintains high code quality standards through comprehensive linting and automated checks.

### Python Code Quality

- **ruff**: Fast Python linter and formatter
- **Formatting**: Consistent code style across Python files
- **Import sorting**: Organized and clean imports
- **CI Integration**: Automated Python linting in CI/CD

### Go Code Quality (CLI)

- **CLI moved to separate repository**: [AI4quantum/maestro-k-cli](https://github.com/AI4quantum/maestro-k-cli)
- **staticcheck**: Detects unused code, unreachable code, and other quality issues
- **golangci-lint**: Advanced Go linting with multiple analyzers
- **go fmt**: Consistent Go code formatting
- **go vet**: Static analysis for potential bugs
- **Dependency management**: Clean and verified module dependencies
- **Race condition detection**: Thread safety validation
- **CI Integration**: Automated Go linting in CI/CD with quality gates

### Running Quality Checks

```bash
# Python quality checks
./tools/lint.sh

# Go quality checks (CLI - separate repository)
# See: https://github.com/AI4quantum/maestro-k-cli

# All quality checks
./tools/lint.sh
```

## Project Structure

```text
maestro-k-knowledge/
├── src/                     # Source code
│   ├── db/                  # Vector database implementations
│   │   ├── vector_db_base.py      # Abstract base class
│   │   ├── vector_db_weaviate.py  # Weaviate implementation
│   │   ├── vector_db_milvus.py    # Milvus implementation
│   │   └── vector_db_factory.py   # Factory function
│   ├── maestro-k_mcp/         # MCP server implementation
│   │   ├── server.py        # Main MCP server
│   │   ├── mcp_config.json  # MCP client configuration
│   │   └── README.md        # MCP server documentation
│   ├── chunking/           # Pluggable document chunking package
│   └── vector_db.py         # Main module exports
├── start.sh                 # MCP server start script
├── stop.sh                  # MCP server stop script
├── tools/                   # Development tools
│   ├── lint.sh              # Code linting and formatting
│   ├── e2e.sh               # End-to-end testing script
│   ├── test-integration.sh  # Integration tests
│   └── tail-logs.sh        # Real-time log monitoring script
├── test.sh                  # Test runner script (MCP, Integration)
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
    ├── CLI_UX_REVIEW.md     # CLI UX review and improvements
    └── PRESENTATION.md      # Project presentation
```

## Environment Variables

- `VECTOR_DB_TYPE`: Default vector database type (defaults to "weaviate")
- `OPENAI_API_KEY`: Required for OpenAI embedding models
- `MAESTRO_KNOWLEDGE_MCP_SERVER_URI`: MCP server URI for CLI tool
- `MILVUS_URI`: Milvus connection URI. **Important**: Do not use quotes around the URI value in your `.env` file (e.g., `MILVUS_URI=http://localhost:19530` instead of `MILVUS_URI="http://localhost:19530"`).
- Database-specific environment variables for Weaviate and Milvus connections

For detailed environment variable usage in CLI and MCP server, see their respective README files.

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
