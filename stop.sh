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
PURPLE='\033[0;35m'
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

print_info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Check if server is running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        # Check if the content is "ready" (stdio mode)
        if [ "$pid" = "ready" ]; then
            return 1  # Not a running HTTP server
        fi
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

# Check if server is ready (for stdio mode)
check_ready() {
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
    
    # Check if HTTP server is running
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_status "Found running HTTP server (PID: $pid)"
        
        # Kill the process
        if kill "$pid" 2>/dev/null; then
            print_success "HTTP server stopped successfully"
        else
            print_warning "Failed to stop HTTP server gracefully, force killing..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        # Remove the PID file
        rm -f "$PID_FILE"
        return 0
    fi
    
    # Check if stdio server is ready
    if check_ready; then
        local status=$(cat "$PID_FILE")
        print_status "Found ready stdio server (Status: $status)"
        
        # Remove the status file
        rm -f "$PID_FILE"
        print_success "MCP stdio server status cleared"
        return 0
    fi
    
    print_warning "No MCP server is running"
    return 0
}

# Show server status
show_status() {
    print_status "MCP Server Status"
    print_status "================="
    
    # Check if HTTP server is running
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_success "HTTP server is running (PID: $pid)"
        if [ -f "$LOG_FILE" ]; then
            print_status "Log file: $LOG_FILE"
            print_status "Recent log entries:"
            tail -n 5 "$LOG_FILE" 2>/dev/null || print_warning "No log entries found"
        fi
        print_info "🌐 Server URL: http://localhost:8030 (or check log for actual URL)"
        print_info "📖 OpenAPI docs: http://localhost:8030/docs"
        print_info "📚 ReDoc docs: http://localhost:8030/redoc"
        print_info "🔧 MCP endpoint: http://localhost:8030/mcp/"
    elif check_ready; then
        local status=$(cat "$PID_FILE")
        print_success "Stdio server is ready (Status: $status)"
        if [ -f "$LOG_FILE" ]; then
            print_status "Log file: $LOG_FILE"
            print_status "Recent log entries:"
            tail -n 5 "$LOG_FILE" 2>/dev/null || print_warning "No log entries found"
        fi
        print_status "To use with MCP clients, run: python -m src.maestro_mcp.server"
        print_info "💡 Tip: Use './start.sh --http' to start HTTP server for browser access"
    else
        print_warning "No MCP server is running"
        if [ -f "$PID_FILE" ]; then
            print_warning "Stale PID file found: $PID_FILE"
        fi
    fi
}

# Clean up stale files
cleanup() {
    print_status "Cleaning up stale files..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ! ps -p "$pid" > /dev/null 2>&1; then
            rm -f "$PID_FILE"
            print_success "Removed stale PID file"
        else
            print_warning "PID file contains running process, not removing"
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
            ./start.sh --stdio
            ;;
        "restart-http")
            print_status "Restarting MCP HTTP server..."
            stop_server
            sleep 2
            ./start.sh --http
            ;;
        *)
            print_error "Unknown command: $1"
            print_status "Usage: $0 {stop|status|cleanup|restart|restart-http}"
            print_status "  stop         - Stop the MCP server"
            print_status "  status       - Show server status"
            print_status "  cleanup      - Clean up stale files"
            print_status "  restart      - Restart the MCP stdio server"
            print_status "  restart-http - Restart the MCP HTTP server"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 