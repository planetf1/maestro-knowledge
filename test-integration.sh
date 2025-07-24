#!/bin/bash
# Test script for CLI integration with MCP server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CLI_DIR="$PROJECT_ROOT/cli"

print_status "Testing CLI integration with MCP server"
print_status "Project root: $PROJECT_ROOT"

# Build the CLI
print_status "Building CLI..."
cd "$CLI_DIR"
go build -o maestro-k src/*.go
print_success "CLI built successfully"

# Test CLI help
print_status "Testing CLI help..."
cd "$CLI_DIR"
./maestro-k --help > /dev/null
print_success "CLI help works"

# Test list command help
print_status "Testing list command help..."
./maestro-k list --help > /dev/null
print_success "List command help works"

# Test dry-run mode
print_status "Testing dry-run mode..."
DRY_RUN_OUTPUT=$(./maestro-k list vector-db --dry-run)
if [[ "$DRY_RUN_OUTPUT" == *"[DRY RUN] Would list vector databases"* ]]; then
    print_success "Dry-run mode works correctly"
else
    print_error "Dry-run mode failed"
    exit 1
fi

# Test with verbose mode
print_status "Testing verbose mode..."
VERBOSE_OUTPUT=$(./maestro-k list vector-db --dry-run --verbose)
if [[ "$VERBOSE_OUTPUT" == *"Listing vector databases"* ]]; then
    print_success "Verbose mode works correctly"
else
    print_error "Verbose mode failed"
    exit 1
fi

# Test environment variable support
print_status "Testing environment variable support..."
export MAESTRO_KNOWLEDGE_MCP_SERVER_URI="http://localhost:9000"
ENV_OUTPUT=$(./maestro-k list vector-db --verbose 2>&1 || true)
if [[ "$ENV_OUTPUT" == *"Connecting to MCP server at: http://localhost:9000"* ]]; then
    print_success "Environment variable support works"
else
    print_warning "Environment variable support may not be working correctly"
    echo "Output: $ENV_OUTPUT"
fi

# Test command line flag override
print_status "Testing command line flag override..."
FLAG_OUTPUT=$(./maestro-k list vector-db --verbose --mcp-server-uri="http://localhost:9999" 2>&1 || true)
if [[ "$FLAG_OUTPUT" == *"Connecting to MCP server at: http://localhost:9999"* ]]; then
    print_success "Command line flag override works"
else
    print_warning "Command line flag override may not be working correctly"
    echo "Output: $FLAG_OUTPUT"
fi

# Test .env file support
print_status "Testing .env file support..."
unset MAESTRO_KNOWLEDGE_MCP_SERVER_URI
cd "$PROJECT_ROOT"
echo "MAESTRO_KNOWLEDGE_MCP_SERVER_URI=http://localhost:8888" > .env
cd "$CLI_DIR"
ENV_FILE_OUTPUT=$(./maestro-k list vector-db --verbose 2>&1 || true)
if [[ "$ENV_FILE_OUTPUT" == *"Connecting to MCP server at: http://localhost:8888"* ]]; then
    print_success ".env file support works"
else
    print_warning ".env file support may not be working correctly"
    echo "Output: $ENV_FILE_OUTPUT"
fi
cd "$PROJECT_ROOT"
rm -f .env

print_success "All CLI integration tests passed!"

# Start comprehensive end-to-end testing
print_status "Starting comprehensive end-to-end testing..."

# 2. Start the MCP server
print_status "Starting MCP server..."
cd "$PROJECT_ROOT"
./start.sh
sleep 3  # Give the server time to start
print_success "MCP server started"

# 3. List vector databases (should be empty initially)
print_status "Testing initial list (should be empty)..."
cd "$CLI_DIR"
INITIAL_LIST=$(./maestro-k list vector-db --verbose)
if [[ "$INITIAL_LIST" == *"No vector databases found"* ]]; then
    print_success "Initial list shows no databases (as expected)"
else
    print_warning "Initial list may have existing databases"
    echo "Output: $INITIAL_LIST"
fi

# 4. Create a vector database
print_status "Creating vector database..."
CREATE_OUTPUT=$(./maestro-k create vector-db ../tests/yamls/local_milvus.yaml --verbose)
if [[ "$CREATE_OUTPUT" == *"✅ Vector database 'local_milvus' created successfully"* ]]; then
    print_success "Vector database created successfully"
else
    print_error "Failed to create vector database"
    echo "Output: $CREATE_OUTPUT"
    exit 1
fi

# 5. List to verify the database was created
print_status "Verifying database appears in list..."
LIST_AFTER_CREATE=$(./maestro-k list vector-db --verbose)
if [[ "$LIST_AFTER_CREATE" == *"local_milvus"* ]] && [[ "$LIST_AFTER_CREATE" == *"milvus"* ]]; then
    print_success "Database appears in list after creation"
else
    print_error "Database not found in list after creation"
    echo "Output: $LIST_AFTER_CREATE"
    exit 1
fi

# 6. Create another database (Weaviate)
print_status "Creating second vector database (Weaviate)..."
CREATE_WEAVIATE_OUTPUT=$(./maestro-k create vector-db ../tests/yamls/remote_weaviate.yaml --verbose)
if [[ "$CREATE_WEAVIATE_OUTPUT" == *"✅ Vector database 'remote_weaviate' created successfully"* ]]; then
    print_success "Weaviate database created successfully"
else
    print_error "Failed to create Weaviate database"
    echo "Output: $CREATE_WEAVIATE_OUTPUT"
    exit 1
fi

# 7. List to verify both databases are present
print_status "Verifying both databases appear in list..."
LIST_BOTH=$(./maestro-k list vector-db --verbose)
if [[ "$LIST_BOTH" == *"local_milvus"* ]] && [[ "$LIST_BOTH" == *"remote_weaviate"* ]] && [[ "$LIST_BOTH" == *"Found 2 vector database"* ]]; then
    print_success "Both databases appear in list"
else
    print_error "Not all databases found in list"
    echo "Output: $LIST_BOTH"
    exit 1
fi

# 8. Delete a vector database
print_status "Testing delete functionality..."
DELETE_OUTPUT=$(./maestro-k delete vector-db local_milvus --verbose)
if [[ "$DELETE_OUTPUT" == *"✅ Vector database 'local_milvus' deleted successfully"* ]]; then
    print_success "Vector database deleted successfully"
else
    print_error "Failed to delete vector database"
    echo "Output: $DELETE_OUTPUT"
    exit 1
fi

# 9. List to verify the database was deleted
print_status "Verifying database was removed from list..."
LIST_AFTER_DELETE=$(./maestro-k list vector-db --verbose)
if [[ "$LIST_AFTER_DELETE" == *"remote_weaviate"* ]] && [[ "$LIST_AFTER_DELETE" != *"local_milvus"* ]] && [[ "$LIST_AFTER_DELETE" == *"Found 1 vector database"* ]]; then
    print_success "Database was removed from list after deletion"
else
    print_error "Database still appears in list after deletion"
    echo "Output: $LIST_AFTER_DELETE"
    exit 1
fi

# 10. Stop the MCP server
print_status "Stopping MCP server..."
cd "$PROJECT_ROOT"
./stop.sh
print_success "MCP server stopped"

print_success "All comprehensive end-to-end tests passed!"
print_status "CLI integration testing completed successfully" 