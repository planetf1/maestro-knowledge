#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[LINT]${NC} $1"
}

print_header "Running comprehensive linting checks..."

# Python Linting Section
print_header "Python Code Quality Checks"
echo "🔍 Running Ruff linter on source and test files..."

# Run ruff check on all source, test, and example files
echo "📁 Checking source files..."
uv run ruff check src/

echo "🧪 Checking test files..."
uv run ruff check tests/

echo "📚 Checking example files..."
uv run ruff check examples/

echo "✅ All Python linting checks passed!"

# Optional: Run ruff format to check formatting
echo "🎨 Checking Python code formatting..."
uv run ruff format --check src/ tests/ examples/

echo "✨ All Python formatting checks passed!"

# Go Linting Section
print_header "Go Code Quality Checks"

# Check if CLI directory exists
if [ ! -d "cli" ]; then
    print_error "CLI directory not found"
    exit 1
fi

# Check if CLI lint script exists
if [ ! -f "cli/lint.sh" ]; then
    print_error "CLI lint script not found: cli/lint.sh"
    exit 1
fi

# Run Go linting
echo "🔧 Running Go linting checks..."
cd cli
if ./lint.sh; then
    print_status "✓ Go linting checks passed"
else
    print_error "Go linting checks failed"
    exit 1
fi
cd ..

print_header "All code quality checks completed successfully! 🎯" 