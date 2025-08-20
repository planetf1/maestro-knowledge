#!/bin/bash

# Combined test script for both Python and CLI components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_help() {
    echo -e "${BLUE}Maestro Knowledge Test Suite${NC}"
    echo ""
    echo "Usage: ./test.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  cli         Run only CLI tests (Go-based command line interface)"
    echo "  mcp         Run only MCP server tests (Python-based server)"
    echo "  integration Run only integration tests (CLI + MCP end-to-end)"
    echo "  all         Run all tests (CLI + MCP + Integration)"
    echo "  help        Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  MAESTRO_K_SKIP_INTEGRATION=true  Skip integration tests even when running 'all'"
    echo "  SKIP_INTEGRATION=true            Alias for MAESTRO_K_SKIP_INTEGRATION"
    echo ""
    echo "Examples:"
    echo "  ./test.sh cli         # Run only CLI tests"
    echo "  ./test.sh mcp         # Run only MCP server tests"
    echo "  ./test.sh integration # Run only integration tests"
    echo "  ./test.sh all         # Run all tests"
    echo "  MAESTRO_K_SKIP_INTEGRATION=true ./test.sh all  # Run all but skip integration"
    echo "  ./test.sh             # Run MCP tests (default)"
    echo ""
    echo "Test Categories:"
    echo "  CLI Tests:"
    echo "    - Go unit tests for CLI commands"
    echo "    - CLI functionality validation"
    echo "    - YAML validation tests"
    echo "    - Command line argument parsing"
    echo ""
    echo "  MCP Tests:"
    echo "    - Python unit tests for MCP server"
    echo "    - Vector database implementations"
    echo "    - API endpoint testing"
    echo "    - Integration with vector databases"
    echo ""
    echo "  Integration Tests:"
    echo "    - End-to-end CLI + MCP testing"
    echo "    - Real vector database operations"
    echo "    - Complete workflow validation"
}

# Check command line arguments
case "${1:-mcp}" in
    "cli")
        RUN_CLI_TESTS=true
        RUN_MCP_TESTS=false
        RUN_INTEGRATION_TESTS=false
        ;;
    "mcp")
        RUN_CLI_TESTS=false
        RUN_MCP_TESTS=true
        RUN_INTEGRATION_TESTS=false
        ;;
    "integration")
        RUN_CLI_TESTS=false
        RUN_MCP_TESTS=false
        RUN_INTEGRATION_TESTS=true
        ;;
    "all")
        RUN_CLI_TESTS=true
        RUN_MCP_TESTS=true
        RUN_INTEGRATION_TESTS=true
        ;;
    "help"|"-h"|"--help")
        print_help
        exit 0
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        print_help
        exit 1
        ;;
esac

# Allow skipping integration tests via environment variable toggles
if [ "${MAESTRO_K_SKIP_INTEGRATION}" = "true" ] || [ "${MAESTRO_K_SKIP_INTEGRATION}" = "1" ] || \
   [ "${SKIP_INTEGRATION}" = "true" ] || [ "${SKIP_INTEGRATION}" = "1" ]; then
    if [ "${RUN_INTEGRATION_TESTS}" = true ]; then
        print_warning "Skipping integration tests due to MAESTRO_K_SKIP_INTEGRATION/SKIP_INTEGRATION env var"
    fi
    RUN_INTEGRATION_TESTS=false
fi

