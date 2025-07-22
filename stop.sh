#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

# Maestro Knowledge MCP Server Stop Script

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

# Check if server is ready
check_running() {
    if [ -f "$PID_FILE" ]; then
        local status=$(cat "$PID_FILE")
        if [ "$status" = "ready" ]; then
            return 0  # Server is ready
        else
            # Status file exists but with wrong status
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1  # Server is not ready
}

# Stop the MCP server
stop_server() {
    print_status "Stopping Maestro Knowledge MCP Server..."
    
    # Check if server is ready
    if ! check_running; then
        print_warning "MCP server is not ready"
        return 0
    fi
    
    local status=$(cat "$PID_FILE")
    print_status "Found ready server (Status: $status)"
    
    # Remove the status file
    rm -f "$PID_FILE"
    print_success "MCP server status cleared"
    return 0
}

# Show server status
show_status() {
    print_status "MCP Server Status"
    print_status "================="
    
    if check_running; then
        local status=$(cat "$PID_FILE")
        print_success "Server is ready (Status: $status)"
        if [ -f "$LOG_FILE" ]; then
            print_status "Log file: $LOG_FILE"
            print_status "Recent log entries:"
            tail -n 5 "$LOG_FILE" 2>/dev/null || print_warning "No log entries found"
        fi
        print_status "To use with MCP clients, run: python -m src.maestro_mcp.server"
    else
        print_warning "Server is not ready"
        if [ -f "$PID_FILE" ]; then
            print_warning "Stale status file found: $PID_FILE"
        fi
    fi
}

# Clean up stale files
cleanup() {
    print_status "Cleaning up stale files..."
    
    if [ -f "$PID_FILE" ]; then
        local status=$(cat "$PID_FILE")
        if [ "$status" != "ready" ]; then
            rm -f "$PID_FILE"
            print_success "Removed stale status file"
        fi
    fi
}

# Main execution
main() {
    print_status "Maestro Knowledge MCP Server Manager"
    print_status "====================================="
    
    case "${1:-stop}" in
        "stop")
            stop_server
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "restart")
            print_status "Restarting MCP server..."
            stop_server
            sleep 2
            ./start.sh
            ;;
        *)
            print_error "Unknown command: $1"
            print_status "Usage: $0 {stop|status|cleanup|restart}"
            print_status "  stop     - Stop the MCP server"
            print_status "  status   - Show server status"
            print_status "  cleanup  - Clean up stale files"
            print_status "  restart  - Restart the MCP server"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 