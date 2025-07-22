# Examples

This directory contains practical examples demonstrating how to use the maestro-knowledge library.

## Available Examples

### `milvus_example.py` - Basic Milvus Usage
A comprehensive example showing how to:
- Set up environment variables for Milvus
- Create a vector database instance
- Write documents with vector embeddings
- List and retrieve documents
- Proper cleanup and error handling

**Run with:**
```bash
python examples/milvus_example.py
```

### `weaviate_example.py` - Basic Weaviate Usage
A comprehensive example showing how to:
- Set up environment variables for Weaviate
- Create a vector database instance
- Write documents with metadata
- List and retrieve documents
- Proper cleanup and error handling

**Run with:**
```bash
python examples/weaviate_example.py
```

**Note**: Both examples use the new import path `from src.db.vector_db_factory import create_vector_database`

## Prerequisites

Before running the examples, make sure you have:

1. **Vector Database Server**: Either Milvus or Weaviate running locally or in the cloud
2. **Dependencies**: Install the required packages
   ```bash
   pip install pymilvus  # For Milvus examples
   pip install weaviate  # For Weaviate examples
   ```

## Environment Setup

The examples use environment variables for configuration. You can set them in your shell:

### For Milvus:
```bash
export VECTOR_DB_TYPE=milvus
export MILVUS_URI=localhost:19530
# Optional: export MILVUS_TOKEN=your_token
```

### For Weaviate:
```bash
export VECTOR_DB_TYPE=weaviate
export WEAVIATE_API_KEY=your_api_key
export WEAVIATE_URL=https://your-cluster.weaviate.network
```

Or create a `.env` file in the project root (remember to add `.env` to `.gitignore`):

```bash
# Choose one database type
VECTOR_DB_TYPE=milvus
MILVUS_URI=localhost:19530

# OR
VECTOR_DB_TYPE=weaviate
WEAVIATE_API_KEY=your_api_key
WEAVIATE_URL=https://your-cluster.weaviate.network
```

## Troubleshooting

If you encounter issues:

1. **Import Errors**: Make sure you're running from the project root directory
2. **Connection Errors**: 
   - For Milvus: Verify your Milvus server is running and accessible
   - For Weaviate: Verify your Weaviate cluster is running and your API key is valid
3. **Missing Dependencies**: Install required packages with `pip install pymilvus` or `pip install weaviate`
4. **Environment Variables**: Check that your environment variables are set correctly for your chosen database 