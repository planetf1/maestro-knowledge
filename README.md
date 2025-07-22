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

### Milvus
- **Implementation**: `MilvusVectorDatabase`
- **Features**:
  - High-performance vector database
  - Scalable architecture
  - Advanced similarity search
  - Support for various distance metrics
- **Requirements**: `pymilvus` Python package
- **Environment Variables**:
  - `MILVUS_HOST`: Milvus server host (default: localhost)
  - `MILVUS_PORT`: Milvus server port (default: 19530)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd maestro-knowledge

# Install dependencies (optional - for specific backends)
pip install weaviate  # For Weaviate support
pip install pymilvus  # For Milvus support
```

### Basic Usage

```python
from src.vector_db_factory import create_vector_database

# Create a vector database instance (automatically selects backend)
db = create_vector_database("weaviate", "MyCollection")

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
export VECTOR_DB_TYPE=weaviate

# Set Weaviate credentials
export WEAVIATE_API_KEY=your_api_key
export WEAVIATE_URL=https://your-cluster.weaviate.network
```

```python
from src.vector_db_factory import create_vector_database

# Database type will be automatically determined from VECTOR_DB_TYPE
db = create_vector_database(collection_name="MyCollection")
```

## Architecture

### Core Components

- **`VectorDatabase`** (Abstract Base Class): Defines the interface for all vector database implementations
- **`WeaviateVectorDatabase`**: Concrete implementation for Weaviate
- **`MilvusVectorDatabase`**: Concrete implementation for Milvus
- **`create_vector_database()`**: Factory function for creating database instances

### Key Methods

All vector database implementations provide these core methods:

- `setup()`: Initialize the collection/schema
- `write_documents(documents)`: Store documents with their vectors
- `list_documents(limit, offset)`: Retrieve documents from the database
- `cleanup()`: Clean up resources
- `db_type`: Property that returns the database type

## Testing

Run the test suite to verify everything works:

```bash
./tests.sh
```

The test suite includes:
- Unit tests for the abstract base class
- Factory function tests
- Backend-specific tests (skipped if dependencies are not available)
- Proper handling of optional dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
