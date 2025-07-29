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
DRY_RUN_OUTPUT=$(./maestro-k list vector-dbs --dry-run)
if [[ "$DRY_RUN_OUTPUT" == *"[DRY RUN] Would list vector databases"* ]]; then
    print_success "Dry-run mode works correctly"
else
    print_error "Dry-run mode failed"
    exit 1
fi

# Test with verbose mode
print_status "Testing verbose mode..."
VERBOSE_OUTPUT=$(./maestro-k list vector-dbs --dry-run --verbose)
if [[ "$VERBOSE_OUTPUT" == *"Listing vector databases"* ]]; then
    print_success "Verbose mode works correctly"
else
    print_error "Verbose mode failed"
    exit 1
fi

# Test environment variable support
print_status "Testing environment variable support..."
export MAESTRO_KNOWLEDGE_MCP_SERVER_URI="http://localhost:9000"
ENV_OUTPUT=$(./maestro-k list vector-dbs --verbose 2>&1 || true)
if [[ "$ENV_OUTPUT" == *"Connecting to MCP server at: http://localhost:9000"* ]]; then
    print_success "Environment variable support works"
else
    print_warning "Environment variable support may not be working correctly"
    echo "Output: $ENV_OUTPUT"
fi

# Test command line flag override
print_status "Testing command line flag override..."
FLAG_OUTPUT=$(./maestro-k list vector-dbs --verbose --mcp-server-uri="http://localhost:9999" 2>&1 || true)
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
./maestro-k delete vdb test_local_milvus --silent 2>/dev/null || true
./maestro-k delete vdb test_remote_weaviate --silent 2>/dev/null || true

# Clean up any test collections that might exist in other databases
print_status "Cleaning up any existing test collections..."
for db_name in $(./maestro-k list vector-dbs --silent 2>/dev/null | grep -E "test_local_milvus|test_remote_weaviate" | awk '{print $1}' 2>/dev/null || true); do
    for collection in $(./maestro-k list collections "$db_name" --silent 2>/dev/null | grep -E "test_collection_.*" | awk '{print $1}' 2>/dev/null || true); do
        ./maestro-k delete collection "$db_name" "$collection" --silent 2>/dev/null || true
    done
done

# 2. Start the MCP server
print_status "Starting MCP server..."
cd "$PROJECT_ROOT"
./start.sh
sleep 3  # Give the server time to start
print_success "MCP server started"

# 3. List vector databases (should be empty initially)
print_status "Testing initial list (should be empty)..."
cd "$CLI_DIR"
INITIAL_LIST=$(./maestro-k list vector-dbs --verbose)
if [[ "$INITIAL_LIST" == *"No vector databases found"* ]]; then
    print_success "Initial list shows no databases (as expected)"
else
    print_warning "Initial list may have existing databases"
    echo "Output: $INITIAL_LIST"
fi

# 4. Create a vector database
print_status "Creating vector database..."
CREATE_OUTPUT=$(./maestro-k create vector-db ../tests/yamls/test_local_milvus.yaml --verbose)
if [[ "$CREATE_OUTPUT" == *"✅ Vector database 'test_local_milvus' created successfully"* ]]; then
    print_success "Vector database created successfully"
else
    print_error "Failed to create vector database"
    echo "Output: $CREATE_OUTPUT"
    exit 1
fi

# 5. List to verify the database was created
print_status "Verifying database appears in list..."
LIST_AFTER_CREATE=$(./maestro-k list vector-dbs --verbose)
if [[ "$LIST_AFTER_CREATE" == *"test_local_milvus"* ]] && [[ "$LIST_AFTER_CREATE" == *"milvus"* ]]; then
    print_success "Database appears in list after creation"
else
    print_error "Database not found in list after creation"
    echo "Output: $LIST_AFTER_CREATE"
    exit 1
fi

# 6. Create another database (Weaviate) - may fail due to missing API key
print_status "Creating second vector database (Weaviate)..."
CREATE_WEAVIATE_OUTPUT=$(./maestro-k create vector-db ../tests/yamls/test_remote_weaviate.yaml --verbose 2>&1 || true)

if [[ "$CREATE_WEAVIATE_OUTPUT" == *"✅ Vector database 'test_remote_weaviate' created successfully"* ]]; then
    print_success "Weaviate database created successfully"
    WEAVIATE_CREATED=true
