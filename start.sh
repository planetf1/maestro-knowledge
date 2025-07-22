#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

# Maestro Knowledge MCP Server Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/mcp_server.pid"
LOG_FILE="$SCRIPT_DIR/mcp_server.log"
PYTHON_MODULE="src.maestro_mcp.server"

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

# Check if server is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Server is running
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1  # Server is not running
}

# Start the MCP server
start_server() {
    print_status "Starting Maestro Knowledge MCP Server..."
    
    # Check if already running
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_warning "MCP server is already running (PID: $pid)"
        return 0
    fi
    
    # Create log file if it doesn't exist
    touch "$LOG_FILE"
    
    # Start the server in background
    print_status "Launching server with module: $PYTHON_MODULE"
    
    # Set PYTHONPATH to include the project root
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    
    # Start the server and capture PID
    # Note: MCP server runs with stdio, so we need to handle this differently
    # For now, we'll create a simple test to verify the module works
    if python -c "import $PYTHON_MODULE; print('Module imported successfully')" > "$LOG_FILE" 2>&1; then
        print_success "MCP server module is ready"
        print_status "Note: MCP server runs with stdio for client communication"
        print_status "To use with MCP clients, run: python -m $PYTHON_MODULE"
        # Create a status file to track that the module is ready
        echo "ready" > "$PID_FILE"
        print_status "Log file: $LOG_FILE"
        print_status "PID file: $PID_FILE"
        print_status "To check status, run: ./stop.sh status"
        return 0
    else
        print_error "Failed to import MCP server module"
        print_status "Check the log file for details: $LOG_FILE"
        return 1
    fi
    

}

# Main execution
main() {
    print_status "Maestro Knowledge MCP Server Manager"
    print_status "====================================="
    
    # Check if Python is available
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check if the MCP module exists
    if ! python -c "import $PYTHON_MODULE" 2>/dev/null; then
        print_error "MCP server module not found: $PYTHON_MODULE"
        print_status "Make sure you're running this from the project root directory"
        exit 1
    fi
    
    start_server
    exit $?
}

# Run main function
main "$@" 