---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# Maestro Knowledge
## Modular Vector Database Interface

**A unified API for multiple vector database backends with multi-database support**

---

# What is Maestro Knowledge?

- **Multi-backend vector database interface**
- **Unified API** for Weaviate and Milvus
- **Flexible embedding strategies** 
- **MCP Server** for AI agent integration with multi-database support
- **CLI tool** for easy management with YAML configuration
- **Document management** with rich metadata
- **Environment variable substitution** for dynamic configuration

---

# Key Features

## 🔄 Multi-backend Support
- **Weaviate** - Cloud-native vector database
- **Milvus** - Open-source vector database
- **Unified interface** - Same API across backends

## 🧠 Flexible Embeddings
- **Pre-computed vectors** support
- **Multiple embedding models** (OpenAI, Cohere, Hugging Face)
- **Automatic vectorization** when needed

## 🤖 AI Agent Ready
- **MCP Server** integration with FastMCP
- **Model Context Protocol** support
- **CLI tool** for easy management
- **Multi-database** support for complex workflows

---

# Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tool      │    │   MCP Server    │    │   Python API    │
│   (Go)          │    │   (FastMCP)     │    │   (Factory)     │
│   Plural cmds   │    │   Multi-DB      │    │   Multi-DB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Vector DB      │
                    │  Interface      │
                    │  (Multi-DB)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Weaviate      │    │     Milvus      │    │   Future DBs    │
│   Backend       │    │    Backend      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

# Supported Embedding Models

## Weaviate Backend
- `default` - text2vec-weaviate
- `text2vec-openai` - OpenAI models
- `text2vec-cohere` - Cohere models  
- `text2vec-huggingface` - Hugging Face models
- `text-embedding-3-small/large` - OpenAI embeddings

## Milvus Backend
- `default` - Pre-computed vectors or OpenAI
- `text-embedding-ada-002` - OpenAI Ada-002
- `text-embedding-3-small/large` - OpenAI embeddings

---

# Quick Start - Python API

```python
from src.vector_db import create_vector_database

# Create database
db = create_vector_database("weaviate", "MyCollection")
db.setup()

# Write documents
documents = [
    {
        "url": "https://example.com/doc1",
        "text": "Machine learning algorithms",
        "metadata": {"topic": "ML", "author": "Alice"}
    }
]
db.write_documents(documents, embedding="default")

# Query documents
docs = db.list_documents(limit=10)
print(f"Found {len(docs)} documents")
```

---

# CLI Tool - Go Implementation

## Commands (Plural Forms)
```bash
# List databases
maestro-k list vector-dbs

# List embeddings
maestro-k list embeds my-database

# List collections
maestro-k list cols my-database

# List documents
maestro-k list docs my-database my-collection

# Create database from YAML
maestro-k create vector-db config.yaml

# Delete database
maestro-k delete vector-db my-db

# Validate YAML config
maestro-k validate config.yaml
```

## Features
- **YAML configuration** support
- **Environment variable substitution** with `{{ENV_VAR_NAME}}`
- **Dry-run mode** for testing
- **Verbose/silent** output modes
- **Environment variable** support
- **MCP server** integration

---

# YAML Configuration

```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: my-milvus-db
  labels:
    app: knowledge-base
spec:
  type: milvus
  uri: {{MILVUS_URI}}
  collection_name: documents
  embedding: text-embedding-3-small
  mode: local
```

## Environment Variable Substitution
```bash
# .env file
MILVUS_URI=localhost:19530
WEAVIATE_URL=https://your-cluster.weaviate.network

# CLI automatically substitutes {{ENV_VAR_NAME}}
./maestro-k create vector-db config.yaml
```

---

# MCP Server Integration

## Model Context Protocol
- **FastMCP** implementation for better performance
- **HTTP server** mode (port 8030)
- **Tool-based** interface
- **AI agent** ready
- **Multi-database** support

## Available Tools
- `create_vector_database_tool`
- `setup_database`
- `list_databases`
- `get_supported_embeddings`
- `list_collections`
- `list_documents_in_collection`
- `write_document` / `write_documents`
- `delete_document` / `delete_documents`
- `cleanup`

---

# Multi-Database Support

## Key Benefits
- **Isolation**: Each database operates independently
- **Flexibility**: Mix different database types
- **Organization**: Use descriptive names for projects
- **Resource Management**: Clean up specific databases

