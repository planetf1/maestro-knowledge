#!/bin/bash

# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

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
echo "📝 Go linting is now in the separate CLI repository: AI4quantum/maestro-cli"
echo "✅ Skipping Go linting checks (CLI moved to separate repository)"

print_header "All code quality checks completed successfully! 🎯" 