#!/bin/bash

# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

# Maestro Knowledge End-to-End Testing Script
#
# NOTE: Document creation commands currently use --dry-run flags to avoid embedding API calls
#       due to vector dimension mismatch issues with open-source embedding models.
#       See: https://github.com/AI4quantum/maestro-knowledge/issues/8
#       
# TODO: Remove --dry-run flags from document creation commands after issue #8 is resolved
#       to enable full end-to-end testing of document creation functionality.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_YAML="$PROJECT_ROOT/tests/yamls/test_local_milvus.yaml"

# Find CLI path
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
        break
    fi
done

# If not found in relative paths, try PATH
if [ -z "$CLI_PATH" ]; then
    if command -v maestro-k >/dev/null 2>&1; then
        CLI_PATH="maestro-k"
    elif command -v maestro >/dev/null 2>&1; then
        # Verify this is the correct maestro CLI by checking if it has vectordb command
        if maestro vectordb --help >/dev/null 2>&1; then
            CLI_PATH="maestro"
        fi
    fi
fi

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}[E2E]${NC} $1"
}

print_command() {
    echo -e "${CYAN}[CMD]${NC} $1"
}

# Function to run a command and show output
run_command() {
    local cmd="$1"
    local description="$2"
    
    print_command "$cmd"
    echo "--- $description ---"
    if eval "$cmd"; then
        print_success "✓ $description completed"
    else
        print_error "✗ $description failed"
        return 1
    fi
    echo ""
}

# Function to show help
show_help() {
    echo "Maestro Knowledge End-to-End Testing Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  help     - Show this help message"
    echo "  fast     - Run fast end-to-end test workflow"
    echo "  complete - Run complete end-to-end test workflow with error testing"
    echo "  query    - Run query end-to-end test workflow"
    echo "  all      - Run fast, complete, and query workflows"
    echo ""
    echo "Examples:"
    echo "  $0 help"
    echo "  $0 fast"
    echo "  $0 complete"
    echo "  $0 query"
    echo "  $0 all"
    echo ""
    echo "Note: This script requires the MCP server to be running."
    echo "      Run './start.sh' before executing this script."
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check if CLI exists
    if [ -z "$CLI_PATH" ]; then
        print_error "maestro CLI not found in PATH or common relative locations"
        print_error "Please ensure the maestro CLI is built and available:"
        print_error "1. Build the CLI: cd /path/to/maestro-cli && ./build.sh"
        print_error "2. Add it to your PATH, or"
        print_error "3. Place it in a relative path from this script"
        exit 1
    fi
    
    # Check if test YAML exists
    if [ ! -f "$TEST_YAML" ]; then
        print_error "Test YAML file not found at $TEST_YAML"
        exit 1
    fi
    
    # Check if MCP server is running
    if [ ! -f "$PROJECT_ROOT/mcp_server.pid" ]; then
        print_error "MCP server is not running"
        print_error "Please start the MCP server first: ./start.sh"
        exit 1
    fi
    
    local pid=$(cat "$PROJECT_ROOT/mcp_server.pid")
    if ! ps -p "$pid" > /dev/null 2>&1; then
        print_error "MCP server process not found (PID: $pid)"
        print_error "Please start the MCP server first: ./start.sh"
        exit 1
    fi
    
    print_success "✓ All prerequisites met"
    echo ""
}

# Function to cleanup existing test resources
cleanup_test_resources() {
    print_header "Cleaning up existing test resources..."
    
    local vdb_name="test_local_milvus"
    
    # Check if vector database exists and delete it
    if "$CLI_PATH" list vdbs 2>/dev/null | grep -q "$vdb_name"; then
        print_status "Found existing vector database '$vdb_name', cleaning up..."
        
        # Get all collections and delete test-related ones
        print_status "Cleaning up test collections..."
        local collections_output=$("$CLI_PATH" list collections $vdb_name 2>/dev/null || echo "[]")
        
        # Delete collections that match test patterns
        echo "$collections_output" | grep -o '"[^"]*"' | tr -d '"' | while read -r collection; do
            if [[ "$collection" == test_* ]] || [[ "$collection" == ExampleCollection ]]; then
                print_status "Deleting collection: $collection"
                "$CLI_PATH" delete collection $vdb_name "$collection" 2>/dev/null || true
            fi
        done
        
        # Delete vector database
        run_command ""$CLI_PATH" delete vdb $vdb_name" "Deleting existing vector database"
    else
        print_status "No existing test vector database found"
    fi
    
    echo ""
}

