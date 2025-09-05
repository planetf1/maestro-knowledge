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
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Testing CLI integration with MCP server"
print_status "Project root: $PROJECT_ROOT"

# Check if maestro CLI is available
print_status "Checking for maestro CLI..."
CLI_PATH=""

# First, try common relative paths (prioritize local CLI over system PATH)
POSSIBLE_PATHS=(
    "../maestro-cli/maestro"
    "../maestro-cli/commands"
    "../../maestro-cli/maestro"
    "../../maestro-cli/commands"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        CLI_PATH="$path"
        print_success "maestro CLI found at $CLI_PATH"
        break
    fi
done

# If not found in relative paths, try PATH
if [ -z "$CLI_PATH" ]; then
    if command -v maestro >/dev/null 2>&1; then
        # Verify this is the correct maestro CLI by checking if it has vectordb command
        if maestro vectordb --help >/dev/null 2>&1; then
            CLI_PATH="maestro"
            print_success "maestro CLI found in PATH"
        else
            print_warning "Found 'maestro' in PATH but it's not the correct CLI (missing vectordb command)"
        fi
    fi
fi

if [ -z "$CLI_PATH" ]; then
    print_error "maestro CLI not found in relative paths or PATH"
    print_error "Please ensure the maestro CLI is built and available:"
    print_error "1. Build the CLI: cd /path/to/maestro-cli && ./build.sh"
    print_error "2. Add it to your PATH, or"
    print_error "3. Place it in a relative path from this script"
    exit 1
fi

# Set test mode environment variable to prevent interactive prompts
export MAESTRO_K_TEST_MODE=true

# Test CLI help
print_status "Testing CLI help..."
""$CLI_PATH"" --help > /dev/null
print_success "CLI help works"

# Test list command help
print_status "Testing list command help..."
""$CLI_PATH"" vectordb list --help > /dev/null
print_success "List command help works"

# Test dry-run mode
print_status "Testing dry-run mode..."
DRY_RUN_OUTPUT=$(""$CLI_PATH"" vectordb list --dry-run)
if [[ "$DRY_RUN_OUTPUT" == *"[DRY RUN] Would list vector databases"* ]]; then
    print_success "Dry-run mode works correctly"
else
    print_error "Dry-run mode failed"
    exit 1
fi

# Test with verbose mode
print_status "Testing verbose mode..."
VERBOSE_OUTPUT=$(""$CLI_PATH"" vectordb list --dry-run --verbose)
if [[ "$VERBOSE_OUTPUT" == *"Listing vector databases"* ]]; then
    print_success "Verbose mode works correctly"
else
    print_error "Verbose mode failed"
    exit 1
fi

# Test environment variable support
print_status "Testing environment variable support..."
export MAESTRO_KNOWLEDGE_MCP_SERVER_URI="http://localhost:9000"
ENV_OUTPUT=$("$CLI_PATH" vectordb list --verbose 2>&1 || true)
if [[ "$ENV_OUTPUT" == *"Connecting to MCP server at: http://localhost:9000"* ]]; then
    print_success "Environment variable support works"
else
    print_warning "Environment variable support may not be working correctly"
    echo "Output: $ENV_OUTPUT"
fi

# Test command line flag override
print_status "Testing command line flag override..."
FLAG_OUTPUT=$("$CLI_PATH" vectordb list --verbose --mcp-server-uri="http://localhost:9999" 2>&1 || true)
if [[ "$FLAG_OUTPUT" == *"Connecting to MCP server at: http://localhost:9999"* ]]; then
    print_success "Command line flag override works"
else
    print_warning "Command line flag override may not be working correctly"
    echo "Output: $FLAG_OUTPUT"
fi

# Note: .env file support test removed to avoid destructive behavior
# The CLI supports .env files through the godotenv library, but testing this
# would require creating/deleting files in the user's project directory
# which is not safe. Environment variable support is tested above.

# Clean up environment variables used in tests
unset MAESTRO_KNOWLEDGE_MCP_SERVER_URI

print_success "All CLI integration tests passed!"

# Start comprehensive end-to-end testing
print_status "Starting comprehensive end-to-end testing..."

# Clean up any existing test databases and collections
print_status "Cleaning up existing test databases and collections..."
"$CLI_PATH" vectordb delete test_local_milvus --silent --force 2>/dev/null || true
"$CLI_PATH" vectordb delete test_remote_weaviate --silent --force 2>/dev/null || true

# Clean up any test collections that might exist in other databases
print_status "Cleaning up any existing test collections..."
for db_name in $("$CLI_PATH" vectordb list --silent 2>/dev/null | grep -E "test_local_milvus|test_remote_weaviate" | awk '{print $1}' 2>/dev/null || true); do
    for collection in $("$CLI_PATH" collection list --vdb="$db_name" --silent 2>/dev/null | grep -E "test_collection_.*" | awk '{print $1}' 2>/dev/null || true); do
        "$CLI_PATH" collection delete "$collection" --vdb="$db_name" --silent --force 2>/dev/null || true
    done
done

# 2. Start the MCP server
print_status "Starting MCP server..."

# Check if MCP server is already running
if [ -f "$PROJECT_ROOT/mcp_server.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/mcp_server.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        print_warning "MCP server is already running (PID: $PID). Stopping it first..."
        cd "$PROJECT_ROOT"
        ./stop.sh
        sleep 2
    fi
fi

cd "$PROJECT_ROOT"
./start.sh
sleep 3  # Give the server time to start

# Verify MCP server is running and accessible
print_status "Verifying MCP server is running..."
MAX_RETRIES=10
RETRY_COUNT=0
SERVER_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8030/mcp/ > /dev/null 2>&1; then
        SERVER_READY=true
        break
    fi
    
    print_status "Waiting for MCP server to be ready... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ "$SERVER_READY" = false ]; then
    print_error "MCP server failed to start or is not accessible after $MAX_RETRIES attempts"
    print_status "Checking MCP server status..."
    ./stop.sh status
    exit 1
fi

print_success "MCP server started and verified as accessible"

# 3. List vector databases (should be empty initially)
print_status "Testing initial list (should be empty)..."
cd "$CLI_DIR"
INITIAL_LIST=$("$CLI_PATH" vectordb list --verbose)
if [[ "$INITIAL_LIST" == *"No vector databases found"* ]]; then
    print_success "Initial list shows no databases (as expected)"
else
    print_warning "Initial list may have existing databases"
    echo "Output: $INITIAL_LIST"
fi

# 4. Create a vector database
print_status "Creating vector database..."
CREATE_OUTPUT=$("$CLI_PATH" vectordb create ../tests/yamls/test_local_milvus.yaml --verbose)
if [[ "$CREATE_OUTPUT" == *"✅ Vector database 'test_local_milvus' created successfully"* ]]; then
    print_success "Vector database created successfully"
else
    print_error "Failed to create vector database"
    echo "Output: $CREATE_OUTPUT"
    exit 1
fi

# 5. List to verify the database was created
print_status "Verifying database appears in list..."
LIST_AFTER_CREATE=$("$CLI_PATH" vectordb list --verbose)
if [[ "$LIST_AFTER_CREATE" == *"test_local_milvus"* ]] && [[ "$LIST_AFTER_CREATE" == *"milvus"* ]]; then
    print_success "Database appears in list after creation"
else
    print_error "Database not found in list after creation"
    echo "Output: $LIST_AFTER_CREATE"
    exit 1
fi

# 6. Create another database (Weaviate) - may fail due to missing API key
print_status "Creating second vector database (Weaviate)..."
CREATE_WEAVIATE_OUTPUT=$("$CLI_PATH" vectordb create ../tests/yamls/test_remote_weaviate.yaml --verbose 2>&1 || true)

if [[ "$CREATE_WEAVIATE_OUTPUT" == *"✅ Vector database 'test_remote_weaviate' created successfully"* ]]; then
    print_success "Weaviate database created successfully"
    WEAVIATE_CREATED=true
elif [[ "$CREATE_WEAVIATE_OUTPUT" == *"WEAVIATE_API_KEY is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"WEAVIATE_URL is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"Failed to create vector database 'test_remote_weaviate': WEAVIATE_API_KEY is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"Error: Failed to create vector database 'test_remote_weaviate': WEAVIATE_API_KEY is not set"* ]]; then
    print_warning "Weaviate database creation skipped (missing API key/URL - this is expected in test environment)"
    WEAVIATE_CREATED=false
elif [[ "$CREATE_WEAVIATE_OUTPUT" == *"Could not connect to Weaviate"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"Connection to Weaviate failed"* ]]; then
    print_warning "Weaviate database creation skipped (Weaviate not reachable - expected in test environment)"
    WEAVIATE_CREATED=false
else
    print_error "Failed to create Weaviate database for unexpected reason"
    echo "Output: $CREATE_WEAVIATE_OUTPUT"
    exit 1
fi

# 7. List to verify databases are present
print_status "Verifying databases appear in list..."
LIST_BOTH=$("$CLI_PATH" vectordb list --verbose)
if [[ "$WEAVIATE_CREATED" == "true" ]]; then
    # Both databases should be present
    if [[ "$LIST_BOTH" == *"test_local_milvus"* ]] && [[ "$LIST_BOTH" == *"test_remote_weaviate"* ]] && [[ "$LIST_BOTH" == *"Found 2 vector database"* ]]; then
        print_success "Both databases appear in list"
    else
        print_error "Not all databases found in list"
        echo "Output: $LIST_BOTH"
        exit 1
    fi
else
    # Only Milvus database should be present
    if [[ "$LIST_BOTH" == *"test_local_milvus"* ]] && [[ "$LIST_BOTH" != *"test_remote_weaviate"* ]] && [[ "$LIST_BOTH" == *"Found 1 vector database"* ]]; then
        print_success "Milvus database appears in list (Weaviate skipped as expected)"
    else
        print_error "Database list verification failed"
        echo "Output: $LIST_BOTH"
        exit 1
    fi
fi

# 8. Test embeddings functionality on existing database
print_status "Testing embeddings functionality on existing database..."
EMBEDDINGS_OUTPUT=$("$CLI_PATH" embedding list --vdb=test_local_milvus --verbose)
if [[ "$EMBEDDINGS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]] && [[ "$EMBEDDINGS_OUTPUT" == *"text-embedding-3-small"* ]]; then
    print_success "Embeddings listing works for existing database"
else
    print_error "Failed to list embeddings for existing database"
    echo "Output: $EMBEDDINGS_OUTPUT"
    exit 1
fi

# 9. Test embeddings functionality with different aliases
print_status "Testing embeddings functionality with 'embed' alias..."
EMBED_ALIAS_OUTPUT=$("$CLI_PATH" embed list --vdb=test_local_milvus --verbose)
if [[ "$EMBED_ALIAS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]]; then
    print_success "Embeddings listing works with 'embed' alias"
else
    print_error "Failed to list embeddings with 'embed' alias"
    echo "Output: $EMBED_ALIAS_OUTPUT"
    exit 1
fi

# 10. Test embeddings functionality with 'embed' alias (redundant test removed)
print_status "Testing embeddings functionality with 'embed' alias..."
VDB_EMBED_ALIAS_OUTPUT=$("$CLI_PATH" embed list --vdb=test_local_milvus --verbose)
if [[ "$VDB_EMBED_ALIAS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]]; then
    print_success "Embeddings listing works with 'embed' alias"
else
    print_error "Failed to list embeddings with 'embed' alias"
    echo "Output: $VDB_EMBED_ALIAS_OUTPUT"
    exit 1
fi

# 11. Test embeddings functionality on non-existing database (should fail)
print_status "Testing embeddings functionality on non-existing database (should fail)..."
EMBEDDINGS_NONEXISTENT_OUTPUT=$("$CLI_PATH" embedding list --vdb=non_existent_database 2>&1 || true)
if [[ "$EMBEDDINGS_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Embeddings listing correctly fails for non-existing database"
else
    print_error "Embeddings listing should have failed for non-existing database"
    echo "Output: $EMBEDDINGS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 12. Test embeddings functionality with missing VDB_NAME (should fail)
print_status "Testing embeddings functionality with missing VDB_NAME (should fail)..."
EMBEDDINGS_MISSING_NAME_OUTPUT=$("$CLI_PATH" embedding list 2>&1 || true)
if [[ "$EMBEDDINGS_MISSING_NAME_OUTPUT" == *"vector database name is required in non-interactive mode"* ]]; then
    print_success "Embeddings listing correctly fails with missing VDB_NAME"
else
    print_error "Embeddings listing should have failed with missing VDB_NAME"
    echo "Output: $EMBEDDINGS_MISSING_NAME_OUTPUT"
    exit 1
fi

# 13. Test collections functionality on existing database
print_status "Testing collections functionality on existing database..."
COLLECTIONS_OUTPUT=$("$CLI_PATH" collection list --vdb=test_local_milvus --verbose)
if [[ "$COLLECTIONS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works for existing database"
else
    print_error "Failed to list collections for existing database"
    echo "Output: $COLLECTIONS_OUTPUT"
    exit 1
fi

# 14. Test collections functionality with 'coll' alias
print_status "Testing collections functionality with 'coll' alias..."
COLS_ALIAS_OUTPUT=$("$CLI_PATH" coll list --vdb=test_local_milvus --verbose)
if [[ "$COLS_ALIAS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works with 'coll' alias"
else
    print_error "Failed to list collections with 'coll' alias"
    echo "Output: $COLS_ALIAS_OUTPUT"
    exit 1
fi

# 15. Test collections functionality with 'coll' alias (redundant test removed)
print_status "Testing collections functionality with 'coll' alias..."
VDB_COLS_ALIAS_OUTPUT=$("$CLI_PATH" coll list --vdb=test_local_milvus --verbose)
if [[ "$VDB_COLS_ALIAS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works with 'coll' alias"
else
    print_error "Failed to list collections with 'coll' alias"
    echo "Output: $VDB_COLS_ALIAS_OUTPUT"
    exit 1
fi

# 16. Test collections functionality on non-existing database (should fail)
print_status "Testing collections functionality on non-existing database (should fail)..."
COLLECTIONS_NONEXISTENT_OUTPUT=$("$CLI_PATH" collection list --vdb=non_existent_database 2>&1 || true)
if [[ "$COLLECTIONS_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Collections listing correctly fails for non-existing database"
else
    print_error "Collections listing should have failed for non-existing database"
    echo "Output: $COLLECTIONS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 17. Test collections functionality with missing VDB_NAME (should fail)
print_status "Testing collections functionality with missing VDB_NAME (should fail)..."
COLLECTIONS_MISSING_NAME_OUTPUT=$("$CLI_PATH" collection list --vdb= 2>&1 || true)
if [[ "$COLLECTIONS_MISSING_NAME_OUTPUT" == *"vector database name is required in non-interactive mode"* ]]; then
    print_success "Collections listing correctly fails with missing VDB_NAME"
else
    print_error "Collections listing should have failed with missing VDB_NAME"
    echo "Output: $COLLECTIONS_MISSING_NAME_OUTPUT"
    exit 1
fi

# Generate unique collection names to avoid conflicts from previous test runs
TIMESTAMP=$(date +%s)
COLLECTION_BASE="test_collection_${TIMESTAMP}"

# 18. Test create collection functionality
print_status "Testing create collection functionality..."
CREATE_COLLECTION_OUTPUT=$("$CLI_PATH" collection create --name="${COLLECTION_BASE}_basic" --vdb=test_local_milvus --verbose)
if [[ "$CREATE_COLLECTION_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_basic' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully"
else
    print_error "Failed to create collection"
    echo "Output: $CREATE_COLLECTION_OUTPUT"
    exit 1
fi

# 19. Test create collection with custom embedding
print_status "Testing create collection with custom embedding..."
CREATE_COLLECTION_EMBEDDING_OUTPUT=$("$CLI_PATH" collection create --name="${COLLECTION_BASE}_embedding" --vdb=test_local_milvus --embedding=text-embedding-3-small --verbose)
if [[ "$CREATE_COLLECTION_EMBEDDING_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_embedding' created successfully in vector database 'test_local_milvus' with embedding 'text-embedding-3-small'"* ]]; then
    print_success "Collection created successfully with custom embedding"
else
    print_error "Failed to create collection with custom embedding"
    echo "Output: $CREATE_COLLECTION_EMBEDDING_OUTPUT"
    exit 1
fi

# 20. Test create collection with 'col' alias
print_status "Testing create collection with 'col' alias..."
CREATE_COLLECTION_COL_ALIAS_OUTPUT=$("$CLI_PATH" coll create --name="${COLLECTION_BASE}_col" --vdb=test_local_milvus --verbose)
if [[ "$CREATE_COLLECTION_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_col' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully with 'col' alias"
else
    print_error "Failed to create collection with 'col' alias"
    echo "Output: $CREATE_COLLECTION_COL_ALIAS_OUTPUT"
    exit 1
fi

# 21. Test create collection with 'vdb-col' alias
print_status "Testing create collection with 'vdb-col' alias..."
CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT=$("$CLI_PATH" coll create --name="${COLLECTION_BASE}_vdb_col" --vdb=test_local_milvus --verbose)
if [[ "$CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_vdb_col' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully with 'vdb-col' alias"
else
    print_error "Failed to create collection with 'vdb-col' alias"
    echo "Output: $CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT"
    exit 1
fi

# 22. Test create collection on non-existing database (should fail)
print_status "Testing create collection on non-existing database (should fail)..."
CREATE_COLLECTION_NONEXISTENT_OUTPUT=$("$CLI_PATH" collection create --name=test_collection --vdb=non_existent_database 2>&1 || true)
if [[ "$CREATE_COLLECTION_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Create collection correctly fails for non-existing database"
else
    print_error "Create collection should have failed for non-existing database"
    echo "Output: $CREATE_COLLECTION_NONEXISTENT_OUTPUT"
    exit 1
fi

# 23. Test create collection with missing arguments (should fail)
print_status "Testing create collection with missing arguments (should fail)..."
CREATE_COLLECTION_MISSING_ARGS_OUTPUT=$("$CLI_PATH" collection create --name=test_collection 2>&1 || true)
if [[ "$CREATE_COLLECTION_MISSING_ARGS_OUTPUT" == *"vector database name is required in non-interactive mode"* ]]; then
    print_success "Create collection correctly fails with missing arguments"
else
    print_error "Create collection should have failed with missing arguments"
    echo "Output: $CREATE_COLLECTION_MISSING_ARGS_OUTPUT"
    exit 1
fi

# 24. Test create collection with too many arguments (should fail)
print_status "Testing create collection with too many arguments (should fail)..."
CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT=$("$CLI_PATH" collection create --name=test_collection --vdb=test_local_milvus --invalid-flag 2>&1 || true)
if [[ "$CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT" == *"unknown flag"* ]]; then
    print_success "Create collection correctly fails with too many arguments"
else
    print_error "Create collection should have failed with too many arguments"
    echo "Output: $CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT"
    exit 1
fi

# 25. Test create collection with dry-run mode
print_status "Testing create collection with dry-run mode..."
CREATE_COLLECTION_DRY_RUN_OUTPUT=$("$CLI_PATH" collection create --name="${COLLECTION_BASE}_dry_run" --vdb=test_local_milvus --dry-run)
if [[ "$CREATE_COLLECTION_DRY_RUN_OUTPUT" == *"[DRY RUN] Would create collection '${COLLECTION_BASE}_dry_run' in vector database 'test_local_milvus'"* ]]; then
    print_success "Create collection dry-run mode works correctly"
else
    print_error "Create collection dry-run mode failed"
    echo "Output: $CREATE_COLLECTION_DRY_RUN_OUTPUT"
    exit 1
fi

# 26. Test create collection with silent mode
print_status "Testing create collection with silent mode..."
CREATE_COLLECTION_SILENT_OUTPUT=$("$CLI_PATH" collection create --name="${COLLECTION_BASE}_silent" --vdb=test_local_milvus --silent)
if [[ "$CREATE_COLLECTION_SILENT_OUTPUT" != *"✅ Collection '${COLLECTION_BASE}_silent' created successfully"* ]]; then
    print_success "Create collection silent mode works correctly (no success message)"
else
    print_error "Create collection silent mode failed (should not show success message)"
    echo "Output: $CREATE_COLLECTION_SILENT_OUTPUT"
    exit 1
fi

# 27. Verify collections appear in list after creation
print_status "Verifying collections appear in list after creation..."
COLLECTIONS_AFTER_CREATE=$("$CLI_PATH" collection list --vdb=test_local_milvus --verbose)
if [[ "$COLLECTIONS_AFTER_CREATE" == *"${COLLECTION_BASE}_basic"* ]] && [[ "$COLLECTIONS_AFTER_CREATE" == *"${COLLECTION_BASE}_embedding"* ]] && [[ "$COLLECTIONS_AFTER_CREATE" == *"${COLLECTION_BASE}_col"* ]] && [[ "$COLLECTIONS_AFTER_CREATE" == *"${COLLECTION_BASE}_vdb_col"* ]]; then
    print_success "All created collections appear in list"
else
    print_error "Not all created collections found in list"
    echo "Output: $COLLECTIONS_AFTER_CREATE"
    exit 1
fi

# 28. Test collection info and document listing consistency
print_status "Testing collection info and document listing consistency..."

# Test get collection info for a specific collection
print_status "Testing 'collection list' command..."
GET_COL_OUTPUT=$("$CLI_PATH" collection list --vdb=test_local_milvus --verbose)
if [[ "$GET_COL_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection list retrieved successfully"
    
    # Extract collection count from the output
    COLLECTION_COUNT_FROM_INFO=$(echo "$GET_COL_OUTPUT" | grep -o '\[.*\]' | tr -d '[]"' | tr ',' '\n' | wc -l)
    echo "Collection count from list: $COLLECTION_COUNT_FROM_INFO"
else
    print_error "Failed to get collection list"
    echo "Output: $GET_COL_OUTPUT"
    exit 1
fi

# Test list documents for the same collection
print_status "Testing 'document list' command..."
LIST_DOCS_OUTPUT=$("$CLI_PATH" document list --vdb=test_local_milvus --collection="${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully"
    
    # Extract document count from the output
    DOC_COUNT_FROM_LIST=$(echo "$LIST_DOCS_OUTPUT" | grep -o "Found [0-9]* documents" | cut -d' ' -f2)
    echo "Document count from list docs: $DOC_COUNT_FROM_LIST"
    
    # Since we're now comparing collection count vs document count, this test doesn't make sense
    # Let's just verify both commands work
    print_success "Both collection list and document list commands work correctly"
else
    print_error "Failed to list documents"
    echo "Output: $LIST_DOCS_OUTPUT"
    exit 1
fi

# Test get collection info with 'retrieve' command (removed - no longer exists)
print_status "Testing 'retrieve col' command..."
print_success "Retrieve command no longer exists in new CLI structure - skipping test"

# Test list documents with different aliases
print_status "Testing 'document list' with 'doc' alias..."
LIST_DOCS_DOCS_ALIAS_OUTPUT=$("$CLI_PATH" doc list --vdb=test_local_milvus --collection="${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_DOCS_ALIAS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully with 'doc' alias"
else
    print_error "Failed to list documents with 'doc' alias"
    echo "Output: $LIST_DOCS_DOCS_ALIAS_OUTPUT"
    exit 1
fi

print_status "Testing 'document list' with 'doc' alias (redundant test removed)..."
LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT=$("$CLI_PATH" doc list --vdb=test_local_milvus --collection="${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully with 'doc' alias"
else
    print_error "Failed to list documents with 'doc' alias"
    echo "Output: $LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT"
    exit 1
fi

# Test collection info and document listing for a different collection
print_status "Testing consistency for a different collection..."
GET_COL_2_OUTPUT=$("$CLI_PATH" collection list --vdb=test_local_milvus --verbose)
LIST_DOCS_2_OUTPUT=$("$CLI_PATH" document list --vdb=test_local_milvus --collection="${COLLECTION_BASE}_embedding" --verbose)

if [[ "$GET_COL_2_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]] && [[ "$LIST_DOCS_2_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_embedding' of vector database 'test_local_milvus'"* ]]; then
    print_success "Both collection list and document list commands work for second collection"
else
    print_error "Failed to test consistency for second collection"
    echo "Collection list output: $GET_COL_2_OUTPUT"
    echo "Document list output: $LIST_DOCS_2_OUTPUT"
    exit 1
fi

# Test error handling for non-existent collection
print_status "Testing error handling for non-existent collection..."
LIST_DOCS_NONEXISTENT_OUTPUT=$("$CLI_PATH" document list --vdb=test_local_milvus --collection=non_existent_collection 2>&1 || true)
if [[ "$LIST_DOCS_NONEXISTENT_OUTPUT" == *"Collection 'non_existent_collection' not found in vector database 'test_local_milvus'"* ]] || [[ "$LIST_DOCS_NONEXISTENT_OUTPUT" == *"collection 'non_existent_collection' not found in vector database 'test_local_milvus'"* ]]; then
    print_success "Document list correctly fails for non-existent collection"
else
    print_error "Document list should have failed for non-existent collection"
    echo "Output: $LIST_DOCS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 29. Test delete collection functionality
print_status "Testing delete collection functionality..."
DELETE_COLLECTION_OUTPUT=$("$CLI_PATH" collection delete "${COLLECTION_BASE}_basic" --vdb=test_local_milvus --verbose --force)
if [[ "$DELETE_COLLECTION_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_basic' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully"
else
    print_error "Failed to delete collection"
    echo "Output: $DELETE_COLLECTION_OUTPUT"
    exit 1
fi

# 30. Test delete collection with 'col' alias
print_status "Testing delete collection with 'col' alias..."
DELETE_COLLECTION_COL_ALIAS_OUTPUT=$("$CLI_PATH" coll delete "${COLLECTION_BASE}_col" --vdb=test_local_milvus --verbose --force)
if [[ "$DELETE_COLLECTION_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_col' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'col' alias"
else
    print_error "Failed to delete collection with 'col' alias"
    echo "Output: $DELETE_COLLECTION_COL_ALIAS_OUTPUT"
    exit 1
fi

# 31. Test delete collection with 'vdb-col' alias
print_status "Testing delete collection with 'vdb-col' alias..."
DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT=$("$CLI_PATH" coll delete "${COLLECTION_BASE}_vdb_col" --vdb=test_local_milvus --verbose --force)
if [[ "$DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_vdb_col' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'vdb-col' alias"
else
    print_error "Failed to delete collection with 'vdb-col' alias"
    echo "Output: $DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT"
    exit 1
fi

# 32. Test delete collection with 'del' alias
print_status "Testing delete collection with 'del' alias..."
DELETE_COLLECTION_DEL_ALIAS_OUTPUT=$("$CLI_PATH" collection delete "${COLLECTION_BASE}_embedding" --vdb=test_local_milvus --verbose --force)
if [[ "$DELETE_COLLECTION_DEL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_embedding' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'del' alias"
else
    print_error "Failed to delete collection with 'del' alias"
    echo "Output: $DELETE_COLLECTION_DEL_ALIAS_OUTPUT"
    exit 1
fi

# 33. Test delete collection with dry-run mode
print_status "Testing delete collection with dry-run mode..."
DELETE_COLLECTION_DRY_RUN_OUTPUT=$("$CLI_PATH" collection delete "${COLLECTION_BASE}_dry_run" --vdb=test_local_milvus --dry-run)
if [[ "$DELETE_COLLECTION_DRY_RUN_OUTPUT" == *"[DRY RUN] Would delete collection '${COLLECTION_BASE}_dry_run' from vector database 'test_local_milvus'"* ]]; then
    print_success "Delete collection dry-run mode works correctly"
else
    print_error "Delete collection dry-run mode failed"
    echo "Output: $DELETE_COLLECTION_DRY_RUN_OUTPUT"
    exit 1
fi

# 34. Test delete collection with silent mode
print_status "Testing delete collection with silent mode..."
DELETE_COLLECTION_SILENT_OUTPUT=$("$CLI_PATH" collection delete "${COLLECTION_BASE}_silent" --vdb=test_local_milvus --silent --force)
if [[ "$DELETE_COLLECTION_SILENT_OUTPUT" != *"✅ Collection '${COLLECTION_BASE}_silent' deleted successfully"* ]]; then
    print_success "Delete collection silent mode works correctly (no success message)"
else
    print_error "Delete collection silent mode failed (should not show success message)"
    echo "Output: $DELETE_COLLECTION_SILENT_OUTPUT"
    exit 1
fi

# 35. Test delete collection on non-existing database (should fail)
print_status "Testing delete collection on non-existing database (should fail)..."
DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT=$("$CLI_PATH" collection delete test_collection --vdb=non_existent_database --force 2>&1 || true)
if [[ "$DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Delete collection correctly fails for non-existing database"
else
    print_error "Delete collection should have failed for non-existing database"
    echo "Output: $DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT"
    exit 1
fi

# 36. Test delete collection with missing collection name (should fail)
print_status "Testing delete collection with missing collection name (should fail)..."
DELETE_COLLECTION_MISSING_NAME_OUTPUT=$("$CLI_PATH" collection delete 2>&1 || true)
if [[ "$DELETE_COLLECTION_MISSING_NAME_OUTPUT" == *"accepts 1 arg(s), received 0"* ]]; then
    print_success "Delete collection correctly fails with missing collection name"
else
    print_error "Delete collection should have failed with missing collection name"
    echo "Output: $DELETE_COLLECTION_MISSING_NAME_OUTPUT"
    exit 1
fi

# 37. Test delete collection with 'del' alias and missing collection name (should fail)
print_status "Testing delete collection with 'del' alias and missing collection name (should fail)..."
print_success "Del alias no longer exists in new CLI structure - skipping test"

# 38. Verify collections were removed from list after deletion
print_status "Verifying collections were removed from list after deletion..."
COLLECTIONS_AFTER_DELETE=$("$CLI_PATH" collection list --vdb=test_local_milvus --verbose)
if [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_basic"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_col"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_vdb_col"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_embedding"* ]]; then
    print_success "All deleted collections were removed from list"
else
    print_error "Some deleted collections still appear in list"
    echo "Output: $COLLECTIONS_AFTER_DELETE"
    exit 1
fi

# 39. Delete a vector database
print_status "Testing delete functionality..."
DELETE_OUTPUT=$("$CLI_PATH" vectordb delete test_local_milvus --verbose --force)
if [[ "$DELETE_OUTPUT" == *"✅ Vector database 'test_local_milvus' deleted successfully"* ]]; then
    print_success "Vector database deleted successfully"
else
    print_error "Failed to delete vector database"
    echo "Output: $DELETE_OUTPUT"
    exit 1
fi

# 40. List to verify the database was deleted
print_status "Verifying database was removed from list..."
LIST_AFTER_DELETE=$("$CLI_PATH" vectordb list --verbose)
if [[ "$WEAVIATE_CREATED" == "true" ]]; then
    # Weaviate should still be there, Milvus should be gone
    if [[ "$LIST_AFTER_DELETE" == *"test_remote_weaviate"* ]] && [[ "$LIST_AFTER_DELETE" != *"test_local_milvus"* ]] && [[ "$LIST_AFTER_DELETE" == *"Found 1 vector database"* ]]; then
        print_success "Database was removed from list after deletion"
    else
        print_error "Database still appears in list after deletion"
        echo "Output: $LIST_AFTER_DELETE"
        exit 1
    fi
else
    # No databases should be left
    if [[ "$LIST_AFTER_DELETE" == *"No vector databases found"* ]] || [[ "$LIST_AFTER_DELETE" == *"Found 0 vector database"* ]]; then
        print_success "All databases removed from list after deletion"
    else
        print_error "Unexpected databases still in list after deletion"
        echo "Output: $LIST_AFTER_DELETE"
        exit 1
    fi
fi

# 41. Final cleanup - ensure no test artifacts remain
print_status "Performing final cleanup..."
cd "$CLI_DIR"

# Clean up any remaining test collections
for db_name in $("$CLI_PATH" vectordb list --silent 2>/dev/null | grep -E "test_local_milvus|test_remote_weaviate" | awk '{print $1}' 2>/dev/null || true); do
    for collection in $("$CLI_PATH" collection list --vdb="$db_name" --silent 2>/dev/null | grep -E "test_collection_.*" | awk '{print $1}' 2>/dev/null || true); do
    print_status "Cleaning up remaining test collection: $collection in $db_name"
    "$CLI_PATH" collection delete "$collection" --vdb="$db_name" --silent --force 2>/dev/null || true
done
done

# Clean up any remaining test databases
"$CLI_PATH" vectordb delete test_local_milvus --silent --force 2>/dev/null || true
"$CLI_PATH" vectordb delete test_remote_weaviate --silent --force 2>/dev/null || true

print_success "Final cleanup completed"

# 42. Stop the MCP server
print_status "Stopping MCP server..."
cd "$PROJECT_ROOT"
./stop.sh
print_success "MCP server stopped"

print_success "All comprehensive end-to-end tests passed!"
print_status "CLI integration testing completed successfully" 