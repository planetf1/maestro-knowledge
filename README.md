# maestro-knowledge

A way to configure, ingest, and query knowledge via an AI-native database (e.g., vector database)

## Overview

Maestro Knowledge provides a unified vector database abstraction layer that supports multiple vector database backends. It offers a clean, consistent API for storing and retrieving vector embeddings, making it easy to switch between different vector database implementations without changing your application code.

## Features

- **Unified Vector Database Interface**: Abstract base class that defines a consistent API for vector operations
- **Multiple Backend Support**: Concrete implementations for popular vector databases
- **Factory Pattern**: Easy creation of vector database instances with automatic backend selection
- **Environment-based Configuration**: Support for environment variables to configure database connections
- **Comprehensive Testing**: Full test suite with proper handling of optional dependencies

## Supported Vector Databases

### Milvus (Recommended)
- **Implementation**: `MilvusVectorDatabase`
- **Features**:
  - High-performance vector database
  - Scalable architecture
  - Advanced similarity search
  - Support for various distance metrics
  - Production-ready with enterprise features
- **Requirements**: `pymilvus` Python package
- **Environment Variables**:
  - `MILVUS_HOST`: Milvus server host (default: localhost)
  - `MILVUS_PORT`: Milvus server port (default: 19530)

### Weaviate
- **Implementation**: `WeaviateVectorDatabase`
- **Features**: 
  - Cloud-native vector database
  - Automatic schema management
  - Built-in vectorization
  - Query agents support
- **Requirements**: `weaviate` Python package
- **Environment Variables**:
  - `WEAVIATE_API_KEY`: Your Weaviate API key
  - `WEAVIATE_URL`: Your Weaviate cluster URL

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd maestro-knowledge

# Install dependencies (optional - for specific backends)
pip install pymilvus  # For Milvus support (recommended)
pip install weaviate  # For Weaviate support
```

### Run the Example

```bash
# Run the comprehensive example
python examples/example.py
```

### Basic Usage

```python
from src.vector_db_factory import create_vector_database

# Create a vector database instance (automatically selects backend)
db = create_vector_database("milvus", "MyCollection")

# Set up the collection
db.setup()

# Write documents with vectors
documents = [
    {
        "url": "https://example.com/doc1",
        "text": "Document content here",
        "metadata": {"type": "webpage", "author": "John Doe"},
        "vector": [0.1, 0.2, 0.3, ...]  # Your vector embedding
    }
]
db.write_documents(documents)

# List documents
docs = db.list_documents(limit=10)

# Clean up
db.cleanup()
```

### Using Environment Variables

```bash
# Set your preferred vector database type
export VECTOR_DB_TYPE=milvus

# Set Milvus connection details (optional - defaults to localhost:19530)
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
```

```python
from src.vector_db_factory import create_vector_database

# Database type will be automatically determined from VECTOR_DB_TYPE
db = create_vector_database(collection_name="MyCollection")
```

## Project Structure

```
maestro-knowledge/
├── src/                          # Source code
│   ├── vector_db_base.py         # Abstract base class for vector databases
│   ├── vector_db_factory.py      # Factory function for creating database instances
│   ├── vector_db_milvus.py       # Milvus implementation (recommended)
│   ├── vector_db_weaviate.py     # Weaviate implementation
│   └── vector_db.py              # Main module exports
├── tests/                        # Test suite
│   ├── test_vector_db_base.py    # Tests for abstract base class
│   ├── test_vector_db_factory.py # Tests for factory function
│   ├── test_vector_db_milvus.py  # Tests for Milvus implementation
│   ├── test_vector_db_weaviate.py # Tests for Weaviate implementation
│   └── test_vector_db.py         # Main test module
├── examples/                     # Usage examples
│   ├── README.md                 # Examples documentation
│   └── example.py                # Basic Milvus usage example
├── .github/                      # GitHub configuration
│   └── workflows/                # GitHub Actions workflows
│       └── ci.yml                # Continuous Integration workflow
├── README.md                     # This file
├── pyproject.toml               # Project configuration
├── .gitignore                   # Git ignore rules
└── tests.sh                     # Test runner script
```

## Architecture

### Core Components

- **`VectorDatabase`** (Abstract Base Class): Defines the interface for all vector database implementations
- **`MilvusVectorDatabase`**: Concrete implementation for Milvus (recommended)
- **`WeaviateVectorDatabase`**: Concrete implementation for Weaviate
- **`create_vector_database()`**: Factory function for creating database instances

### Key Methods

All vector database implementations provide these core methods:

- `setup()`: Initialize the collection/schema
- `write_documents(documents)`: Store documents with their vectors
- `list_documents(limit, offset)`: Retrieve documents from the database
- `cleanup()`: Clean up resources
- `db_type`: Property that returns the database type

## Testing

### Local Testing

Run the test suite to verify everything works:

```bash
./tests.sh
```

The test suite includes:
- Unit tests for the abstract base class
- Factory function tests
- Backend-specific tests (skipped if dependencies are not available)
- Proper handling of optional dependencies

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline includes:

- **Multi-Python Testing**: Tests run on Python 3.11, 3.12, and 3.13
- **Dependency Testing**: Separate job with all optional dependencies installed
- **Code Quality**: Linting with Ruff for code style and formatting
- **Security Checks**: Bandit and Safety for security vulnerability scanning
- **Artifact Upload**: Test results and security reports are preserved as artifacts

The CI runs automatically on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop` branches

View the latest CI status: [![CI](https://github.com/AI4quantum/maestro-knowledge/actions/workflows/ci.yml/badge.svg)](https://github.com/AI4quantum/maestro-knowledge/actions/workflows/ci.yml)

> **Note**: The CI badge will appear after the first successful workflow run on GitHub.

### Code Quality

This project maintains high code quality standards:

- **Linting**: Uses Ruff for fast Python linting and import sorting
- **Formatting**: Automatic code formatting with Ruff
- **Type Hints**: Full type annotation support
- **Documentation**: Comprehensive docstrings and README
- **Test Coverage**: Extensive test suite with proper dependency handling

To run code quality checks locally:

```bash
# Install development dependencies
uv pip install ruff bandit safety

# Run linting
uv run ruff check src/ tests/ examples/

# Run formatting check
uv run ruff format --check src/ tests/ examples/

# Auto-fix formatting issues
uv run ruff format src/ tests/ examples/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
