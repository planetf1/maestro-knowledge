# Examples

This directory contains practical examples demonstrating how to use the maestro-knowledge library.

## Available Examples

### `example.py` - Basic Milvus Usage
A comprehensive example showing how to:
- Set up environment variables for Milvus
- Create a vector database instance
- Write documents with vector embeddings
- List and retrieve documents
- Proper cleanup and error handling

**Run with:**
```bash
python examples/example.py
```

**Note**: The example uses the new import path `from src.db.vector_db_factory import create_vector_database`

## Prerequisites

Before running the examples, make sure you have:

1. **Milvus Server**: Either running locally or a cloud instance
2. **Dependencies**: Install the required packages
   ```bash
   pip install pymilvus  # For Milvus examples
   pip install weaviate  # For Weaviate examples (if needed)
   ```

## Environment Setup

The examples use environment variables for configuration. You can set them in your shell:

```bash
export VECTOR_DB_TYPE=milvus
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
```

Or create a `.env` file in the project root (remember to add `.env` to `.gitignore`):

```bash
VECTOR_DB_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Troubleshooting

If you encounter issues:

1. **Import Errors**: Make sure you're running from the project root directory
2. **Connection Errors**: Verify your Milvus server is running and accessible
3. **Missing Dependencies**: Install required packages with `pip install pymilvus`
4. **Environment Variables**: Check that your environment variables are set correctly 