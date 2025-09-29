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
    echo "  ${GREEN}Basic Test Categories:${NC}"
    echo "  unit        Run only unit tests (fast, isolated, no external deps) (~5s)"
    echo "  integration Run only integration tests (components working together) (~5s)"
    echo "  e2e         Run only end-to-end tests (requires external dependencies)"
    echo ""
    echo "  ${GREEN}Combined Test Categories:${NC}"
    echo "  standard    Run standard tests (unit + integration) - no external deps (~10s)"
    echo "  all         Run everything (all tests including those with external deps)"
    echo ""
    echo "Examples:"
    echo "  ./test.sh unit        # Fast unit tests"
    echo "  ./test.sh integration # Integration tests"
    echo "  ./test.sh standard    # Standard tests (unit + integration)"
    echo "  ./test.sh e2e         # End-to-end tests (requires external dependencies)"
    echo "  ./test.sh all         # Everything (including tests with external deps)"
    echo "  ./test.sh             # Run standard tests (default)"
    echo ""
    echo "Test Categories:"
    echo "  ${GREEN}Unit Tests:${NC}"
    echo "    - Isolated component testing with mocked dependencies"
    echo "    - Fast execution, no external services required"
    echo "    - Pure Python logic validation"
    echo ""
    echo "  ${GREEN}Integration Tests:${NC}"
    echo "    - Multiple Python components working together"
    echo "    - Database factories, chunking systems, etc."
    echo "    - Still uses mocks for external services"
    echo ""

    echo "  ${GREEN}End-to-End Python Tests:${NC}"
    echo "    - Full Python application stack"
    echo "    - MCP server with vector databases"
    echo "    - Complete workflow validation"
    echo ""
    echo "  ${GREEN}CLI Tests:${NC}"
    echo "    - CLI has been moved to: AI4quantum/maestro-cli"
    echo "    - Please run CLI tests in the maestro-cli repository"
    echo ""
    echo "  ${GREEN}System Integration Tests:${NC}"
    echo "    - End-to-end CLI + MCP testing"
    echo "    - Real vector database operations"
    echo "    - Complete system workflow validation"
    echo "    - Requires CLI from AI4quantum/maestro-cli repository"
}

# Check command line arguments
case "${1:-standard}" in  # Default to standard tests
    "unit")
        RUN_UNIT_TESTS=true
        RUN_INTEGRATION_TESTS=false
        RUN_E2E_TESTS=false
        RUN_CLI_TESTS=false
        RUN_SYSTEM_E2E_TESTS=false
        ;;
    "integration")
        RUN_UNIT_TESTS=false
        RUN_INTEGRATION_TESTS=true
        RUN_E2E_TESTS=false
        RUN_CLI_TESTS=false
        RUN_SYSTEM_E2E_TESTS=false
        ;;
    "service")
        print_error "Unknown command: service"
        echo ""
        print_help
        exit 1
        ;;
    "e2e")
        RUN_UNIT_TESTS=true
        RUN_INTEGRATION_TESTS=false
        RUN_E2E_TESTS=false
        RUN_CLI_TESTS=false
        RUN_SYSTEM_E2E_TESTS=false
        ;;
    "standard")
        # Standard tests - unit + integration (no external dependencies)
        # This is what most people would use and what CI should run
        RUN_UNIT_TESTS=true
        RUN_INTEGRATION_TESTS=true
        RUN_E2E_TESTS=false
        RUN_CLI_TESTS=false
        RUN_SYSTEM_E2E_TESTS=false
        ;;
    "all")
        # Everything (all tests including those with external dependencies)
        RUN_UNIT_TESTS=true
        RUN_INTEGRATION_TESTS=true
        RUN_E2E_TESTS=true
        RUN_CLI_TESTS=true
        RUN_SYSTEM_E2E_TESTS=true
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

# Run unit tests if requested
if [ "$RUN_UNIT_TESTS" = true ]; then
    print_header "Running Unit Tests..."
    
    # Add some test .env variables
    export OPENAI_API_KEY=fake-openai-key
    export WEAVIATE_API_KEY=fake-weaviate-key
    export WEAVIATE_URL=fake-weaviate-url.com

    # Run unit tests only
    PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -m unit -v
    
    print_status "✓ Unit tests completed"
fi

# Run integration tests if requested
if [ "$RUN_INTEGRATION_TESTS" = true ]; then
    print_header "Running Integration Tests..."
    
    # Add some test .env variables
    export OPENAI_API_KEY=fake-openai-key
    export WEAVIATE_API_KEY=fake-weaviate-key
    export WEAVIATE_URL=fake-weaviate-url.com

    # Run integration tests only
    PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -m integration -v
    
    print_status "✓ Integration tests completed"
fi



# Run end-to-end Python tests if requested
if [ "$RUN_E2E_TESTS" = true ]; then
    print_header "Running End-to-End Python Tests..."
    
    # Add some test .env variables
    export OPENAI_API_KEY=fake-openai-key
    export WEAVIATE_API_KEY=fake-weaviate-key
    export WEAVIATE_URL=fake-weaviate-url.com

    # Run e2e tests only
    PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -m e2e -v
    
    print_status "✓ End-to-end Python tests completed"
fi

# Run MCP tests if requested (legacy - all Python tests)
if [ "$RUN_MCP_TESTS" = true ]; then
    print_header "Running MCP Server Tests (All Python Tests)..."
    
    # Add some test .env variables
    export OPENAI_API_KEY=fake-openai-key
    export WEAVIATE_API_KEY=fake-weaviate-key
    export WEAVIATE_URL=fake-weaviate-url.com

    # Run all tests with the correct PYTHONPATH and robustly suppress Pydantic deprecation warnings
    PYTHONWARNINGS="ignore:PydanticDeprecatedSince20" PYTHONPATH=src uv run pytest -v
    
    print_header "MCP Server Tests Completed Successfully! 🎉"
fi

# Run system integration tests if requested
if [ "$RUN_SYSTEM_E2E_TESTS" = true ]; then
    print_header "Running System Integration Tests..."
    
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
    
    print_header "System Integration Tests Completed Successfully! 🎉"
fi

# Print summary of what was run
TESTS_RUN=""
if [ "$RUN_UNIT_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN Unit"
fi
if [ "$RUN_INTEGRATION_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN Integration"
fi

if [ "$RUN_E2E_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN E2E-Python"
fi
if [ "$RUN_MCP_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN MCP-All-Python"
fi
if [ "$RUN_CLI_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN CLI"
fi
if [ "$RUN_SYSTEM_E2E_TESTS" = true ]; then
    TESTS_RUN="$TESTS_RUN System-E2E"
fi

if [ -n "$TESTS_RUN" ]; then
    print_status "✅ All requested tests completed successfully:$TESTS_RUN"
else
    print_warning "No tests were run"
fi 