## Example Workflow
```python
# Create multiple databases
create_vector_database_tool(db_name="project_a", db_type="weaviate")
create_vector_database_tool(db_name="project_b", db_type="milvus")

# List all databases
list_databases()

# Operate on specific databases
write_document(db_name="project_a", ...)
write_document(db_name="project_b", ...)
```

---

# Testing & Quality

## Test Coverage
- **Python unit tests** - 70+ tests
- **Go CLI tests** - 47 tests
- **Integration tests** - End-to-end workflows
- **Schema validation** - YAML validation
- **CLI integration tests** - Full CLI workflow testing

## Quality Tools
- **Ruff** - Python linting and formatting
- **Go fmt** - Go formatting
- **Pytest** - Python testing
- **GitHub Actions** - CI/CD

## Pre-PR Test Suite
```bash
./lint.sh && ./test.sh all && ./test-integration.sh
```
This comprehensive sequence ensures:
- Code quality and formatting
- All unit tests pass (CLI + MCP)
- Integration tests pass
- CLI tool integration works
- Multi-database functionality

---

# Project Structure

```
maestro-knowledge/
├── src/                    # Python source
│   ├── db/                # Database backends
│   ├── maestro_mcp/       # MCP server (FastMCP)
│   └── vector_db.py       # Factory interface
├── cli/                   # Go CLI tool
│   ├── src/              # Go source (plural commands)
│   ├── tests/            # CLI tests
│   └── examples/         # CLI examples
├── tests/                # Python tests
├── examples/             # Usage examples
├── schemas/              # YAML schemas
├── docs/                 # Documentation
├── start.sh              # MCP server start
├── stop.sh               # MCP server stop
├── lint.sh               # Code quality
├── test.sh               # Test runner (CLI, MCP, Integration)
└── test-integration.sh   # Integration tests
```

---

# Use Cases

## 🤖 AI Agent Integration
- **RAG systems** with multiple backends
- **Document processing** pipelines
- **Knowledge bases** for AI assistants
- **Multi-database** workflows

## 📚 Document Management
- **Content indexing** and search
- **Metadata-rich** document storage
- **Multi-modal** content support
- **Environment-based** configuration

## 🔄 Backend Flexibility
- **Cloud-native** (Weaviate)
- **Self-hosted** (Milvus)
- **Easy migration** between backends
- **Dynamic configuration** with environment variables

---

# Getting Started

## Installation
```bash
git clone <repository-url>
cd maestro-knowledge
uv sync
```

## Start MCP Server
```bash
./start.sh
```

## Use CLI
```bash
cd cli
go build -o maestro-k src/*.go
./maestro-k list vector-dbs --help
```

## Environment Setup
```bash
# Create .env file
echo "MAESTRO_KNOWLEDGE_MCP_SERVER_URI=http://localhost:8030" > .env
echo "WEAVIATE_URL=https://your-cluster.weaviate.network" >> .env
```

---

# Future Roadmap

## 🚀 Planned Features
- **Additional backends** (Pinecone, Qdrant)
- **Advanced querying** capabilities
- **Performance optimizations**
- **Enhanced CLI** features
- **Distributed** multi-database deployments

## 🔧 Improvements
- **Better error handling**
- **More embedding models**
- **Advanced metadata** support
- **Enhanced environment variable** substitution
- **Multi-region** database support

---

# Contributing

## Development Setup
```bash
# Python environment
uv sync
uv run pytest

# Go CLI
cd cli
go test ./...

# Comprehensive testing (before PR)
./lint.sh && ./test.sh all && ./test-integration.sh
```

## Guidelines
- **Type hints** for Python
- **Error handling** for Go
- **Comprehensive tests**
- **Documentation** updates
- **Pre-PR test suite** must pass
- **Integration testing** with CLI tool
- **Plural commands** for CLI list operations
- **Multi-database** testing

---

# Thank You!

## Questions & Discussion

**GitHub**: [Repository URL]
**Documentation**: See `README.md` and `docs/`
**Examples**: Check `examples/` directory

---

# Demo Time!

## Live Examples
- **Python API** usage with multi-database support
- **CLI tool** commands with plural forms
- **MCP server** integration with FastMCP
- **YAML configuration** with environment variable substitution
- **Multi-database** workflows

*Let's see it in action!* 