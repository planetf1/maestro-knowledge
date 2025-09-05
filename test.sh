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
    echo "  cli         CLI tests (moved to separate repository - AI4quantum/maestro-cli)"
    echo "  mcp         Run only MCP server tests (Python-based server)"
    echo "  integration Run only integration tests (CLI + MCP end-to-end)"
    echo "  all         Run all tests (MCP + Integration)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./test.sh cli         # CLI tests (redirected to separate repo)"
    echo "  ./test.sh mcp         # Run only MCP server tests"
    echo "  ./test.sh integration # Run only integration tests"
    echo "  ./test.sh all         # Run all tests"
    echo "  ./test.sh             # Run MCP tests (default)"
    echo ""
    echo "Test Categories:"
    echo "  CLI Tests:"
    echo "    - CLI has been moved to: AI4quantum/maestro-cli"
    echo "    - Please run CLI tests in the maestro-cli repository"
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
    echo "    - Requires CLI from AI4quantum/maestro-cli repository"
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

# Run CLI tests if requested
if [ "$RUN_CLI_TESTS" = true ]; then
    print_header "CLI tests are now in a separate repository..."
    print_status "CLI has been moved to: AI4quantum/maestro-cli"
    print_status "Please run CLI tests in the maestro-cli repository"
    print_warning "Skipping CLI tests in this repository"
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
    
    # Check if CLI is available
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
        if command -v maestro >/dev/null 2>&1; then
            # Verify this is the correct maestro CLI by checking if it has vectordb command
            if maestro vectordb --help >/dev/null 2>&1; then
                CLI_PATH="maestro"
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