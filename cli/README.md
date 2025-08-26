# Maestro Knowledge CLI

A command-line interface for interacting with the Maestro Knowledge MCP server with support for YAML configuration and environment variable substitution.

## Features

- **List vector databases**: List all available vector database instances
- **List embeddings**: List supported embeddings for a specific vector database
- **List collections**: List all collections in a specific vector database
- **List documents**: List documents in a specific collection of a vector database
- **Query documents**: Query documents using natural language with semantic search
- **Pluggable document chunking**: Configure per-collection chunking (None, Fixed with size/overlap, Sentence)
   - Discover supported strategies with `maestro-k chunking list`
- **Create vector databases**: Create vector databases from YAML configuration files
- **Delete vector databases**: Delete vector databases by name
- **Validate configurations**: Validate YAML configuration files
- **Environment variable substitution**: Replace `{{ENV_VAR_NAME}}` placeholders in YAML files
- **Environment variable support**: Configure MCP server URI via environment variables
- **Command-line flag override**: Override MCP server URI via command-line flags
- **Dry-run mode**: Test commands without making actual changes
- **Verbose output**: Get detailed information about operations
- **Silent mode**: Suppress success messages
- **Safety features**: Confirmation prompts for destructive operations with `--force` flag bypass

### Enhanced User Experience

- **Command suggestions**: Intelligent suggestions for mistyped commands with "Did you mean..." functionality
- **Command aliases**: Short aliases for common commands (e.g., `vdb` for `vectordb`, `coll` for `collection`, `doc` for `document`)
- **Contextual help**: Helpful tips and next steps shown after successful operations
- **Command examples**: Comprehensive examples for all commands and subcommands
- **Error guidance**: Helpful suggestions for common error scenarios when using `--verbose` mode
- **Interactive selection**: When resource names aren't provided, the CLI prompts for selection
- **Auto-completion**: Shell completion for commands, subcommands, flags, and resource names
- **Progress indicators**: Visual feedback for long-running operations
- **Status commands**: Quick overview of system state with `maestro-k status`

## Installation

### Prerequisites

- Go 1.21 or later
- Access to a running Maestro Knowledge MCP server

### Building

```bash
cd cli
go build -o maestro-k src/*.go

# Or use the build script
./build.sh
```

## Usage

### Basic Commands

```bash
# Show help
./maestro-k --help

# Show version
./maestro-k --version

# List vector databases
./maestro-k vectordb list

# List vector databases with verbose output
./maestro-k vectordb list --verbose

# List collections for a specific vector database
./maestro-k collection list --vdb=my-database

# List collections with verbose output
./maestro-k collection list --vdb=my-database --verbose

# List embeddings for a specific vector database
./maestro-k embedding list --vdb=my-database

# List embeddings with verbose output
./maestro-k embedding list --vdb=my-database --verbose

# List documents in a specific collection
./maestro-k document list --vdb=my-database --collection=my-collection

# List documents with verbose output
./maestro-k document list --vdb=my-database --collection=my-collection --verbose

# Query documents using natural language
# Tip: pass --collection to avoid an interactive prompt
./maestro-k query "What is the main topic of the documents?" --vdb=my-database
./maestro-k query "Find information about API endpoints" --vdb=my-database --collection=my-collection --doc-limit 10

# Create vector database from YAML file
./maestro-k vectordb create config.yaml

# Create vector database with environment variable substitution
./maestro-k vectordb create config.yaml --verbose

# Delete vector database (with confirmation prompt)
./maestro-k vectordb delete my-database

# Delete vector database without confirmation
./maestro-k vectordb delete my-database --force

# Validate YAML configuration
./maestro-k validate config.yaml

# Create collection with chunking
./maestro-k create collection my-database my-collection \
   --embedding=text-embedding-3-small \
   --chunking-strategy=Sentence \
   --chunk-size=512 \
   --chunk-overlap=32

# List supported chunking strategies
./maestro-k chunking list
```

### Enhanced UX Features

#### Interactive Selection Examples

```bash
# The CLI will prompt you to select a vector database if not specified
./maestro-k collection list

# The CLI will prompt you to select a collection if not specified
./maestro-k document list --vdb=my-database

# The CLI will prompt you to select a document if not specified
./maestro-k document delete --vdb=my-database --collection=my-collection

# Search and query also prompt for a collection when --collection is omitted
./maestro-k search "example" --vdb=my-database
./maestro-k query "example" --vdb=my-database

# Note: Prompts are skipped in non-interactive contexts and with --dry-run; pass --collection to avoid prompting
```

