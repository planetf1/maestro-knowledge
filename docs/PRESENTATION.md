---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# Maestro Knowledge
## Modular Vector Database Interface

**A unified API for multiple vector database backends**

---

# What is Maestro Knowledge?

- **Multi-backend vector database interface**
- **Unified API** for Weaviate and Milvus
- **Flexible embedding strategies** 
- **MCP Server** for AI agent integration
- **CLI tool** for easy management
- **Document management** with rich metadata

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
- **MCP Server** integration
- **Model Context Protocol** support
- **CLI tool** for easy management

---

# Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tool      │    │   MCP Server    │    │   Python API    │
│   (Go)          │    │   (FastMCP)     │    │   (Factory)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Vector DB      │
                    │  Interface      │
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

## Commands
```bash
# List databases
maestro-k list vector-db

# Create database from YAML
maestro-k create vector-db config.yaml

# Delete database
maestro-k delete vector-db my-db

# Validate YAML config
maestro-k validate config.yaml
```

## Features
- **YAML configuration** support
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
  uri: localhost:19530
  collection_name: documents
  embedding: text-embedding-3-small
  mode: local
```

---

# MCP Server Integration

## Model Context Protocol
- **FastMCP** implementation
- **HTTP server** mode (port 8030)
- **Tool-based** interface
- **AI agent** ready

## Available Tools
- `create_vector_database_tool`
- `setup_database_tool` 
- `list_databases_tool`
- `delete_vector_database_tool`

---

# Testing & Quality

## Test Coverage
- **Python unit tests** - 70+ tests
- **Go CLI tests** - 47 tests
- **Integration tests** - End-to-end workflows
- **Schema validation** - YAML validation

## Quality Tools
- **Ruff** - Python linting
- **Go fmt** - Go formatting
- **Pytest** - Python testing
- **GitHub Actions** - CI/CD

---

# Project Structure

```
maestro-knowledge/
├── src/                    # Python source
│   ├── db/                # Database backends
│   ├── maestro_mcp/       # MCP server
│   └── vector_db.py       # Factory interface
├── cli/                   # Go CLI tool
│   ├── src/              # Go source
│   └── tests/            # CLI tests
├── tests/                # Python tests
├── examples/             # Usage examples
├── schemas/              # YAML schemas
└── docs/                 # Documentation
```

---

# Use Cases

## 🤖 AI Agent Integration
- **RAG systems** with multiple backends
- **Document processing** pipelines
- **Knowledge bases** for AI assistants

## 📚 Document Management
- **Content indexing** and search
- **Metadata-rich** document storage
- **Multi-modal** content support

## 🔄 Backend Flexibility
- **Cloud-native** (Weaviate)
- **Self-hosted** (Milvus)
- **Easy migration** between backends

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
./maestro-k --help
```

---

# Future Roadmap

## 🚀 Planned Features
- **Additional backends** (Pinecone, Qdrant)
- **Advanced querying** capabilities
- **Performance optimizations**
- **Enhanced CLI** features

## 🔧 Improvements
- **Better error handling**
- **More embedding models**
- **Advanced metadata** support
- **Distributed** deployments

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
```

## Guidelines
- **Type hints** for Python
- **Error handling** for Go
- **Comprehensive tests**
- **Documentation** updates

---

# Thank You!

## Questions & Discussion

**GitHub**: [Repository URL]
**Documentation**: See `README.md` and `docs/`
**Examples**: Check `examples/` directory

---

# Demo Time!

## Live Examples
- **Python API** usage
- **CLI tool** commands
- **MCP server** integration
- **YAML configuration**

*Let's see it in action!* 