# Function to run fast workflow
run_fast_workflow() {
    print_header "Running FAST end-to-end workflow"
    echo "This workflow tests basic functionality with a single collection and document."
    echo ""
    
    check_prerequisites
    cleanup_test_resources
    
    local vdb_name="test_local_milvus"
    local collection_name="e2e_test_collection"
    
    # Step 1: Create vector database
    run_command ""$CLI_PATH" create vdb $TEST_YAML" "Creating vector database from YAML"
    
    # Step 2: List embeddings
    run_command ""$CLI_PATH" list embeddings $vdb_name" "Listing available embeddings"
    
    # Step 3: Create collection
    run_command ""$CLI_PATH" create collection $vdb_name $collection_name" "Creating collection"
    
    # Step 4: List collections
    run_command ""$CLI_PATH" list collections $vdb_name" "Listing collections"
    
    # Step 5: Create a simple document (using echo to create content)
    local doc_content="This is a test document for end-to-end testing."
    local doc_file="/tmp/test_document.txt"
    echo "$doc_content" > "$doc_file"
    
    print_command "echo '$doc_content' > $doc_file"
    print_success "✓ Created test document"
    
    # Step 6: Create document using create command (dry-run)
    # TODO: Remove --dry-run flag after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    run_command ""$CLI_PATH" create document $vdb_name $collection_name test_doc --file-name=$doc_file --dry-run" "Creating document using create command (dry-run)"
    
    # Step 7: List documents to verify creation (will be empty in dry-run)
    run_command ""$CLI_PATH" list documents $vdb_name $collection_name" "Listing documents after creation"
    
    # Step 8: Create another document using write command (dry-run)
    local doc2_content="This is another test document for end-to-end testing."
    local doc2_file="/tmp/test_document_2.txt"
    echo "$doc2_content" > "$doc2_file"
    
    print_command "echo '$doc2_content' > $doc2_file"
    print_success "✓ Created second test document"
    
    # TODO: Remove --dry-run flag after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    run_command ""$CLI_PATH" write document $vdb_name $collection_name test_doc_2 --file-name=$doc2_file --dry-run" "Creating document using write command (dry-run)"
    
    # Step 9: Test command aliases (dry-run)
    local doc3_content="This is a test document using command aliases."
    local doc3_file="/tmp/test_document_3.txt"
    echo "$doc3_content" > "$doc3_file"
    
    print_command "echo '$doc3_content' > $doc3_file"
    print_success "✓ Created third test document"
    
    # TODO: Remove --dry-run flags after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    run_command ""$CLI_PATH" create doc $vdb_name $collection_name test_doc_3 --file-name=$doc3_file --dry-run" "Creating document using 'create doc' alias (dry-run)"
    run_command ""$CLI_PATH" write vdb-doc $vdb_name $collection_name test_doc_4 --doc-file-name=$doc3_file --dry-run" "Creating document using 'write vdb-doc' alias with doc-file-name flag (dry-run)"
    
    # Step 10: List documents to verify all documents (will be empty in dry-run)
    run_command ""$CLI_PATH" list documents $vdb_name $collection_name" "Listing documents after all creations"
    
    # Step 11: Test document deletion (dry-run since documents weren't actually created)
    print_header "Testing document deletion..."
    run_command ""$CLI_PATH" delete document $vdb_name $collection_name test_doc --dry-run" "Deleting document using delete command (dry-run)"
    run_command ""$CLI_PATH" del doc $vdb_name $collection_name test_doc_2 --dry-run" "Deleting document using del doc alias (dry-run)"
    run_command ""$CLI_PATH" delete vdb-doc $vdb_name $collection_name test_doc_3 --dry-run" "Deleting document using delete vdb-doc alias (dry-run)"
    
    # Step 12: Test document deletion error handling - try to delete non-existent document
    print_command ""$CLI_PATH" delete document $vdb_name $collection_name non_existent_doc --dry-run"
    echo "--- Attempting to delete non-existent document (dry-run) ---"
    if "$CLI_PATH" delete document $vdb_name $collection_name non_existent_doc --dry-run 2>&1; then
        print_success "✓ Dry-run mode correctly handles non-existent document deletion"
    else
        print_error "✗ Dry-run mode should handle non-existent document gracefully"
        return 1
    fi
    echo ""
    
    # Step 13: Delete collection
    run_command ""$CLI_PATH" delete collection $vdb_name $collection_name" "Deleting collection"
    
    # Step 14: Delete vector database
    run_command ""$CLI_PATH" delete vdb $vdb_name" "Deleting vector database"
    
    # Cleanup
    rm -f "$doc_file" "$doc2_file" "$doc3_file"
    
    print_success "✓ FAST workflow completed successfully!"
    echo ""
}

