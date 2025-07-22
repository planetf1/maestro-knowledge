# Maestro Vector Database MCP Server

This MCP (Model Context Protocol) server exposes the Maestro Vector Database functionality to AI agents through a standardized interface with flexible embedding strategies.

## Features

The MCP server provides the following tools for vector database operations:

### Database Management
- **create_vector_database**: Create a new vector database instance (Weaviate or Milvus)
- **setup_database**: Set up the current vector database and create collections with specified embedding
- **get_supported_embeddings**: Get list of supported embedding models for the current database
- **cleanup**: Clean up resources and close database connections
- **get_database_info**: Get information about the current vector database including supported embeddings

### Document Operations
- **write_document**: Write a single document to the vector database with specified embedding strategy
- **write_documents**: Write multiple documents to the vector database with specified embedding strategy
- **list_documents**: List documents from the vector database
- **count_documents**: Get the current count of documents in the collection

### Document Management
- **delete_document**: Delete a single document by ID
- **delete_documents**: Delete multiple documents by IDs
- **delete_collection**: Delete an entire collection from the database

## Embedding Strategies

The MCP server supports flexible embedding strategies for both vector databases:

### Supported Embedding Models

#### Weaviate
- `default`: Uses Weaviate's built-in text2vec-weaviate vectorizer
- `text2vec-weaviate`: Weaviate's built-in text vectorizer
- `text2vec-openai`: OpenAI's embedding models (requires API key)
- `text2vec-cohere`: Cohere's embedding models
- `text2vec-huggingface`: Hugging Face models
- `text-embedding-ada-002`: OpenAI's Ada-002 model
- `text-embedding-3-small`: OpenAI's text-embedding-3-small model
- `text-embedding-3-large`: OpenAI's text-embedding-3-large model

#### Milvus
- `default`: Uses pre-computed vectors if available, otherwise text-embedding-ada-002
- `text-embedding-ada-002`: OpenAI's Ada-002 embedding model
- `text-embedding-3-small`: OpenAI's text-embedding-3-small model
- `text-embedding-3-large`: OpenAI's text-embedding-3-large model

## Usage

### Running the Server

```bash
# From the project root
./start.sh

# Stop the server
./stop.sh

# Check server status
./stop.sh status

# Restart the server
./stop.sh restart
```

### Configuration

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

### Example Usage

Here's how an AI agent might interact with the vector database:

1. **Create a vector database**:
   ```json
   {
     "name": "create_vector_database",
     "arguments": {
       "db_type": "weaviate",
       "collection_name": "MyDocuments"
     }
   }
   ```

2. **Get supported embeddings**:
   ```json
   {
     "name": "get_supported_embeddings",
     "arguments": {}
   }
   ```

3. **Set up the database with specific embedding**:
   ```json
   {
     "name": "setup_database",
     "arguments": {
       "embedding": "text-embedding-ada-002"
     }
   }
   ```

4. **Write a document with default embedding**:
   ```json
   {
     "name": "write_document",
     "arguments": {
       "url": "https://example.com/doc1",
       "text": "This is the content of the document",
       "metadata": {
         "author": "John Doe",
         "date": "2024-01-01"
       },
       "embedding": "default"
     }
   }
   ```

5. **Write a document with pre-computed vector (Milvus)**:
   ```json
   {
     "name": "write_document",
     "arguments": {
       "url": "https://example.com/doc2",
       "text": "This document has a pre-computed vector",
       "metadata": {
         "author": "Jane Smith",
         "date": "2024-01-02"
       },
       "vector": [0.1, 0.2, 0.3, ...],
       "embedding": "default"
     }
   }
   ```

6. **Write multiple documents with specific embedding**:
   ```json
   {
     "name": "write_documents",
     "arguments": {
       "documents": [
         {
           "url": "https://example.com/doc3",
           "text": "First document",
           "metadata": {"category": "tech"}
         },
         {
           "url": "https://example.com/doc4",
           "text": "Second document",
           "metadata": {"category": "science"}
         }
       ],
       "embedding": "text-embedding-3-small"
     }
   }
   ```

7. **List documents**:
   ```json
   {
     "name": "list_documents",
     "arguments": {
       "limit": 10,
       "offset": 0
     }
   }
   ```

8. **Get database information**:
   ```json
   {
     "name": "get_database_info",
     "arguments": {}
   }
   ```

## Environment Variables

The server respects the following environment variables:

- `VECTOR_DB_TYPE`: Default vector database type (defaults to "weaviate")
- `OPENAI_API_KEY`: Required for OpenAI embedding models
- Database-specific environment variables for Weaviate and Milvus connections

## Error Handling

The server provides detailed error messages for common issues:
- Missing database initialization
- Invalid database types
- Unsupported embedding models
- Missing API keys for embedding services
- Connection errors
- Document operation failures

## Dependencies

- `mcp`: Model Context Protocol library
- All existing Maestro Vector Database dependencies (Weaviate, Milvus, etc.)
- `openai`: Required for OpenAI embedding models 