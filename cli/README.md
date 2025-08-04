# Maestro Knowledge CLI

A command-line interface for interacting with the Maestro Knowledge MCP server with support for YAML configuration and environment variable substitution.

## Features

- **List vector databases**: List all available vector database instances
- **List embeddings**: List supported embeddings for a specific vector database
- **List collections**: List all collections in a specific vector database
- **List documents**: List documents in a specific collection of a vector database
- **Query documents**: Query documents using natural language with semantic search
- **Create vector databases**: Create vector databases from YAML configuration files
- **Delete vector databases**: Delete vector databases by name
- **Validate configurations**: Validate YAML configuration files
- **Environment variable substitution**: Replace `{{ENV_VAR_NAME}}` placeholders in YAML files
- **Environment variable support**: Configure MCP server URI via environment variables
- **Command-line flag override**: Override MCP server URI via command-line flags
- **Dry-run mode**: Test commands without making actual changes
- **Verbose output**: Get detailed information about operations
- **Silent mode**: Suppress success messages

## Installation

### Prerequisites

- Go 1.21 or later
- Access to a running Maestro Knowledge MCP server

### Building

```bash
cd cli
go build -o maestro-k src/*.go
```

## Usage

### Basic Commands

```bash
# Show help
./maestro-k --help

# Show version
./maestro-k --version

# List vector databases (using plural form)
./maestro-k list vector-dbs

# List vector databases with verbose output
./maestro-k list vector-dbs --verbose

# List embeddings for a specific vector database
./maestro-k list embeddings my-database

# List embeddings with verbose output
./maestro-k list embeddings my-database --verbose

# List embeddings using short alias
./maestro-k list embeds my-database

# List collections for a specific vector database
./maestro-k list collections my-database

# List collections with verbose output
./maestro-k list collections my-database --verbose

# List collections using short alias
./maestro-k list cols my-database

# List documents in a specific collection
./maestro-k list documents my-database my-collection

# List documents with verbose output
./maestro-k list documents my-database my-collection --verbose

# List documents using short alias
./maestro-k list docs my-database my-collection

# Query documents using natural language
./maestro-k query my-database "What is the main topic of the documents?"
./maestro-k query vdb my-database "Find information about API endpoints" --doc-limit 10

# Create vector database from YAML file
./maestro-k create vector-db config.yaml

# Create vector database with environment variable substitution
./maestro-k create vector-db config.yaml --verbose

# Delete vector database
./maestro-k delete vector-db my-database

# Validate YAML configuration
./maestro-k validate config.yaml
```

### MCP Server Configuration

The CLI can connect to an MCP server using several methods:

#### 1. Environment Variable (Recommended)

Set the `MAESTRO_KNOWLEDGE_MCP_SERVER_URI` environment variable:

```bash
export MAESTRO_KNOWLEDGE_MCP_SERVER_URI="http://localhost:8030"
./maestro-k list vector-dbs
```

#### 2. .env File

Create a `.env` file in the current directory with your configuration:

```bash
# MCP Server configuration
MAESTRO_KNOWLEDGE_MCP_SERVER_URI=http://localhost:8030

# Weaviate configuration (for Weaviate backend)
WEAVIATE_API_KEY=your-weaviate-api-key
WEAVIATE_URL=https://your-weaviate-cluster.weaviate.network

# OpenAI configuration (for OpenAI embeddings)
OPENAI_API_KEY=your-openai-api-key
```

The CLI will automatically load the `.env` file if it exists in the current directory.

#### 3. Command-line Flag

Override the MCP server URI via command-line flag:

```bash
./maestro-k list vector-dbs --mcp-server-uri="http://localhost:8030"
```