# Function to run complete workflow
run_complete_workflow() {
    print_header "Running COMPLETE end-to-end workflow"
    echo "This workflow tests advanced functionality with multiple collections and error handling."
    echo ""
    
    check_prerequisites
    cleanup_test_resources
    
    local vdb_name="test_local_milvus"
    local collection1="e2e_test_collection_1"
    local collection2="e2e_test_collection_2"
    local non_existent_collection="non_existent_collection"
    
    # Step 1: Create vector database
    run_command ""$CLI_PATH" create vdb $TEST_YAML" "Creating vector database from YAML"
    
    # Step 2: List embeddings
    run_command ""$CLI_PATH" list embeddings $vdb_name" "Listing available embeddings"
    
    # Step 3: Create first collection
    run_command ""$CLI_PATH" create collection $vdb_name $collection1" "Creating first collection"
    
    # Step 4: Create second collection
    run_command ""$CLI_PATH" create collection $vdb_name $collection2" "Creating second collection"
    
    # Step 5: List collections
    run_command ""$CLI_PATH" list collections $vdb_name" "Listing collections"
    
    # Step 6: Create test documents
    local doc1_content="This is test document 1 for collection 1."
    local doc2_content="This is test document 2 for collection 2."
    local doc3_content="This is test document 3 for collection 1 with custom embedding."
    local doc1_file="/tmp/test_document_1.txt"
    local doc2_file="/tmp/test_document_2.txt"
    local doc3_file="/tmp/test_document_3.txt"
    
    echo "$doc1_content" > "$doc1_file"
    echo "$doc2_content" > "$doc2_file"
    echo "$doc3_content" > "$doc3_file"
    
    print_command "echo '$doc1_content' > $doc1_file"
    print_command "echo '$doc2_content' > $doc2_file"
    print_command "echo '$doc3_content' > $doc3_file"
    print_success "✓ Created test documents"
    
    # Step 7: Create documents using create command (dry-run)
    # TODO: Remove --dry-run flags after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    run_command ""$CLI_PATH" create document $vdb_name $collection1 test_doc_1 --file-name=$doc1_file --dry-run" "Creating document 1 using create command (dry-run)"
    run_command ""$CLI_PATH" create document $vdb_name $collection2 test_doc_2 --file-name=$doc2_file --dry-run" "Creating document 2 using create command (dry-run)"
    
    # Step 8: Create document with custom embedding using write command (dry-run)
    # TODO: Remove --dry-run flag after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    run_command ""$CLI_PATH" write document $vdb_name $collection1 test_doc_3 --file-name=$doc3_file --embed=text-embedding-3-small --dry-run" "Creating document 3 with custom embedding using write command (dry-run)"
    
    # Step 9: List documents to verify creation (will be empty in dry-run)
    run_command ""$CLI_PATH" list documents $vdb_name $collection1" "Listing documents in collection 1"
    run_command ""$CLI_PATH" list documents $vdb_name $collection2" "Listing documents in collection 2"
    
    # Step 10: Test error handling - try to delete non-existent collection
    print_header "Testing error handling..."
    print_command ""$CLI_PATH" delete collection $vdb_name $non_existent_collection"
    echo "--- Attempting to delete non-existent collection ---"
    if ! "$CLI_PATH" delete collection $vdb_name $non_existent_collection 2>&1; then
        print_success "✓ Correctly failed to delete non-existent collection"
    else
        print_error "✗ Should have failed to delete non-existent collection"
        return 1
    fi
    echo ""
    
    # Step 11: Test document error handling - try to create document with non-existent file
    print_header "Testing document error handling..."
    # TODO: Remove --dry-run flag after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    print_command ""$CLI_PATH" create document $vdb_name $collection1 test_error_doc --file-name=/tmp/non_existent_file.txt --dry-run"
    echo "--- Attempting to create document with non-existent file (dry-run) ---"
    if ! "$CLI_PATH" create document $vdb_name $collection1 test_error_doc --file-name=/tmp/non_existent_file.txt --dry-run 2>&1; then
        print_success "✓ Correctly failed to create document with non-existent file"
    else
        print_error "✗ Should have failed to create document with non-existent file"
        return 1
    fi
    echo ""
    
    # Step 12: Test document error handling - try to create document with duplicate name (dry-run mode doesn't check for duplicates)
    # TODO: Remove --dry-run flag after https://github.com/AI4quantum/maestro-knowledge/issues/8 is resolved
    print_command ""$CLI_PATH" create document $vdb_name $collection1 test_doc_1 --file-name=$doc1_file --dry-run"
    echo "--- Attempting to create document with duplicate name (dry-run) ---"
    if "$CLI_PATH" create document $vdb_name $collection1 test_doc_1 --file-name=$doc1_file --dry-run 2>&1; then
        print_success "✓ Correctly allowed duplicate document creation in dry-run mode"
    else
        print_error "✗ Should have allowed duplicate document creation in dry-run mode"
        return 1
    fi
    echo ""
    
    # Step 13: Test document deletion (dry-run since documents weren't actually created)
    print_header "Testing document deletion..."
    run_command ""$CLI_PATH" delete document $vdb_name $collection1 test_doc_1 --dry-run" "Deleting document 1 using delete command (dry-run)"
    run_command ""$CLI_PATH" del doc $vdb_name $collection2 test_doc_2 --dry-run" "Deleting document 2 using del doc alias (dry-run)"
    run_command ""$CLI_PATH" delete vdb-doc $vdb_name $collection1 test_doc_3 --dry-run" "Deleting document 3 using delete vdb-doc alias (dry-run)"
    
    # Step 14: Test document deletion error handling - try to delete non-existent document
    print_command ""$CLI_PATH" delete document $vdb_name $collection1 non_existent_doc --dry-run"
    echo "--- Attempting to delete non-existent document (dry-run) ---"
    if ! "$CLI_PATH" delete document $vdb_name $collection1 non_existent_doc --dry-run 2>&1; then
        print_success "✓ Correctly failed to delete non-existent document"
    else
        print_error "✗ Should have failed to delete non-existent document"
        return 1
    fi
    echo ""
    
    # Step 15: Delete collections
    run_command ""$CLI_PATH" delete collection $vdb_name $collection1" "Deleting first collection"
    run_command ""$CLI_PATH" delete collection $vdb_name $collection2" "Deleting second collection"
    
    # Step 16: Delete vector database
    run_command ""$CLI_PATH" delete vdb $vdb_name" "Deleting vector database"
    
    # Cleanup
    rm -f "$doc1_file" "$doc2_file" "$doc3_file"
    
    print_success "✓ COMPLETE workflow completed successfully!"
    echo ""
}

