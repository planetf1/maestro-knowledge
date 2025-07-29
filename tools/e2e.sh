#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

# Maestro Knowledge End-to-End Testing Script

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
CLI_PATH="$PROJECT_ROOT/maestro-k"
TEST_YAML="$PROJECT_ROOT/tests/yamls/test_local_milvus.yaml"

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
    echo "  all      - Run both fast and complete workflows"
    echo ""
    echo "Examples:"
    echo "  $0 help"
    echo "  $0 fast"
    echo "  $0 complete"
    echo "  $0 all"
    echo ""
    echo "Note: This script requires the MCP server to be running."
    echo "      Run './start.sh' before executing this script."
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check if CLI exists
    if [ ! -f "$CLI_PATH" ]; then
        print_error "CLI tool not found at $CLI_PATH"
        print_error "Please build the CLI first: cd cli && ./build.sh"
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
    if $CLI_PATH list vdbs 2>/dev/null | grep -q "$vdb_name"; then
        print_status "Found existing vector database '$vdb_name', cleaning up..."
        
        # Get all collections and delete test-related ones
        print_status "Cleaning up test collections..."
        local collections_output=$($CLI_PATH list collections $vdb_name 2>/dev/null || echo "[]")
        
        # Delete collections that match test patterns
        echo "$collections_output" | grep -o '"[^"]*"' | tr -d '"' | while read -r collection; do
            if [[ "$collection" == test_* ]] || [[ "$collection" == ExampleCollection ]]; then
                print_status "Deleting collection: $collection"
                $CLI_PATH delete collection $vdb_name "$collection" 2>/dev/null || true
            fi
        done
        
        # Delete vector database
        run_command "$CLI_PATH delete vdb $vdb_name" "Deleting existing vector database"
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
    run_command "$CLI_PATH create vdb $TEST_YAML" "Creating vector database from YAML"
    
    # Step 2: List embeddings
    run_command "$CLI_PATH list embeddings $vdb_name" "Listing available embeddings"
    
    # Step 3: Create collection
    run_command "$CLI_PATH create collection $vdb_name $collection_name" "Creating collection"
    
    # Step 4: List collections
    run_command "$CLI_PATH list collections $vdb_name" "Listing collections"
    
    # Step 5: Create a simple document (using echo to create content)
    local doc_content="This is a test document for end-to-end testing."
    local doc_file="/tmp/test_document.txt"
    echo "$doc_content" > "$doc_file"
    
    print_command "echo '$doc_content' > $doc_file"
    print_success "✓ Created test document"
    
    # Note: Since write command is not yet implemented, we'll skip document writing for now
    print_warning "Document writing skipped (write command not yet implemented)"
    
    # Step 6: List documents (will be empty since we didn't write any)
    run_command "$CLI_PATH list documents $vdb_name $collection_name" "Listing documents (empty)"
    
    # Step 7: Delete collection
    run_command "$CLI_PATH delete collection $vdb_name $collection_name" "Deleting collection"
    
    # Step 8: Delete vector database
    run_command "$CLI_PATH delete vdb $vdb_name" "Deleting vector database"
    
    # Cleanup
    rm -f "$doc_file"
    
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
    run_command "$CLI_PATH create vdb $TEST_YAML" "Creating vector database from YAML"
    
    # Step 2: List embeddings
    run_command "$CLI_PATH list embeddings $vdb_name" "Listing available embeddings"
    
    # Step 3: Create first collection
    run_command "$CLI_PATH create collection $vdb_name $collection1" "Creating first collection"
    
    # Step 4: Create second collection
    run_command "$CLI_PATH create collection $vdb_name $collection2" "Creating second collection"
    
    # Step 5: List collections
    run_command "$CLI_PATH list collections $vdb_name" "Listing collections"
    
    # Step 6: Create test documents
    local doc1_content="This is test document 1 for collection 1."
    local doc2_content="This is test document 2 for collection 2."
    local doc1_file="/tmp/test_document_1.txt"
    local doc2_file="/tmp/test_document_2.txt"
    
    echo "$doc1_content" > "$doc1_file"
    echo "$doc2_content" > "$doc2_file"
    
    print_command "echo '$doc1_content' > $doc1_file"
    print_command "echo '$doc2_content' > $doc2_file"
    print_success "✓ Created test documents"
    
    # Note: Since write command is not yet implemented, we'll skip document writing for now
    print_warning "Document writing skipped (write command not yet implemented)"
    
    # Step 7: List documents (will be empty since we didn't write any)
    run_command "$CLI_PATH list documents $vdb_name $collection1" "Listing documents in collection 1 (empty)"
    run_command "$CLI_PATH list documents $vdb_name $collection2" "Listing documents in collection 2 (empty)"
    
    # Step 8: Test error handling - try to delete non-existent collection
    print_header "Testing error handling..."
    print_command "$CLI_PATH delete collection $vdb_name $non_existent_collection"
    echo "--- Attempting to delete non-existent collection ---"
    if ! $CLI_PATH delete collection $vdb_name $non_existent_collection 2>&1; then
        print_success "✓ Correctly failed to delete non-existent collection"
    else
        print_error "✗ Should have failed to delete non-existent collection"
        return 1
    fi
    echo ""
    
    # Step 9: Delete collections
    run_command "$CLI_PATH delete collection $vdb_name $collection1" "Deleting first collection"
    run_command "$CLI_PATH delete collection $vdb_name $collection2" "Deleting second collection"
    
    # Step 10: Delete vector database
    run_command "$CLI_PATH delete vdb $vdb_name" "Deleting vector database"
    
    # Cleanup
    rm -f "$doc1_file" "$doc2_file"
    
    print_success "✓ COMPLETE workflow completed successfully!"
    echo ""
}

# Function to run all workflows
run_all_workflows() {
    print_header "Running ALL end-to-end workflows"
    echo "This will run both fast and complete workflows."
    echo ""
    
    run_fast_workflow
    run_complete_workflow
    
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