#### Auto-completion Setup

**Bash:**
```bash
# Generate completion script
./maestro-k completion bash > ~/.local/share/bash-completion/completions/maestro-k

# Or add to your .bashrc
echo 'source <(./maestro-k completion bash)' >> ~/.bashrc
```

**Zsh:**
```bash
# Generate completion script
./maestro-k completion zsh > ~/.zsh/completions/_maestro-k

# Or add to your .zshrc
echo 'source <(./maestro-k completion zsh)' >> ~/.zshrc
```

**Fish:**
```bash
# Generate completion script
./maestro-k completion fish > ~/.config/fish/completions/maestro-k.fish
```

**PowerShell:**
```powershell
# Generate completion script
./maestro-k completion powershell | Out-String | Invoke-Expression
```

#### Progress Indicators

Progress indicators are automatically shown for long-running operations:

```bash
# Document creation with progress indicator
./maestro-k document create --name=my-doc --file=document.txt --vdb=my-database --collection=my-collection

# Query execution with progress indicator
./maestro-k query "What is the main topic?" --vdb=my-database

# Status check with progress indicator
./maestro-k status
```

#### Status Command

```bash
# Show overall system status
./maestro-k status

# Show status for a specific vector database
./maestro-k status --vdb=my-database

# Show detailed status with verbose output
./maestro-k status --verbose
```

Example output:
```
🔍 Maestro Knowledge System Status
==================================
📊 Vector Database: test_remote_weaviate (weaviate)
   📁 Collection: test_collection
   📄 Documents: 3
   📂 Collections: test_collection, another_collection
   🧠 Supported Embeddings: text-embedding-3-small, text-embedding-3-large
   ✅ Status: Online

📈 Summary:
   • Total Vector Databases: 1
   • Total Documents: 3
   • MCP Server: http://localhost:8030/mcp
   • Connection: ✅ Active
```

### Command Aliases

For convenience, the CLI provides shorter aliases for all resource commands:

```bash
# Vector databases
./maestro-k vectordb list    # or: ./maestro-k vdb list

# Collections  
./maestro-k collection list  # or: ./maestro-k coll list

# Documents
./maestro-k document list    # or: ./maestro-k doc list

# Embeddings
./maestro-k embedding list   # or: ./maestro-k embed list
```

### Interactive Selection Examples

```bash
# Interactive selection when flags are missing
./maestro-k collection list             # Prompts you to select a vector database
./maestro-k document list               # Prompts you to select both VDB and collection
./maestro-k query "test"                # Prompts you to select a vector database

# Auto-completion for resource names and file paths
./maestro-k collection list --vdb=<TAB> # Completes vector database names
./maestro-k document list --collection=<TAB> # Completes collection names
./maestro-k document create --file=<TAB>     # Completes file paths
./maestro-k collection create --embedding=<TAB> # Completes embedding models

# Command suggestions for typos
./maestro-k vectord                     # Suggests: vectordb
./maestro-k docum                       # Suggests: document
./maestro-k embedd                      # Suggests: embedding

# Contextual help appears after operations
./maestro-k vectordb list               # Shows tip about creating new databases
./maestro-k collection create --vdb=my-db --name=my-coll  # Shows tip about adding documents
./maestro-k query "test" --vdb=my-db    # Shows tips about doc-limit and collection flags

# Error guidance with --verbose
./maestro-k collection list --verbose   # Shows helpful suggestions for common errors
```

### MCP Server Configuration

The CLI can connect to an MCP server using several methods:

#### 1. Environment Variable (Recommended)

Set the `MAESTRO_KNOWLEDGE_MCP_SERVER_URI` environment variable:

```bash
export MAESTRO_KNOWLEDGE_MCP_SERVER_URI="http://localhost:8030"
./maestro-k vectordb list
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
./maestro-k vectordb list --mcp-server-uri="http://localhost:8030"
```