# Function to run query workflow (query CLI, MCP, Python/Go tests)
run_query_workflow() {
    print_header "Running QUERY end-to-end workflow"
    echo "This workflow tests query CLI, MCP server, and Python/Go query tests."
    echo ""

    # Check prerequisites
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    if ! command -v curl >/dev/null 2>&1; then
        print_error "curl is required but not installed"
        exit 1
    fi
    if ! command -v ""$CLI_PATH"" &> /dev/null; then
        print_error "maestro-k CLI not found in PATH"
        print_error "Please install the maestro CLI from: AI4quantum/maestro-cli"
        print_error "Make sure the maestro-k binary is available in your PATH"
        exit 1
    fi

    # CLI query help
    print_status "Test: CLI query command help"
    if ""$CLI_PATH"" query --help >/dev/null 2>&1; then
        print_success "CLI query help command works"
    else
        print_error "CLI query help command failed"
        exit 1
    fi

    # CLI query vdb help
    print_status "Test: CLI query vdb command help"
    if ""$CLI_PATH"" query vdb --help >/dev/null 2>&1; then
        print_success "CLI query vdb help command works"
    else
        print_error "CLI query vdb help command failed"
        exit 1
    fi

    # CLI query dry-run
    print_status "Test: CLI query command with dry-run"
    output=$(""$CLI_PATH"" query test-db "test query" --dry-run 2>&1)
    if echo "$output" | grep -q "\[DRY RUN\]"; then
        print_success "CLI query dry-run works"
    else
        print_error "CLI query dry-run failed"
        echo "Output: $output"
        exit 1
    fi

    # CLI query with doc-limit
    print_status "Test: CLI query command with doc-limit"
    output=$(""$CLI_PATH"" query test-db "test query" --doc-limit 10 --dry-run 2>&1)
    if echo "$output" | grep -q "\[DRY RUN\]"; then
        print_success "CLI query with doc-limit works"
    else
        print_error "CLI query with doc-limit failed"
        echo "Output: $output"
        exit 1
    fi

    # CLI query with special characters
    print_status "Test: CLI query with special characters"
    special_queries=(
        "What's the deal with API endpoints? (v2.0)"
        "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        "Unicode: αβγδε ζηθικλμν ξοπρστ υφχψω"
    )
    for query in "${special_queries[@]}"; do
        output=$(""$CLI_PATH"" query test-db "$query" --dry-run 2>&1)
        if echo "$output" | grep -q "\[DRY RUN\]"; then
            print_success "Query with special characters works: ${query:0:30}..."
        else
            print_error "Query with special characters failed: ${query:0:30}..."
            echo "Output: $output"
            exit 1
        fi
    done

    # CLI query with different doc-limit values
    print_status "Test: CLI query with different doc-limit values"
    doc_limits=(1 5 10 100)
    for limit in "${doc_limits[@]}"; do
        output=$(""$CLI_PATH"" query test-db "test query" --doc-limit $limit --dry-run 2>&1)
        if echo "$output" | grep -q "\[DRY RUN\]"; then
            print_success "Query with doc-limit $limit works"
        else
            print_error "Query with doc-limit $limit failed"
            echo "Output: $output"
            exit 1
        fi
    done

    # Python query tests
    print_status "Test: Python query functionality tests"
    if command -v pytest >/dev/null 2>&1; then
        if pytest tests/test_query_functionality.py -v; then
            print_success "Python query functionality tests passed"
        else
            print_error "Python query functionality tests failed"
            exit 1
        fi
        if pytest tests/test_mcp_query.py -v; then
            print_success "Python MCP query tests passed"
        else
            print_error "Python MCP query tests failed"
            exit 1
        fi
        if pytest tests/test_query_integration.py -v; then
            print_success "Python query integration tests passed"
        else
            print_error "Python query integration tests failed"
            exit 1
        fi
    else
        print_warning "pytest not found, skipping Python unit tests"
    fi

    # Go CLI query tests
    print_status "Test: Go CLI query tests"
    print_warning "Go CLI query tests require the maestro-cli repository"
    print_warning "Please run CLI tests in the AI4quantum/maestro-cli repository"
    print_success "Skipping Go CLI query tests (moved to separate repository)"

    print_success "✓ QUERY workflow completed successfully!"
    echo ""
}

# Function to run all workflows
run_all_workflows() {
    print_header "Running ALL end-to-end workflows"
    echo "This will run fast, complete, and query workflows."
    echo ""
    run_fast_workflow
    run_complete_workflow
    run_query_workflow
    print_success "✓ ALL workflows completed successfully!"
    echo ""
}

# Main script logic
main() {
    case "${1:-help}" in
        help)
            show_help
            ;;
        fast)
            run_fast_workflow
            ;;
        complete)
            run_complete_workflow
            ;;
        query)
            run_query_workflow
            ;;
        all)
            run_all_workflows
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 