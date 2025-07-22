# Maestro Vector Database MCP Server

This MCP (Model Context Protocol) server exposes the Maestro Vector Database functionality to AI agents through a standardized interface.

## Features

The MCP server provides the following tools for vector database operations:

### Database Management
- **create_vector_database**: Create a new vector database instance (Weaviate or Milvus)
- **setup_database**: Set up the current vector database and create collections
- **cleanup**: Clean up resources and close database connections
- **get_database_info**: Get information about the current vector database

### Document Operations
- **write_document**: Write a single document to the vector database
- **write_documents**: Write multiple documents to the vector database
- **list_documents**: List documents from the vector database
- **count_documents**: Get the current count of documents in the collection

### Document Management
- **delete_document**: Delete a single document by ID
- **delete_documents**: Delete multiple documents by IDs
- **delete_collection**: Delete an entire collection from the database

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

2. **Set up the database**:
   ```json
   {
     "name": "setup_database",
     "arguments": {}
   }
   ```

3. **Write a document**:
   ```json
   {
     "name": "write_document",
     "arguments": {
       "url": "https://example.com/doc1",
       "text": "This is the content of the document",
       "metadata": {
         "author": "John Doe",
         "date": "2024-01-01"
       }
     }
   }
   ```

4. **List documents**:
   ```json
   {
     "name": "list_documents",
     "arguments": {
       "limit": 10,
       "offset": 0
     }
   }
   ```

## Environment Variables

The server respects the following environment variables:

- `VECTOR_DB_TYPE`: Default vector database type (defaults to "weaviate")
- Database-specific environment variables for Weaviate and Milvus connections

## Error Handling

The server provides detailed error messages for common issues:
- Missing database initialization
- Invalid database types
- Connection errors
- Document operation failures

## Dependencies

- `mcp`: Model Context Protocol library
- All existing Maestro Vector Database dependencies (Weaviate, Milvus, etc.) 