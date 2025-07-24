# Maestro Vector Database MCP Server

This MCP (Model Context Protocol) server exposes the Maestro Vector Database functionality to AI agents through a standardized interface with flexible embedding strategies.

## Features

The MCP server provides the following tools for vector database operations with support for multiple simultaneous databases:

### Database Management
- **create_vector_database**: Create a new vector database instance (Weaviate or Milvus) with a unique name
- **setup_database**: Set up a vector database and create collections with specified embedding
- **get_supported_embeddings**: Get list of supported embedding models for a specific database
- **cleanup**: Clean up resources and close database connections for a specific database
- **get_database_info**: Get information about a specific vector database including supported embeddings
- **list_databases**: List all available vector database instances

### Document Operations
- **write_document**: Write a single document to a specific vector database with specified embedding strategy
- **write_documents**: Write multiple documents to a specific vector database with specified embedding strategy
- **list_documents**: List documents from a specific vector database
- **count_documents**: Get the current count of documents in a specific collection

### Document Management
- **delete_document**: Delete a single document by ID from a specific database
- **delete_documents**: Delete multiple documents by IDs from a specific database
- **delete_collection**: Delete an entire collection from a specific database

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

## Multi-Database Support

The MCP server now supports managing multiple vector databases simultaneously. Each database is identified by a unique name, allowing you to:

- Create and manage multiple databases of different types (Weaviate, Milvus)
- Use different databases for different purposes or projects
- Operate on specific databases by providing the database name in tool calls
- List all available databases and their status

### Key Benefits

- **Isolation**: Each database operates independently with its own collections and documents
- **Flexibility**: Mix different database types (Weaviate and Milvus) in the same session
- **Organization**: Use descriptive names to organize databases by project or purpose
- **Resource Management**: Clean up specific databases without affecting others

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

Here's how an AI agent might interact with multiple vector databases:

1. **Create multiple vector databases**:
   ```json
   {
     "name": "create_vector_database",
     "arguments": {
       "db_name": "project_a_db",
       "db_type": "weaviate",
       "collection_name": "ProjectADocuments"
     }
   }
   ```
   ```json
   {
     "name": "create_vector_database",
     "arguments": {
       "db_name": "project_b_db",
       "db_type": "milvus",
       "collection_name": "ProjectBDocuments"
     }
   }
   ```

2. **List all available databases**:
   ```json
   {
     "name": "list_databases",
     "arguments": {}
   }
   ```

3. **Get supported embeddings for a specific database**:
   ```json
   {
     "name": "get_supported_embeddings",
     "arguments": {
       "db_name": "project_a_db"
     }
   }
   ```

4. **Set up a specific database with embedding**:
   ```json
   {
     "name": "setup_database",
     "arguments": {
       "db_name": "project_a_db",
       "embedding": "text-embedding-ada-002"
     }
   }
   ```

5. **Write documents to different databases**:
   ```json
   {
     "name": "write_document",
     "arguments": {
       "db_name": "project_a_db",
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
   ```json
   {
     "name": "write_document",
     "arguments": {
       "db_name": "project_b_db",
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

6. **Write multiple documents to a specific database**:
   ```json
   {
     "name": "write_documents",
     "arguments": {
       "db_name": "project_a_db",
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

7. **List documents from a specific database**:
   ```json
   {
     "name": "list_documents",
     "arguments": {
       "db_name": "project_a_db",
       "limit": 10,
       "offset": 0
     }
   }
   ```

8. **Get information about a specific database**:
   ```json
   {
     "name": "get_database_info",
     "arguments": {
       "db_name": "project_a_db"
     }
   }
   ```

9. **Clean up a specific database**:
   ```json
   {
     "name": "cleanup",
     "arguments": {
       "db_name": "project_a_db"
     }
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