**Priority order**: Command-line flag > Environment variable > .env file > Default (http://localhost:8030)

**Supported Environment Variables**:
- `MAESTRO_KNOWLEDGE_MCP_SERVER_URI`: MCP server URI
- `WEAVIATE_API_KEY`: Weaviate API key for Weaviate backend
- `WEAVIATE_URL`: Weaviate cluster URL
- `OPENAI_API_KEY`: OpenAI API key for embeddings

### Environment Variable Substitution in YAML Files

The CLI supports environment variable substitution in YAML files using the `{{ENV_VAR_NAME}}` syntax. This allows you to use environment variables directly in your configuration files:

```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: my-weaviate-db
spec:
  type: weaviate
  uri: {{WEAVIATE_URL}}
  collection_name: my_collection
  embedding: text-embedding-3-small
  mode: remote
```

When you run `./maestro-k create vector-db config.yaml`, the CLI will:
1. Load environment variables from `.env` file (if present)
2. Replace `{{WEAVIATE_URL}}` with the actual value from the environment
3. Process the YAML file with the substituted values

**Features**:
- **Automatic substitution**: All `{{ENV_VAR_NAME}}` placeholders are replaced before YAML parsing
- **Error handling**: Clear error messages if required environment variables are missing
- **Verbose logging**: Shows which environment variables are being substituted (when using `--verbose`)
- **Validation**: Ensures all required environment variables are set before processing

#### URL Format Flexibility

The CLI automatically normalizes URLs to ensure they have the correct protocol prefix:

- **Hostname only**: `localhost` → `http://localhost:8030`
- **Hostname with port**: `localhost:8030` → `http://localhost:8030`
- **Full URL**: `http://localhost:8030` → `http://localhost:8030` (unchanged)
- **HTTPS URL**: `https://example.com:9000` → `https://example.com:9000` (unchanged)

This makes it easy to specify server addresses in any format:
```bash
# All of these work the same way:
./maestro-k list vector-dbs --mcp-server-uri="localhost:8030"
./maestro-k list vector-dbs --mcp-server-uri="http://localhost:8030"
./maestro-k list vector-dbs --mcp-server-uri="https://example.com:9000"
```

### Global Flags

- `--verbose`: Show detailed output
- `--silent`: Suppress success messages
- `--dry-run`: Test commands without making changes
- `--mcp-server-uri`: Override MCP server URI
- `--help`: Show help information
- `--version`: Show version information

### List Command

The `list` command displays information about vector databases, embeddings, collections, or documents:

```bash
# List all vector databases
./maestro-k list vector-dbs

# List with verbose output
./maestro-k list vector-dbs --verbose

# Test the command without connecting to server
./maestro-k list vector-dbs --dry-run

# List embeddings for a specific vector database
./maestro-k list embeddings my-database

# List embeddings with verbose output
./maestro-k list embeddings my-database --verbose

# List embeddings using short alias
./maestro-k list embeds my-database

# Test embeddings command without connecting to server
./maestro-k list embeddings my-database --dry-run

# List collections for a specific vector database
./maestro-k list collections my-database

# List collections with verbose output
./maestro-k list collections my-database --verbose

# List collections using short alias
./maestro-k list cols my-database

# Test collections command without connecting to server
./maestro-k list collections my-database --dry-run

# List documents in a specific collection
./maestro-k list documents my-database my-collection

# List documents with verbose output
./maestro-k list documents my-database my-collection --verbose

# List documents using short alias
./maestro-k list docs my-database my-collection

# Test documents command without connecting to server
./maestro-k list documents my-database my-collection --dry-run
```

#### Output Format

**Vector Databases**: When databases are found, the output shows:
- Database name and type
- Collection name
- Document count

Example:
```
Found 2 vector database(s):

1. project_a_db (weaviate)
   Collection: ProjectADocuments
   Documents: 15

2. project_b_db (milvus)
   Collection: ProjectBDocuments
   Documents: 8
```

**Embeddings**: When listing embeddings for a vector database, the output shows:
- Supported embedding models for the specific database type

Example:
```
Supported embeddings for weaviate vector database 'my-database': [
  "default",
  "text2vec-weaviate",
  "text2vec-openai",
  "text2vec-cohere",
  "text2vec-huggingface",
  "text-embedding-ada-002",
  "text-embedding-3-small",
  "text-embedding-3-large"
]
```

**Collections**: When listing collections for a vector database, the output shows:
- All collections available in the vector database

Example:
```
Collections in vector database 'my-database': [
  "Collection1",
  "Collection2",
  "MaestroDocs"
]
```

**Documents**: When listing documents in a collection, the output shows:
- All documents in the specified collection with their properties

Example:
```
Found 3 documents in collection 'my-collection' of vector database 'my-database': [
  {
    "id": "doc1",
    "url": "https://example.com/doc1",
    "text": "Document content...",
    "metadata": {
      "source": "web",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  },
  {
    "id": "doc2",
    "url": "https://example.com/doc2",
    "text": "Another document...",
    "metadata": {
      "source": "file",
      "timestamp": "2024-01-02T00:00:00Z"
    }
  }
]
```

### Create Command

The `create` command creates vector databases from YAML configuration files:

```bash
# Create vector database from YAML file
./maestro-k create vector-db config.yaml

# Create with verbose output
./maestro-k create vector-db config.yaml --verbose

# Create with dry-run mode
./maestro-k create vector-db config.yaml --dry-run

# Override configuration values
./maestro-k create vector-db config.yaml --type=weaviate --uri=localhost:8080
```

**Supported Override Flags**:
- `--type`: Override database type (milvus, weaviate)
- `--uri`: Override connection URI
- `--collection-name`: Override collection name
- `--embedding`: Override embedding model
- `--mode`: Override deployment mode (local, remote)

#### Create Collection Command

The `create` command can also create collections in existing vector databases:

```bash
# Create collection in vector database
./maestro-k create collection my-database my-collection

# Create collection with verbose output
./maestro-k create collection my-database my-collection --verbose

# Create collection using short aliases
./maestro-k create col my-database my-collection
./maestro-k create vdb-col my-database my-collection

# Create collection with dry-run mode
./maestro-k create collection my-database my-collection --dry-run
```

#### Create Document Command

The `create` command can also create documents in collections:

```bash
# Create document from file
./maestro-k create document my-database my-collection my-doc --file-name=document.txt

# Create document with specific embedding
./maestro-k create document my-database my-collection my-doc --file-name=document.txt --embed=text-embedding-3-small

# Create document using short aliases
./maestro-k create doc my-database my-collection my-doc --file-name=document.txt
./maestro-k create vdb-doc my-database my-collection my-doc --file-name=document.txt

# Create document with dry-run mode
./maestro-k create document my-database my-collection my-doc --file-name=document.txt --dry-run
```

### Write Command

The `write` command is an alias for creating documents:

```bash
# Write document from file
./maestro-k write document my-database my-collection my-doc --file-name=document.txt

# Write document with specific embedding
./maestro-k write document my-database my-collection my-doc --file-name=document.txt --embed=text-embedding-3-small

# Write document using short aliases
./maestro-k write doc my-database my-collection my-doc --file-name=document.txt
./maestro-k write vdb-doc my-database my-collection my-doc --file-name=document.txt

# Write document with dry-run mode
./maestro-k write document my-database my-collection my-doc --file-name=document.txt --dry-run
```

### Delete Command

The `delete` command deletes vector databases, collections, or documents:

```bash
# Delete vector database
./maestro-k delete vector-db my-database

# Delete with verbose output
./maestro-k delete vector-db my-database --verbose

# Delete with dry-run mode
./maestro-k delete vector-db my-database --dry-run

# Delete using short aliases
./maestro-k delete vdb my-database
./maestro-k del vector-db my-database
./maestro-k del vdb my-database
```

#### Delete Collection Command

```bash
# Delete collection from vector database
./maestro-k delete collection my-database my-collection

# Delete collection with verbose output
./maestro-k delete collection my-database my-collection --verbose

# Delete collection using short aliases
./maestro-k delete col my-database my-collection
./maestro-k delete vdb-col my-database my-collection
./maestro-k del collection my-database my-collection
./maestro-k del col my-database my-collection

# Delete collection with dry-run mode
./maestro-k delete collection my-database my-collection --dry-run
```

#### Delete Document Command

```bash
# Delete document from collection
./maestro-k delete document my-database my-collection my-document

# Delete document with verbose output
./maestro-k delete document my-database my-collection my-document --verbose

# Delete document using short aliases
./maestro-k delete doc my-database my-collection my-document
./maestro-k delete vdb-doc my-database my-collection my-document
./maestro-k del document my-database my-collection my-document
./maestro-k del doc my-database my-collection my-document

# Delete document with dry-run mode
./maestro-k delete document my-database my-collection my-document --dry-run
```

### Query Command

The `query` command allows you to search documents using natural language queries with semantic search:

```bash
# Query documents using natural language
./maestro-k query my-database "What is the main topic of the documents?"

# Query with specific document limit
./maestro-k query my-database "Find information about API endpoints" --doc-limit 10

# Query using vdb subcommand
./maestro-k query vdb my-database "What are the key features mentioned?"

# Query with collection name specification
./maestro-k query my-database "Search for technical documentation" --collection-name my-collection

# Query with dry-run mode
./maestro-k query my-database "Test query" --dry-run

# Query with verbose output
./maestro-k query my-database "Complex search query" --verbose
```

#### Query Command Features

- **Natural Language Queries**: Use plain English to search through your documents
- **Semantic Search**: Finds relevant documents based on meaning, not just keywords
- **Document Limit Control**: Control how many documents to consider with `--doc-limit`
- **Collection Targeting**: Optionally specify which collection to search in
- **Dry-run Mode**: Test queries without actually executing them
- **Verbose Output**: Get detailed information about the query process

#### Query Command Flags

- `--doc-limit, -d`: Maximum number of documents to consider (default: 5)
- `--collection-name, -c`: Specific collection to search in (optional)
- `--dry-run`: Test the command without making changes
- `--verbose`: Show detailed output
- `--silent`: Suppress success messages

#### Query Examples

```bash
# Basic query
./maestro-k query my-database "What is machine learning?"

# Query with higher document limit
./maestro-k query my-database "Find all API documentation" --doc-limit 20

# Query specific collection
./maestro-k query my-database "Search for user guides" --collection-name documentation

# Query with vdb subcommand
./maestro-k query vdb my-database "What are the system requirements?"

# Test query without execution
./maestro-k query my-database "Test query" --dry-run
```

### Retrieve/Get Commands

The `retrieve` and `get` commands retrieve information about collections and documents:

```bash
# Retrieve collection information (uses default collection if not specified)
./maestro-k retrieve collection my-database

# Retrieve specific collection information
./maestro-k retrieve collection my-database my-collection

# Retrieve using short aliases
./maestro-k retrieve col my-database
./maestro-k retrieve vdb-col my-database my-collection

# Get collection information (alternative command)
./maestro-k get collection my-database
./maestro-k get col my-database my-collection

# Retrieve with verbose output
./maestro-k retrieve collection my-database --verbose

# Retrieve with dry-run mode
./maestro-k retrieve collection my-database --dry-run
```

#### Retrieve Document Command

```bash
# Retrieve specific document from collection
./maestro-k retrieve document my-database my-collection my-document

# Retrieve document using short aliases
./maestro-k retrieve doc my-database my-collection my-document
./maestro-k retrieve vdb-doc my-database my-collection my-document

# Get document information (alternative command)
./maestro-k get document my-database my-collection my-document
./maestro-k get doc my-database my-collection my-document
./maestro-k get vdb-doc my-database my-collection my-document

# Retrieve document with verbose output
./maestro-k retrieve document my-database my-collection my-document --verbose

# Retrieve document with dry-run mode
./maestro-k retrieve document my-database my-collection my-document --dry-run
```

**Collection Information Output**: When retrieving collection information, the output shows:
- Collection name
- Document count
- Database type
- Embedding information
- Additional metadata

Example:
```json
Collection information for 'my-collection' in vector database 'my-database': {
  "name": "my-collection",
  "document_count": 15,
  "db_type": "weaviate",
  "embedding": "text2vec-weaviate",
  "metadata": {
    "description": "My test collection",
    "vectorizer": "text2vec-weaviate",
    "properties_count": 4,
    "module_config": null
  }
}
```

**Document Information Output**: When retrieving document information, the output shows:
- Document ID
- Document URL
- Document text content
- Document metadata including doc_name and collection_name

Example:
```json
Document 'my-document' from collection 'my-collection' in vector database 'my-database': {
  "id": "doc_123",
  "url": "https://example.com/my-document",
  "text": "This is the content of the document...",
  "metadata": {
    "doc_name": "my-document",
    "collection_name": "my-collection",
    "source": "web",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Validate Command

The `validate` command validates YAML configuration files:

```bash
# Validate YAML configuration
./maestro-k validate config.yaml

# Validate with verbose output
./maestro-k validate config.yaml --verbose
```

## Examples

### Complete Workflow

1. **Start the MCP server**:
```bash
   cd /path/to/maestro-knowledge
   ./start.sh --http
   ```

2. **List databases**:
   ```bash
   cd cli
   ./maestro-k list vector-dbs --mcp-server-uri="http://localhost:8030"
   ```

3. **List with verbose output**:
   ```bash
   ./maestro-k list vector-dbs --mcp-server-uri="http://localhost:8030" --verbose
   ```

4. **List embeddings for a database**:
   ```bash
   ./maestro-k list embeddings my-database --mcp-server-uri="http://localhost:8030"
   ```

5. **List collections for a database**:
   ```bash
   ./maestro-k list collections my-database --mcp-server-uri="http://localhost:8030"
   ```

6. **List documents in a collection**:
   ```bash
   ./maestro-k list documents my-database my-collection --mcp-server-uri="http://localhost:8030"
   ```

7. **Query documents using natural language**:
   ```bash
   ./maestro-k query my-database "What is the main topic?" --mcp-server-uri="http://localhost:8030"
   ./maestro-k query vdb my-database "Find API documentation" --doc-limit 10 --mcp-server-uri="http://localhost:8030"
   ```

8. **Retrieve collection information**:
   ```bash
   ./maestro-k retrieve collection my-database --mcp-server-uri="http://localhost:8030"
   ```

9. **Create a vector database from YAML**:
   ```bash
   ./maestro-k create vector-db config.yaml --mcp-server-uri="http://localhost:8030"
   ```

10. **Delete a vector database**:
    ```bash
    ./maestro-k delete vector-db my-database --mcp-server-uri="http://localhost:8030"
    ```

### Examples

See the [examples/](examples/) directory for usage examples:

- [example_usage.sh](examples/example_usage.sh) - Comprehensive CLI usage demonstration with MCP server

### Testing

Run the integration test suite:

```bash
./test_integration.sh
```

This will test:
- CLI help functionality
- Dry-run mode
- Verbose mode
- Environment variable support
- Command-line flag override
- .env file support
- YAML validation
- Environment variable substitution
- Query functionality
- Query command validation

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check if the MCP server is running**:
   ```bash
   cd /path/to/maestro-knowledge
   ./stop.sh status
   ```

2. **Verify the server URI**:
```bash
   ./maestro-k list vector-dbs --mcp-server-uri="http://localhost:8030" --verbose
   ```

3. **Check server logs**:
   ```bash
   tail -f /path/to/maestro-knowledge/mcp_server.log
   ```

### Common Issues

- **"connection refused"**: MCP server is not running or wrong port
- **"HTTP error 404"**: Wrong endpoint or server not configured correctly
- **"failed to parse database list"**: Server response format issue
- **"missing required environment variables"**: Environment variable substitution failed
- **"vector database already exists"**: Database with that name already exists
- **"vector database does not exist"**: Database with that name doesn't exist

## Development

### Project Structure

```
cli/
├── src/
│   ├── main.go          # Main CLI entry point
│   ├── list.go          # List command implementation
│   ├── create.go        # Create command implementation
│   ├── delete.go        # Delete command implementation
│   ├── query.go         # Query command implementation
│   ├── validate.go      # Validate command implementation
│   └── mcp_client.go    # MCP server client
├── examples/
│   ├── example_usage.sh # Comprehensive CLI usage examples
│   └── README.md        # Examples documentation
├── tests/
│   ├── list_test.go     # List command tests
│   ├── create_test.go   # Create command tests
│   ├── delete_test.go   # Delete command tests
│   ├── query_test.go    # Query command tests
│   ├── validate_test.go # Validate command tests
│   └── main_test.go     # Main CLI tests
├── go.mod               # Go module dependencies
├── go.sum               # Go module checksums
├── test_integration.sh  # Integration test script
└── README.md           # This file
```

### Adding New Commands

1. Create a new command file (e.g., `src/new_command.go`)
2. Define the command using Cobra
3. Add the command to `main.go`
4. Update this README

### Testing

```bash
# Run integration tests
./test_integration.sh

# Build and test manually
go build -o maestro-k src/*.go
./maestro-k --help
```

## License

Apache 2.0 License - see the main project LICENSE file for details. 