**Priority order**: Command-line flag > Environment variable > .env file > Default (http://localhost:8030)

**Supported Environment Variables**:
- `MAESTRO_KNOWLEDGE_MCP_SERVER_URI`: MCP server URI
- `WEAVIATE_API_KEY`: Weaviate API key for Weaviate backend
- `WEAVIATE_URL`: Weaviate cluster URL
- `OPENAI_API_KEY`: OpenAI API key for embeddings

### Chunking support

- Configure chunking when defining collections via YAML. The CLI exposes discovery of supported strategies with:

```bash
./maestro-k chunking list
```

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
./maestro-k vectordb list --mcp-server-uri="localhost:8030"
./maestro-k vectordb list --mcp-server-uri="http://localhost:8030"
./maestro-k vectordb list --mcp-server-uri="https://example.com:9000"
```

### Global Flags

- `--verbose`: Show detailed output
- `--silent`: Suppress success messages
- `--dry-run`: Test commands without making changes
- `--force` / `-f`: Skip confirmation prompts for destructive operations
- `--mcp-server-uri`: Override MCP server URI
- `--help`: Show help information
- `--version`: Show version information

### List Commands

The CLI provides resource-based list commands for vector databases, collections, and documents:

```bash
# List all vector databases
./maestro-k vectordb list

# List with verbose output
./maestro-k vectordb list --verbose

# Test the command without connecting to server
./maestro-k vectordb list --dry-run

# List collections for a specific vector database
./maestro-k collection list --vdb=my-database

# List collections with verbose output
./maestro-k collection list --vdb=my-database --verbose

# Test collections command without connecting to server
./maestro-k collection list --vdb=my-database --dry-run

# List embeddings for a specific vector database
./maestro-k embedding list --vdb=my-database

# List embeddings with verbose output
./maestro-k embedding list --vdb=my-database --verbose

# Test embeddings command without connecting to server
./maestro-k embedding list --vdb=my-database --dry-run

# List documents in a specific collection
./maestro-k document list --vdb=my-database --collection=my-collection

# List documents with verbose output
./maestro-k document list --vdb=my-database --collection=my-collection --verbose

# Test documents command without connecting to server
./maestro-k document list --vdb=my-database --collection=my-collection --dry-run
```

#### Output Format

**Vector Databases**: When databases are found, the output shows:
- Database name and type
- Collection name
- Document count

Example:
```text
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
```text
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
- `--collection`: Specific collection to search in (optional; if omitted you'll be prompted interactively unless in --dry-run or non-interactive mode)

**Collections**: When listing collections for a vector database, the output shows:
- All collections available in the vector database

Example:
```text
Collections in vector database 'my-database': [
  "Collection1",
  "Collection2",
  "MaestroDocs"
]
```

**Documents**: When listing documents in a collection, the output shows:
- All documents in the specified collection with their properties

Example:
```json
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

### Create Commands

The CLI provides resource-based create commands for vector databases, collections, and documents:

#### Create Vector Database Command

```bash
# Create vector database from YAML file
./maestro-k vdb create config.yaml

# Create with verbose output
./maestro-k vdb create config.yaml --verbose

# Create with dry-run mode
./maestro-k vdb create config.yaml --dry-run

# Override configuration values
./maestro-k vdb create config.yaml --type=weaviate --uri=localhost:8080
```

**Supported Override Flags**:
- `--type`: Override database type (milvus, weaviate)
- `--uri`: Override connection URI
- `--collection-name`: Override collection name
- `--embedding`: Override embedding model
- `--mode`: Override deployment mode (local, remote)

#### Create Collection Command

```bash
# Create collection in vector database
./maestro-k collection create --name=my-collection --vdb=my-database

# Create collection with verbose output
./maestro-k collection create --name=my-collection --vdb=my-database --verbose

# Create collection with dry-run mode
./maestro-k collection create --name=my-collection --vdb=my-database --dry-run
```

#### Create Document Command

```bash
# Create document from file
./maestro-k document create --name=my-doc --file=document.txt --vdb=my-database --collection=my-collection

# Create document with dry-run mode
./maestro-k document create --name=my-doc --file=document.txt --vdb=my-database --collection=my-collection --dry-run
```

### Write Command

The `write` command is an alias for creating documents:

```bash
# Write document from file
./maestro-k write document my-database my-collection my-doc --file-name=document.txt

# Write document using short aliases
./maestro-k write doc my-database my-collection my-doc --file-name=document.txt
./maestro-k write vdb-doc my-database my-collection my-doc --file-name=document.txt

# Write document with dry-run mode
./maestro-k write document my-database my-collection my-doc --file-name=document.txt --dry-run

Note: --embed on write is deprecated and ignored; embedding is configured per collection when the collection is created.
```

### Confirmation Prompts for Destructive Operations

The CLI includes safety features to prevent accidental deletion of resources. All delete operations require user confirmation unless the `--force` flag is used.

#### Confirmation Behavior

- **Interactive Confirmation**: Delete commands prompt for confirmation before proceeding
- **Force Flag**: Use `--force` or `-f` to skip confirmation prompts
- **Dry-run Mode**: Confirmation is automatically skipped in dry-run mode
- **Silent Mode**: Confirmation is automatically skipped in silent mode

#### Confirmation Examples

```bash
# Delete vector database with confirmation prompt
./maestro-k vectordb delete my-database
# Output: ⚠️  Are you sure you want to delete 'vector database 'my-database''? This action cannot be undone. [y/N]:

# Skip confirmation with --force flag
./maestro-k vectordb delete my-database --force

# Skip confirmation with -f flag
./maestro-k vectordb delete my-database -f

# Confirmation automatically skipped in dry-run mode
./maestro-k vectordb delete my-database --dry-run

# Confirmation automatically skipped in silent mode
./maestro-k vectordb delete my-database --silent
```

### Delete Commands

The CLI provides resource-based delete commands for vector databases, collections, and documents:

#### Delete Vector Database Command

```bash
# Delete vector database (with confirmation prompt)
./maestro-k vdb delete my-database

# Delete with verbose output
./maestro-k vdb delete my-database --verbose

# Delete with dry-run mode
./maestro-k vdb delete my-database --dry-run

# Skip confirmation with force flag
./maestro-k vdb delete my-database --force
```

#### Delete Collection Command

```bash
# Delete collection from vector database (with confirmation prompt)
./maestro-k collection delete my-collection --vdb=my-database

# Delete collection with verbose output
./maestro-k collection delete my-collection --vdb=my-database --verbose

# Delete collection with dry-run mode
./maestro-k collection delete my-collection --vdb=my-database --dry-run

# Skip confirmation with force flag
./maestro-k collection delete my-collection --vdb=my-database --force
```

#### Delete Document Command

```bash
# Delete document from collection (with confirmation prompt)
./maestro-k document delete my-document --vdb=my-database --collection=my-collection

# Delete document with verbose output
./maestro-k document delete my-document --vdb=my-database --collection=my-collection --verbose

# Delete document with dry-run mode
./maestro-k document delete my-document --vdb=my-database --collection=my-collection --dry-run

# Skip confirmation with force flag
./maestro-k document delete my-document --vdb=my-database --collection=my-collection --force
```

### Search Command

The `search` command performs a vector search and returns JSON results suitable for programmatic use.

```bash
# Basic search (prompts for collection if omitted)
./maestro-k search "Find information about API endpoints" --vdb=my-database

# Search with specific document limit and collection
./maestro-k search "quantum circuits" --vdb=my-database --collection=my-collection --doc-limit 10
```

Search output schema (normalized across backends):

- id, url, text
- metadata:
   - doc_name
   - chunk_sequence_number
   - total_chunks
   - offset_start, offset_end
   - chunk_size
- similarity: canonical score in [0..1]
- distance: cosine distance (for reference)
- rank: 1-based rank
- _metric: e.g., "cosine"
- _search_mode: "vector" or "keyword"

Flags:

- `--doc-limit, -d`: Maximum number of documents to consider (default: 5)
- `--collection`: Specific collection to search in (optional; if omitted you'll be prompted interactively unless in --dry-run or non-interactive mode)

### Query Command

The `query` command allows you to search documents using natural language queries with semantic search:

```bash
# Query documents using natural language
./maestro-k query "What is the main topic of the documents?" --vdb=my-database

# Query with specific document limit
./maestro-k query "Find information about API endpoints" --vdb=my-database --doc-limit 10

# Query with collection name specification
./maestro-k query "Search for technical documentation" --vdb=my-database --collection=my-collection

# Query with dry-run mode
./maestro-k query "Test query" --vdb=my-database --dry-run

# Query with verbose output
./maestro-k query "Complex search query" --vdb=my-database --verbose
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
- `--collection`: Specific collection to search in (optional; if omitted you'll be prompted interactively unless in --dry-run or non-interactive mode)
- `--dry-run`: Test the command without making changes
- `--verbose`: Show detailed output
- `--silent`: Suppress success messages

#### Query Examples

```bash
# Basic query
./maestro-k query "What is machine learning?" --vdb=my-database

# Query with higher document limit
./maestro-k query "Find all API documentation" --vdb=my-database --doc-limit 20

# Query specific collection
./maestro-k query "Search for user guides" --vdb=my-database --collection=documentation

# Test query without execution
./maestro-k query "Test query" --vdb=my-database --dry-run
```

### Collection Info Command

Show collection information (embedding and chunking):

```bash
./maestro-k collection info --vdb=my-database --name=my-collection
```

**Collection Information Output**: The output shows:
- Collection name
- Document count
- Database type
- Embedding information
- Chunking configuration (strategy and parameters)
- Additional metadata

Example:

Collection information for 'my-collection' in vector database 'my-database':

```json
{
  "name": "my-collection",
  "document_count": 15,
  "db_type": "weaviate",
   "embedding": "text2vec-weaviate",
   "chunking": {
      "strategy": "Sentence",
      "parameters": { "chunk_size": 512, "overlap": 32 }
   },
  "metadata": {
    "description": "My test collection",
    "vectorizer": "text2vec-weaviate",
    "properties_count": 4,
    "module_config": null
  }
}
```

Note: The CLI does not currently provide a standalone "document get" command.

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
   ./maestro-k vdb list --mcp-server-uri="http://localhost:8030"
   ```

3. **List with verbose output**:
   ```bash
   ./maestro-k vdb list --mcp-server-uri="http://localhost:8030" --verbose
   ```

4. **List collections for a database**:
   ```bash
   ./maestro-k collection list --vdb=my-database --mcp-server-uri="http://localhost:8030"
   ```

5. **List documents in a collection**:
   ```bash
   ./maestro-k document list --vdb=my-database --collection=my-collection --mcp-server-uri="http://localhost:8030"
   ```

6. **Query documents using natural language**:
   ```bash
   ./maestro-k query "What is the main topic?" --vdb=my-database --mcp-server-uri="http://localhost:8030"
   ./maestro-k query "Find API documentation" --vdb=my-database --doc-limit 10 --mcp-server-uri="http://localhost:8030"
   ```

7. **Create a vector database from YAML**:
   ```bash
   ./maestro-k vdb create config.yaml --mcp-server-uri="http://localhost:8030"
   ```

8. **Delete a vector database**:
   ```bash
   ./maestro-k vdb delete my-database --mcp-server-uri="http://localhost:8030"
   ```

### Examples

See the [examples/](examples/) directory for usage examples:

- [example_usage.sh](examples/example_usage.sh) - Comprehensive CLI usage demonstration with MCP server

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
./maestro-k vectordb list --mcp-server-uri="http://localhost:8030" --verbose
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

```text
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
├── lint.sh              # Comprehensive linting script
├── test_integration.sh  # Integration test script
└── README.md           # This file
```

### Code Quality and Linting

The CLI includes comprehensive linting and code quality checks to ensure maintainable, high-quality Go code.

#### Available Linting Tools

- **staticcheck**: Detects unused code, unreachable code, and other code quality issues
- **golangci-lint**: Advanced Go linting with multiple analyzers
- **go fmt**: Code formatting
- **go vet**: Static analysis
- **go mod tidy/verify**: Dependency management
- **Race condition checks**: Thread safety validation

#### Running Linting

```bash
# Run all linting checks
./lint.sh

# Run specific checks
go fmt ./src/...           # Format code
go vet ./src/...           # Static analysis
staticcheck ./src/...      # Unused code detection
golangci-lint run ./src/... # Advanced linting
```

#### Linting in CI/CD

The project includes automated linting in CI/CD pipelines:

- **Main CI**: Runs CLI linting for all changes
- **CLI CI**: Dedicated CLI linting job for CLI-specific changes
- **Quality Gate**: Linting failures block merges until resolved

#### Linting Features

- **Unused Code Detection**: Automatically identifies unused variables, functions, and imports
- **Code Formatting**: Ensures consistent code style across the project
- **Static Analysis**: Catches potential bugs and code smells
- **Dependency Management**: Verifies module dependencies are clean and secure
- **Thread Safety**: Detects race conditions in concurrent code

### Adding New Commands

1. Create a new command file (e.g., `src/new_command.go`)
2. Define the command using Cobra
3. Add the command to `main.go`
4. Update this README
5. **Run linting**: `./lint.sh` to ensure code quality

### Testing

```bash
# Run all tests
go test ./tests/...

# Run integration tests
./test_integration.sh

# Build and test manually
go build -o maestro-k src/*.go
./maestro-k --help

# Run with verbose output
go test -v ./tests/...
```

### Development Workflow

1. **Make changes** to CLI code
2. **Run linting**: `./lint.sh` to check code quality
3. **Run tests**: `go test ./tests/...` to verify functionality
4. **Run integration tests**: `./test_integration.sh` for end-to-end validation
5. **Commit changes** with descriptive commit messages

### Code Quality Standards

- **No unused code**: All variables, functions, and imports must be used
- **Consistent formatting**: Code follows `go fmt` standards
- **Static analysis clean**: No `go vet` warnings
- **Dependency hygiene**: Clean module dependencies
- **Thread safety**: No race conditions in concurrent code

## License

Apache 2.0 License - see the main project LICENSE file for details.