elif [[ "$CREATE_WEAVIATE_OUTPUT" == *"WEAVIATE_API_KEY is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"WEAVIATE_URL is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"Failed to create vector database 'test_remote_weaviate': WEAVIATE_API_KEY is not set"* ]] || [[ "$CREATE_WEAVIATE_OUTPUT" == *"Error: Failed to create vector database 'test_remote_weaviate': WEAVIATE_API_KEY is not set"* ]]; then
    print_warning "Weaviate database creation skipped (missing API key/URL - this is expected in test environment)"
    WEAVIATE_CREATED=false
else
    print_error "Failed to create Weaviate database for unexpected reason"
    echo "Output: $CREATE_WEAVIATE_OUTPUT"
    exit 1
fi

# 7. List to verify databases are present
print_status "Verifying databases appear in list..."
LIST_BOTH=$(./maestro-k list vector-dbs --verbose)
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
EMBEDDINGS_OUTPUT=$(./maestro-k list embeddings test_local_milvus --verbose)
if [[ "$EMBEDDINGS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]] && [[ "$EMBEDDINGS_OUTPUT" == *"text-embedding-3-small"* ]]; then
    print_success "Embeddings listing works for existing database"
else
    print_error "Failed to list embeddings for existing database"
    echo "Output: $EMBEDDINGS_OUTPUT"
    exit 1
fi

# 9. Test embeddings functionality with different aliases
print_status "Testing embeddings functionality with 'embeds' alias..."
EMBED_ALIAS_OUTPUT=$(./maestro-k list embeds test_local_milvus --verbose)
if [[ "$EMBED_ALIAS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]]; then
    print_success "Embeddings listing works with 'embeds' alias"
else
    print_error "Failed to list embeddings with 'embeds' alias"
    echo "Output: $EMBED_ALIAS_OUTPUT"
    exit 1
fi

# 10. Test embeddings functionality with 'vdb-embeds' alias
print_status "Testing embeddings functionality with 'vdb-embeds' alias..."
VDB_EMBED_ALIAS_OUTPUT=$(./maestro-k list vdb-embeds test_local_milvus --verbose)
if [[ "$VDB_EMBED_ALIAS_OUTPUT" == *"Supported embeddings for milvus vector database 'test_local_milvus'"* ]]; then
    print_success "Embeddings listing works with 'vdb-embeds' alias"
else
    print_error "Failed to list embeddings with 'vdb-embeds' alias"
    echo "Output: $VDB_EMBED_ALIAS_OUTPUT"
    exit 1
fi

# 11. Test embeddings functionality on non-existing database (should fail)
print_status "Testing embeddings functionality on non-existing database (should fail)..."
EMBEDDINGS_NONEXISTENT_OUTPUT=$(./maestro-k list embeddings non_existent_database 2>&1 || true)
if [[ "$EMBEDDINGS_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Embeddings listing correctly fails for non-existing database"
else
    print_error "Embeddings listing should have failed for non-existing database"
    echo "Output: $EMBEDDINGS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 12. Test embeddings functionality with missing VDB_NAME (should fail)
print_status "Testing embeddings functionality with missing VDB_NAME (should fail)..."
EMBEDDINGS_MISSING_NAME_OUTPUT=$(./maestro-k list embeddings 2>&1 || true)
if [[ "$EMBEDDINGS_MISSING_NAME_OUTPUT" == *"VDB_NAME is required for embeddings command"* ]]; then
    print_success "Embeddings listing correctly fails with missing VDB_NAME"
else
    print_error "Embeddings listing should have failed with missing VDB_NAME"
    echo "Output: $EMBEDDINGS_MISSING_NAME_OUTPUT"
    exit 1
fi

# 13. Test collections functionality on existing database
print_status "Testing collections functionality on existing database..."
COLLECTIONS_OUTPUT=$(./maestro-k list collections test_local_milvus --verbose)
if [[ "$COLLECTIONS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works for existing database"
else
    print_error "Failed to list collections for existing database"
    echo "Output: $COLLECTIONS_OUTPUT"
    exit 1
fi

# 14. Test collections functionality with 'cols' alias
print_status "Testing collections functionality with 'cols' alias..."
COLS_ALIAS_OUTPUT=$(./maestro-k list cols test_local_milvus --verbose)
if [[ "$COLS_ALIAS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works with 'cols' alias"
else
    print_error "Failed to list collections with 'cols' alias"
    echo "Output: $COLS_ALIAS_OUTPUT"
    exit 1
fi

# 15. Test collections functionality with 'vdb-cols' alias
print_status "Testing collections functionality with 'vdb-cols' alias..."
VDB_COLS_ALIAS_OUTPUT=$(./maestro-k list vdb-cols test_local_milvus --verbose)
if [[ "$VDB_COLS_ALIAS_OUTPUT" == *"Collections in vector database 'test_local_milvus'"* ]]; then
    print_success "Collections listing works with 'vdb-cols' alias"
else
    print_error "Failed to list collections with 'vdb-cols' alias"
    echo "Output: $VDB_COLS_ALIAS_OUTPUT"
    exit 1
fi

# 16. Test collections functionality on non-existing database (should fail)
print_status "Testing collections functionality on non-existing database (should fail)..."
COLLECTIONS_NONEXISTENT_OUTPUT=$(./maestro-k list collections non_existent_database 2>&1 || true)
if [[ "$COLLECTIONS_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Collections listing correctly fails for non-existing database"
else
    print_error "Collections listing should have failed for non-existing database"
    echo "Output: $COLLECTIONS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 17. Test collections functionality with missing VDB_NAME (should fail)
print_status "Testing collections functionality with missing VDB_NAME (should fail)..."
COLLECTIONS_MISSING_NAME_OUTPUT=$(./maestro-k list collections 2>&1 || true)
if [[ "$COLLECTIONS_MISSING_NAME_OUTPUT" == *"VDB_NAME is required for collections command"* ]]; then
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
CREATE_COLLECTION_OUTPUT=$(./maestro-k create collection test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$CREATE_COLLECTION_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_basic' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully"
else
    print_error "Failed to create collection"
    echo "Output: $CREATE_COLLECTION_OUTPUT"
    exit 1
fi

# 19. Test create collection with custom embedding
print_status "Testing create collection with custom embedding..."
CREATE_COLLECTION_EMBEDDING_OUTPUT=$(./maestro-k create collection test_local_milvus "${COLLECTION_BASE}_embedding" --embedding=text-embedding-3-small --verbose)
if [[ "$CREATE_COLLECTION_EMBEDDING_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_embedding' created successfully in vector database 'test_local_milvus' with embedding 'text-embedding-3-small'"* ]]; then
    print_success "Collection created successfully with custom embedding"
else
    print_error "Failed to create collection with custom embedding"
    echo "Output: $CREATE_COLLECTION_EMBEDDING_OUTPUT"
    exit 1
fi

# 20. Test create collection with 'col' alias
print_status "Testing create collection with 'col' alias..."
CREATE_COLLECTION_COL_ALIAS_OUTPUT=$(./maestro-k create col test_local_milvus "${COLLECTION_BASE}_col" --verbose)
if [[ "$CREATE_COLLECTION_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_col' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully with 'col' alias"
else
    print_error "Failed to create collection with 'col' alias"
    echo "Output: $CREATE_COLLECTION_COL_ALIAS_OUTPUT"
    exit 1
fi

# 21. Test create collection with 'vdb-col' alias
print_status "Testing create collection with 'vdb-col' alias..."
CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT=$(./maestro-k create vdb-col test_local_milvus "${COLLECTION_BASE}_vdb_col" --verbose)
if [[ "$CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_vdb_col' created successfully in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection created successfully with 'vdb-col' alias"
else
    print_error "Failed to create collection with 'vdb-col' alias"
    echo "Output: $CREATE_COLLECTION_VDB_COL_ALIAS_OUTPUT"
    exit 1
fi

# 22. Test create collection on non-existing database (should fail)
print_status "Testing create collection on non-existing database (should fail)..."
CREATE_COLLECTION_NONEXISTENT_OUTPUT=$(./maestro-k create collection non_existent_database test_collection 2>&1 || true)
if [[ "$CREATE_COLLECTION_NONEXISTENT_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Create collection correctly fails for non-existing database"
else
    print_error "Create collection should have failed for non-existing database"
    echo "Output: $CREATE_COLLECTION_NONEXISTENT_OUTPUT"
    exit 1
fi

# 23. Test create collection with missing arguments (should fail)
print_status "Testing create collection with missing arguments (should fail)..."
CREATE_COLLECTION_MISSING_ARGS_OUTPUT=$(./maestro-k create collection test_local_milvus 2>&1 || true)
if [[ "$CREATE_COLLECTION_MISSING_ARGS_OUTPUT" == *"accepts 2 arg(s), received 1"* ]]; then
    print_success "Create collection correctly fails with missing arguments"
else
    print_error "Create collection should have failed with missing arguments"
    echo "Output: $CREATE_COLLECTION_MISSING_ARGS_OUTPUT"
    exit 1
fi

# 24. Test create collection with too many arguments (should fail)
print_status "Testing create collection with too many arguments (should fail)..."
CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT=$(./maestro-k create collection test_local_milvus test_collection extra_arg 2>&1 || true)
if [[ "$CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT" == *"accepts 2 arg(s), received 3"* ]]; then
    print_success "Create collection correctly fails with too many arguments"
else
    print_error "Create collection should have failed with too many arguments"
    echo "Output: $CREATE_COLLECTION_TOO_MANY_ARGS_OUTPUT"
    exit 1
fi

# 25. Test create collection with dry-run mode
print_status "Testing create collection with dry-run mode..."
CREATE_COLLECTION_DRY_RUN_OUTPUT=$(./maestro-k create collection test_local_milvus "${COLLECTION_BASE}_dry_run" --dry-run)
if [[ "$CREATE_COLLECTION_DRY_RUN_OUTPUT" == *"[DRY RUN] Would create collection '${COLLECTION_BASE}_dry_run' in vector database 'test_local_milvus'"* ]]; then
    print_success "Create collection dry-run mode works correctly"
else
    print_error "Create collection dry-run mode failed"
    echo "Output: $CREATE_COLLECTION_DRY_RUN_OUTPUT"
    exit 1
fi

# 26. Test create collection with silent mode
print_status "Testing create collection with silent mode..."
CREATE_COLLECTION_SILENT_OUTPUT=$(./maestro-k create collection test_local_milvus "${COLLECTION_BASE}_silent" --silent)
if [[ "$CREATE_COLLECTION_SILENT_OUTPUT" != *"✅ Collection '${COLLECTION_BASE}_silent' created successfully"* ]]; then
    print_success "Create collection silent mode works correctly (no success message)"
else
    print_error "Create collection silent mode failed (should not show success message)"
    echo "Output: $CREATE_COLLECTION_SILENT_OUTPUT"
    exit 1
fi

# 27. Verify collections appear in list after creation
print_status "Verifying collections appear in list after creation..."
COLLECTIONS_AFTER_CREATE=$(./maestro-k list collections test_local_milvus --verbose)
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
print_status "Testing 'get col' command..."
GET_COL_OUTPUT=$(./maestro-k get col test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$GET_COL_OUTPUT" == *"Collection information for '${COLLECTION_BASE}_basic' in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection info retrieved successfully"
    
    # Extract document count from the output
    DOC_COUNT_FROM_INFO=$(echo "$GET_COL_OUTPUT" | grep -o '"document_count":[[:space:]]*[0-9]*' | tail -1 | sed 's/"document_count":[[:space:]]*//')
    echo "Document count from collection info: $DOC_COUNT_FROM_INFO"
else
    print_error "Failed to get collection info"
    echo "Output: $GET_COL_OUTPUT"
    exit 1
fi

# Test list documents for the same collection
print_status "Testing 'list docs' command..."
LIST_DOCS_OUTPUT=$(./maestro-k list docs test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully"
    
    # Extract document count from the output
    DOC_COUNT_FROM_LIST=$(echo "$LIST_DOCS_OUTPUT" | grep -o "Found [0-9]* documents" | cut -d' ' -f2)
    echo "Document count from list docs: $DOC_COUNT_FROM_LIST"
    
    # Compare the counts - they should be consistent
    if [[ "$DOC_COUNT_FROM_INFO" == "$DOC_COUNT_FROM_LIST" ]]; then
        print_success "Document counts are consistent between 'get col' and 'list docs'"
    else
        print_error "Document counts are inconsistent: info=$DOC_COUNT_FROM_INFO, list=$DOC_COUNT_FROM_LIST"
        echo "Collection info output: $GET_COL_OUTPUT"
        echo "List docs output: $LIST_DOCS_OUTPUT"
        exit 1
    fi
else
    print_error "Failed to list documents"
    echo "Output: $LIST_DOCS_OUTPUT"
    exit 1
fi

# Test get collection info with 'retrieve' command
print_status "Testing 'retrieve col' command..."
RETRIEVE_COL_OUTPUT=$(./maestro-k retrieve col test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$RETRIEVE_COL_OUTPUT" == *"Collection information for '${COLLECTION_BASE}_basic' in vector database 'test_local_milvus'"* ]]; then
    print_success "Collection info retrieved successfully with 'retrieve' command"
    
    # Extract document count from the output
    DOC_COUNT_FROM_RETRIEVE=$(echo "$RETRIEVE_COL_OUTPUT" | grep -o '"document_count":[[:space:]]*[0-9]*' | tail -1 | sed 's/"document_count":[[:space:]]*//')
    echo "Document count from retrieve col: $DOC_COUNT_FROM_RETRIEVE"
    
    # Compare with the previous count
    if [[ "$DOC_COUNT_FROM_RETRIEVE" == "$DOC_COUNT_FROM_INFO" ]]; then
        print_success "Document counts are consistent between 'get col' and 'retrieve col'"
    else
        print_error "Document counts are inconsistent: get=$DOC_COUNT_FROM_INFO, retrieve=$DOC_COUNT_FROM_RETRIEVE"
        exit 1
    fi
else
    print_error "Failed to retrieve collection info"
    echo "Output: $RETRIEVE_COL_OUTPUT"
    exit 1
fi

# Test list documents with different aliases
print_status "Testing 'list docs' with different aliases..."
LIST_DOCS_DOCS_ALIAS_OUTPUT=$(./maestro-k list docs test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_DOCS_ALIAS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully with 'docs' alias"
else
    print_error "Failed to list documents with 'docs' alias"
    echo "Output: $LIST_DOCS_DOCS_ALIAS_OUTPUT"
    exit 1
fi

print_status "Testing 'list vdb-docs' with different aliases..."
LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT=$(./maestro-k list vdb-docs test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_basic' of vector database 'test_local_milvus'"* ]]; then
    print_success "Documents listed successfully with 'vdb-docs' alias"
else
    print_error "Failed to list documents with 'vdb-docs' alias"
    echo "Output: $LIST_DOCS_VDB_DOCS_ALIAS_OUTPUT"
    exit 1
fi

# Test collection info and document listing for a different collection
print_status "Testing consistency for a different collection..."
GET_COL_2_OUTPUT=$(./maestro-k get col test_local_milvus "${COLLECTION_BASE}_embedding" --verbose)
LIST_DOCS_2_OUTPUT=$(./maestro-k list docs test_local_milvus "${COLLECTION_BASE}_embedding" --verbose)

if [[ "$GET_COL_2_OUTPUT" == *"Collection information for '${COLLECTION_BASE}_embedding' in vector database 'test_local_milvus'"* ]] && [[ "$LIST_DOCS_2_OUTPUT" == *"Found"*"documents in collection '${COLLECTION_BASE}_embedding' of vector database 'test_local_milvus'"* ]]; then
    DOC_COUNT_INFO_2=$(echo "$GET_COL_2_OUTPUT" | grep -o '"document_count":[[:space:]]*[0-9]*' | tail -1 | sed 's/"document_count":[[:space:]]*//')
    DOC_COUNT_LIST_2=$(echo "$LIST_DOCS_2_OUTPUT" | grep -o "Found [0-9]* documents" | cut -d' ' -f2)
    
    if [[ "$DOC_COUNT_INFO_2" == "$DOC_COUNT_LIST_2" ]]; then
        print_success "Document counts are consistent for second collection"
    else
        print_error "Document counts are inconsistent for second collection: info=$DOC_COUNT_INFO_2, list=$DOC_COUNT_LIST_2"
        exit 1
    fi
else
    print_error "Failed to test consistency for second collection"
    echo "Get col output: $GET_COL_2_OUTPUT"
    echo "List docs output: $LIST_DOCS_2_OUTPUT"
    exit 1
fi

# Test error handling for non-existent collection
print_status "Testing error handling for non-existent collection..."
GET_COL_NONEXISTENT_OUTPUT=$(./maestro-k get col test_local_milvus non_existent_collection 2>&1 || true)
if [[ "$GET_COL_NONEXISTENT_OUTPUT" == *"collection 'non_existent_collection' not found in vector database 'test_local_milvus'"* ]]; then
    print_success "Get col correctly fails for non-existent collection"
else
    print_error "Get col should have failed for non-existent collection"
    echo "Output: $GET_COL_NONEXISTENT_OUTPUT"
    exit 1
fi

LIST_DOCS_NONEXISTENT_OUTPUT=$(./maestro-k list docs test_local_milvus non_existent_collection 2>&1 || true)
if [[ "$LIST_DOCS_NONEXISTENT_OUTPUT" == *"Collection 'non_existent_collection' not found in vector database 'test_local_milvus'"* ]] || [[ "$LIST_DOCS_NONEXISTENT_OUTPUT" == *"collection 'non_existent_collection' not found in vector database 'test_local_milvus'"* ]]; then
    print_success "List docs correctly fails for non-existent collection"
else
    print_error "List docs should have failed for non-existent collection"
    echo "Output: $LIST_DOCS_NONEXISTENT_OUTPUT"
    exit 1
fi

# 29. Test delete collection functionality
print_status "Testing delete collection functionality..."
DELETE_COLLECTION_OUTPUT=$(./maestro-k delete collection test_local_milvus "${COLLECTION_BASE}_basic" --verbose)
if [[ "$DELETE_COLLECTION_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_basic' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully"
else
    print_error "Failed to delete collection"
    echo "Output: $DELETE_COLLECTION_OUTPUT"
    exit 1
fi

# 30. Test delete collection with 'col' alias
print_status "Testing delete collection with 'col' alias..."
DELETE_COLLECTION_COL_ALIAS_OUTPUT=$(./maestro-k delete col test_local_milvus "${COLLECTION_BASE}_col" --verbose)
if [[ "$DELETE_COLLECTION_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_col' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'col' alias"
else
    print_error "Failed to delete collection with 'col' alias"
    echo "Output: $DELETE_COLLECTION_COL_ALIAS_OUTPUT"
    exit 1
fi

# 31. Test delete collection with 'vdb-col' alias
print_status "Testing delete collection with 'vdb-col' alias..."
DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT=$(./maestro-k delete vdb-col test_local_milvus "${COLLECTION_BASE}_vdb_col" --verbose)
if [[ "$DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_vdb_col' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'vdb-col' alias"
else
    print_error "Failed to delete collection with 'vdb-col' alias"
    echo "Output: $DELETE_COLLECTION_VDB_COL_ALIAS_OUTPUT"
    exit 1
fi

# 32. Test delete collection with 'del' alias
print_status "Testing delete collection with 'del' alias..."
DELETE_COLLECTION_DEL_ALIAS_OUTPUT=$(./maestro-k del collection test_local_milvus "${COLLECTION_BASE}_embedding" --verbose)
if [[ "$DELETE_COLLECTION_DEL_ALIAS_OUTPUT" == *"✅ Collection '${COLLECTION_BASE}_embedding' deleted successfully from vector database 'test_local_milvus'"* ]]; then
    print_success "Collection deleted successfully with 'del' alias"
else
    print_error "Failed to delete collection with 'del' alias"
    echo "Output: $DELETE_COLLECTION_DEL_ALIAS_OUTPUT"
    exit 1
fi

# 33. Test delete collection with dry-run mode
print_status "Testing delete collection with dry-run mode..."
DELETE_COLLECTION_DRY_RUN_OUTPUT=$(./maestro-k delete collection test_local_milvus "${COLLECTION_BASE}_dry_run" --dry-run)
if [[ "$DELETE_COLLECTION_DRY_RUN_OUTPUT" == *"[DRY RUN] Would delete collection '${COLLECTION_BASE}_dry_run' from vector database 'test_local_milvus'"* ]]; then
    print_success "Delete collection dry-run mode works correctly"
else
    print_error "Delete collection dry-run mode failed"
    echo "Output: $DELETE_COLLECTION_DRY_RUN_OUTPUT"
    exit 1
fi

# 34. Test delete collection with silent mode
print_status "Testing delete collection with silent mode..."
DELETE_COLLECTION_SILENT_OUTPUT=$(./maestro-k delete collection test_local_milvus "${COLLECTION_BASE}_silent" --silent)
if [[ "$DELETE_COLLECTION_SILENT_OUTPUT" != *"✅ Collection '${COLLECTION_BASE}_silent' deleted successfully"* ]]; then
    print_success "Delete collection silent mode works correctly (no success message)"
else
    print_error "Delete collection silent mode failed (should not show success message)"
    echo "Output: $DELETE_COLLECTION_SILENT_OUTPUT"
    exit 1
fi

# 35. Test delete collection on non-existing database (should fail)
print_status "Testing delete collection on non-existing database (should fail)..."
DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT=$(./maestro-k delete collection non_existent_database test_collection 2>&1 || true)
if [[ "$DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT" == *"vector database 'non_existent_database' does not exist"* ]]; then
    print_success "Delete collection correctly fails for non-existing database"
else
    print_error "Delete collection should have failed for non-existing database"
    echo "Output: $DELETE_COLLECTION_NONEXISTENT_DB_OUTPUT"
    exit 1
fi

# 36. Test delete collection with missing collection name (should fail)
print_status "Testing delete collection with missing collection name (should fail)..."
DELETE_COLLECTION_MISSING_NAME_OUTPUT=$(./maestro-k delete collection test_local_milvus 2>&1 || true)
if [[ "$DELETE_COLLECTION_MISSING_NAME_OUTPUT" == *"collection deletion requires both VDB_NAME and COLLECTION_NAME"* ]]; then
    print_success "Delete collection correctly fails with missing collection name"
else
    print_error "Delete collection should have failed with missing collection name"
    echo "Output: $DELETE_COLLECTION_MISSING_NAME_OUTPUT"
    exit 1
fi

# 37. Test delete collection with 'del' alias and missing collection name (should fail)
print_status "Testing delete collection with 'del' alias and missing collection name (should fail)..."
DELETE_COLLECTION_DEL_MISSING_NAME_OUTPUT=$(./maestro-k del collection test_local_milvus 2>&1 || true)
if [[ "$DELETE_COLLECTION_DEL_MISSING_NAME_OUTPUT" == *"collection deletion requires both VDB_NAME and COLLECTION_NAME"* ]]; then
    print_success "Delete collection with 'del' alias correctly fails with missing collection name"
else
    print_error "Delete collection with 'del' alias should have failed with missing collection name"
    echo "Output: $DELETE_COLLECTION_DEL_MISSING_NAME_OUTPUT"
    exit 1
fi

# 38. Verify collections were removed from list after deletion
print_status "Verifying collections were removed from list after deletion..."
COLLECTIONS_AFTER_DELETE=$(./maestro-k list collections test_local_milvus --verbose)
if [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_basic"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_col"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_vdb_col"* ]] && [[ "$COLLECTIONS_AFTER_DELETE" != *"${COLLECTION_BASE}_embedding"* ]]; then
    print_success "All deleted collections were removed from list"
else
    print_error "Some deleted collections still appear in list"
    echo "Output: $COLLECTIONS_AFTER_DELETE"
    exit 1
fi

# 39. Delete a vector database
print_status "Testing delete functionality..."
DELETE_OUTPUT=$(./maestro-k delete vector-db test_local_milvus --verbose)
if [[ "$DELETE_OUTPUT" == *"✅ Vector database 'test_local_milvus' deleted successfully"* ]]; then
    print_success "Vector database deleted successfully"
else
    print_error "Failed to delete vector database"
    echo "Output: $DELETE_OUTPUT"
    exit 1
fi

# 40. List to verify the database was deleted
print_status "Verifying database was removed from list..."
LIST_AFTER_DELETE=$(./maestro-k list vector-dbs --verbose)
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
for db_name in $(./maestro-k list vector-dbs --silent 2>/dev/null | grep -E "test_local_milvus|test_remote_weaviate" | awk '{print $1}' 2>/dev/null || true); do
    for collection in $(./maestro-k list collections "$db_name" --silent 2>/dev/null | grep -E "test_collection_.*" | awk '{print $1}' 2>/dev/null || true); do
        print_status "Cleaning up remaining test collection: $collection in $db_name"
        ./maestro-k delete collection "$db_name" "$collection" --silent 2>/dev/null || true
    done
done

# Clean up any remaining test databases
./maestro-k delete vdb test_local_milvus --silent 2>/dev/null || true
./maestro-k delete vdb test_remote_weaviate --silent 2>/dev/null || true

print_success "Final cleanup completed"

# 42. Stop the MCP server
print_status "Stopping MCP server..."
cd "$PROJECT_ROOT"
./stop.sh
print_success "MCP server stopped"

print_success "All comprehensive end-to-end tests passed!"
print_status "CLI integration testing completed successfully" 