# Run CLI tests if requested
if [ "$RUN_CLI_TESTS" = true ]; then
    print_header "Running CLI Workflow Tests..."
    
    # Check if we're in the right directory
    if [ ! -f "cli/go.mod" ]; then
        print_error "CLI tests require cli/go.mod to exist"
        exit 1
    fi

    # Step 1: Set up Go
    print_status "Step 1: Setting up Go..."
    if command -v go &> /dev/null; then
        GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
        print_status "✓ Go $GO_VERSION detected"
    else
        print_error "Go is not installed"
        exit 1
    fi

    # Step 2: Build CLI
    print_status "Step 2: Building CLI..."
    cd cli
    if ./build.sh; then
        print_status "✓ CLI build successful"
    else
        print_error "CLI build failed"
        exit 1
    fi
    cd ..

    # Step 3: Test CLI
    print_status "Step 3: Testing CLI..."
    cd cli
    if ./test.sh unit; then
        print_status "✓ CLI tests passed"
    else
        print_error "CLI tests failed"
        exit 1
    fi
    cd ..

    # Step 4: Test CLI functionality
    print_status "Step 4: Testing CLI functionality..."
    # Copy binary to root for testing
    cp cli/maestro-k ./maestro-k
    chmod +x ./maestro-k
    if ./maestro-k --version &> /dev/null; then
        print_status "✓ CLI version command works"
    else
        print_error "CLI version command failed"
        exit 1
    fi

    if ./maestro-k --help &> /dev/null; then
        print_status "✓ CLI help command works"
    else
        print_error "CLI help command failed"
        exit 1
    fi

    if ./maestro-k validate --help &> /dev/null; then
        print_status "✓ CLI validate help command works"
    else
        print_error "CLI validate help command failed"
        exit 1
    fi

    # Step 5: Test YAML validation
    print_status "Step 5: Testing YAML validation..."

    # Test with valid YAML
    if ./maestro-k validate --verbose tests/yamls/test_local_milvus.yaml &> /dev/null; then
        print_status "✓ Valid YAML validation works"
    else
        print_error "Valid YAML validation failed"
        exit 1
    fi

    # Test with schema validation (if schema exists)
    if [ -f "schemas/vector-database-schema.json" ]; then
        if ./maestro-k validate --verbose schemas/vector-database-schema.json tests/yamls/test_local_milvus.yaml &> /dev/null; then
            print_status "✓ Schema validation works"
        else
            print_error "Schema validation failed"
            exit 1
        fi
    else
        print_warning "schemas/vector-database-schema.json not found, skipping schema validation test"
    fi

    # Test with invalid YAML (should fail)
    # Create a temporary invalid YAML file
    INVALID_YAML_CONTENT='---
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: test-milvus
spec:
  type: milvus
  uri: localhost:19530
  collection_name: test_collection
  embedding: text-embedding-3-small
  mode: local
  # Missing closing quote - this will cause a YAML parsing error
  api_version: "v1'
    
    INVALID_YAML_FILE=$(mktemp)
    echo "$INVALID_YAML_CONTENT" > "$INVALID_YAML_FILE"
    
    if ./maestro-k validate --verbose "$INVALID_YAML_FILE" &> /dev/null; then
        print_warning "⚠ Invalid YAML validation should have failed"
    else
        print_status "✓ Invalid YAML correctly rejected"
    fi
    
    # Clean up
    rm -f "$INVALID_YAML_FILE"

    # Step 6: Show CLI info
    print_status "Step 6: Showing CLI info..."
    echo "CLI binary information:"
    ls -lh maestro-k
    file maestro-k
    echo "CLI version:"
    ./maestro-k --version

    print_header "CLI Workflow Tests Completed Successfully! 🎉"
fi

# Run MCP tests if requested
if [ "$RUN_MCP_TESTS" = true ]; then
    print_header "Running MCP Server Tests..."
    
    # Add some test .env variables
    export OPENAI_API_KEY=fake-openai-key
    export WEAVIATE_API_KEY=fake-weaviate-key
    export WEAVIATE_URL=fake-weaviate-url.com

    # Run all tests with the correct PYTHONPATH and robustly suppress Pydantic deprecation warnings
    PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -v
    
    print_header "MCP Server Tests Completed Successfully! 🎉"
fi

# Run integration tests if requested
if [ "$RUN_INTEGRATION_TESTS" = true ]; then
    print_header "Running Integration Tests..."
    
    if [ -f "./tools/test-integration.sh" ]; then
        if ./tools/test-integration.sh; then
            print_status "✓ Integration tests passed"
        else
            print_error "Integration tests failed"
            exit 1
        fi
    else
        print_warning "tools/test-integration.sh not found, skipping integration tests"
    fi
    
    print_header "Integration Tests Completed Successfully! 🎉"
fi

print_status "All requested tests completed!" 