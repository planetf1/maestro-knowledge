# Contributing to Maestro Knowledge

Thank you for your interest in contributing to Maestro Knowledge! This document provides guidelines and instructions for contributing to this project.

## 📚 Documentation Structure

Before contributing, please familiarize yourself with our documentation:

- **[📖 Documentation Index](README.md)** - Overview of all documentation
- **[🔧 Vector Database Abstraction](VECTOR_DB_ABSTRACTION.md)** - Understanding the database layer
- **[📋 Project Overview](PRESENTATION.md)** - Complete project overview

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Maestro Knowledge. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

#### Before Submitting A Bug Report

* Check the documentation for a list of common questions and problems.
* Perform a cursory search to see if the problem has already been reported. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as GitHub issues. Create an issue and provide the following information by filling in the template.

Explain the problem and include additional details to help maintainers reproduce the problem:

* Use a clear and descriptive title for the issue to identify the problem.
* Describe the exact steps which reproduce the problem in as many details as possible.
* Provide specific examples to demonstrate the steps.
* Describe the behavior you observed after following the steps and point out what exactly is the problem with that behavior.
* Explain which behavior you expected to see instead and why.
* Include screenshots and animated GIFs which show you following the described steps and clearly demonstrate the problem.
* If the problem wasn't triggered by a specific action, describe what you were doing before the problem happened.
* Include details about your configuration and environment:
  * Which version of Maestro Knowledge are you using?
* What's the name and version of the OS you're using?
* Are you running Maestro Knowledge in a virtual machine?
  * What are your environment variables?
  * Which vector database are you using? (Weaviate, Milvus, etc.)
  * Which embedding model are you using? (default, text-embedding-ada-002, etc.)

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Maestro Knowledge, including completely new features and minor improvements to existing functionality.

#### Before Submitting An Enhancement Suggestion

* Check the documentation for suggestions.
* Perform a cursory search to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title for the issue to identify the suggestion.
* Provide a step-by-step description of the suggested enhancement in as many details as possible.
* Provide specific examples to demonstrate the steps.
* Describe the current behavior and explain which behavior you expected to see instead and why.
* Include screenshots and animated GIFs which help you demonstrate the steps or point out the part of Maestro Knowledge which the suggestion is related to.
* Explain why this enhancement would be useful to most Maestro Knowledge users.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible.
* Follow our coding conventions
* Document new code based on the Documentation Style Guide
* End all files with a newline

## 🏗️ Development Setup

### Project Structure

```
maestro-knowledge/
├── docs/                    # 📚 Documentation
│   ├── README.md           # Documentation index
│   ├── VECTOR_DB_ABSTRACTION.md
│   ├── CONTRIBUTING.md     # This file
│   └── PRESENTATION.md
├── examples/                # 📚 Example implementations
│   ├── README.md           # Examples documentation
│   ├── milvus_example.py   # Milvus usage example
│   └── weaviate_example.py # Weaviate usage example
├── src/                     # 🐍 Source code
│   ├── db/                  # Vector database implementations
│   │   ├── __init__.py      # Package exports
│   │   ├── vector_db_base.py # Abstract base class
│   │   ├── vector_db_weaviate.py # Weaviate implementation
│   │   ├── vector_db_milvus.py # Milvus implementation
│   │   └── vector_db_factory.py # Factory function
│   ├── maestro_mcp/         # MCP server implementation
│   │   ├── __init__.py      # Package exports
│   │   ├── server.py        # Main MCP server (FastMCP)
│   │   ├── mcp_config.json  # MCP client configuration
│   │   └── README.md        # MCP server documentation
│   └── vector_db.py         # Vector database compatibility layer
├── cli/                     # Go CLI tool
│   ├── src/                 # Go source code
│   │   ├── main.go          # Main CLI entry point
│   │   ├── list.go          # List command (plural forms)
│   │   ├── create.go        # Create command
│   │   ├── delete.go        # Delete command
│   │   ├── validate.go      # Validate command
│   │   └── mcp_client.go    # MCP server client
│   ├── tests/               # CLI tests
│   ├── examples/            # CLI usage examples
│   ├── build.sh             # Build script
│   └── README.md            # CLI documentation
├── start.sh                 # MCP server start script
├── stop.sh                  # MCP server stop script
├── tests/                   # 🧪 Test suite
│   ├── test_vector_db_base.py
│   ├── test_vector_db_weaviate.py
│   ├── test_vector_db_milvus.py
│   ├── test_vector_db_factory.py
│   ├── test_vector_db.py    # Compatibility layer tests
│   ├── test_mcp_server.py   # MCP server tests
│   └── test_integration_examples.py # Integration tests for examples
├── .github/                 # GitHub configuration
│   └── workflows/           # GitHub Actions workflows
│       └── ci.yml           # Continuous Integration workflow
├── test.sh                  # Test runner script (CLI, MCP, Integration)
├── test-integration.sh      # CLI integration tests
├── tools/                   # Development tools
│   ├── lint.sh              # Linting and formatting script
│   ├── e2e.sh               # End-to-end testing script
│   ├── test-integration.sh  # Integration tests
│   └── tail-logs.sh        # Real-time log monitoring script
├── pyproject.toml           # Project configuration
└── README.md                # Main project documentation
```

### Vector Database Development

When working with vector databases:

1. **Follow the abstraction pattern**: All vector database code should implement the `VectorDatabase` interface
2. **Create separate files**: New implementations should be in separate files (e.g., `src/db/vector_db_pinecone.py`)
3. **Add tests**: Include comprehensive tests in separate test files (e.g., `tests/test_vector_db_pinecone.py`)
4. **Update factory function**: Add new database types to `create_vector_database()` in `src/db/vector_db_factory.py`
5. **Documentation**: Update [VECTOR_DB_ABSTRACTION.md](VECTOR_DB_ABSTRACTION.md) with new implementations
6. **Update compatibility layer**: Add imports to `src/vector_db.py` for backward compatibility
7. **Implement all required methods**: Ensure all abstract methods are implemented (setup, write_documents, list_documents, count_documents, delete_documents, delete_collection, create_query_agent, cleanup, supported_embeddings)

### Embedding Strategy Implementation

The library now supports flexible embedding strategies. When implementing a new vector database:

#### Required Methods for Embedding Support

1. **`supported_embeddings()`**: Return a list of supported embedding model names
2. **`write_documents(documents, embedding="default")`**: Handle different embedding strategies

#### Embedding Strategy Patterns

**For databases with built-in vectorizers (like Weaviate):**
```python
def supported_embeddings(self) -> List[str]:
    return [
        "default",  # Uses database's default vectorizer
        "text2vec-openai",  # OpenAI integration
        "text2vec-cohere",  # Cohere integration
        # Add other supported vectorizers
    ]

def write_documents(self, documents: List[Dict[str, Any]], embedding: str = "default"):
    # Validate embedding parameter
    if embedding not in self.supported_embeddings():
        raise ValueError(f"Unsupported embedding: {embedding}")
    
    # Handle different embedding strategies
    if embedding == "default":
        # Use database's default vectorizer
        pass
    elif embedding == "text2vec-openai":
        # Configure OpenAI vectorizer
        pass
    # ... handle other embedding types
```

**For databases requiring external embedding generation (like Milvus):**
```python
def supported_embeddings(self) -> List[str]:
    return [
        "default",  # Uses pre-computed vectors or default model
        "text-embedding-ada-002",  # OpenAI Ada-002
        "text-embedding-3-small",  # OpenAI text-embedding-3-small
        # Add other supported models
    ]

def write_documents(self, documents: List[Dict[str, Any]], embedding: str = "default"):
    # Validate embedding parameter
    if embedding not in self.supported_embeddings():
        raise ValueError(f"Unsupported embedding: {embedding}")
    
    for doc in documents:
        if embedding == "default":
            # Use pre-computed vector if available, otherwise use default model
            if "vector" in doc:
                vector = doc["vector"]
            else:
                vector = self._generate_embedding(doc["text"], "text-embedding-ada-002")
        else:
            # Generate embedding using specified model
            vector = self._generate_embedding(doc["text"], embedding)
        
        # Store document with vector
        # ...
```

#### Testing Embedding Functionality

When adding tests for new vector database implementations, include tests for:

1. **Supported embeddings method**:
```python
def test_supported_embeddings(self):
    db = YourVectorDatabase()
    embeddings = db.supported_embeddings()
    assert "default" in embeddings
    # Test other expected embeddings
```

2. **Write documents with different embeddings**:
```python
def test_write_documents_default_embedding(self):
    # Test with default embedding
    
def test_write_documents_custom_embedding(self):
    # Test with specific embedding model
    
def test_write_documents_unsupported_embedding(self):
    # Test error handling for unsupported embeddings
```

3. **Embedding model integration**:
```python
def test_embedding_model_generation(self):
    # Test actual embedding generation (with mocking)
```

### MCP Server Development

The MCP (Model Context Protocol) server provides AI agents with access to vector database functionality through a standardized interface with multi-database support.

#### MCP Server Structure

- **`src/maestro_mcp/server.py`**: Main server implementation with FastMCP tool definitions
- **`src/maestro_mcp/mcp_config.json`**: Configuration for MCP clients
- **`src/maestro_mcp/README.md`**: Detailed MCP server documentation

#### Adding New MCP Tools

To add new tools to the MCP server:

1. **Define the tool**: Add a new Pydantic model for input validation
2. **Implement the tool**: Add a new async function with the `@app.tool()` decorator
3. **Add tests**: Update `tests/test_mcp_server.py` to test the new tool
4. **Update documentation**: Document the new tool in `src/maestro_mcp/README.md`

Example of adding a new tool:

```python
# Define input model
class NewToolInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    param1: str = Field(..., description="Parameter description")

# Implement the tool
@app.tool()
async def new_tool(input: NewToolInput) -> str:
    db = get_database_by_name(input.db_name)
    # Implement tool logic here
    return "Tool executed successfully"
```

#### MCP Server Testing

The MCP server tests in `tests/test_mcp_server.py` validate:
- Server creation and initialization
- Tool definitions and structure
- Import dependencies
- Error handling
- Multi-database functionality

### CLI Development

The CLI tool is written in Go and provides command-line access to the MCP server functionality.

#### CLI Command Structure

The CLI uses plural forms for list subcommands:
- `list vector-dbs` (not `list vector-db`)
- `list embeds` (not `list embed`)
- `list cols` (not `list col`)
- `list docs` (not `list doc`)

#### Adding New CLI Commands

1. **Create command file**: Add new command file (e.g., `cli/src/new_command.go`)
2. **Define the command**: Use Cobra framework for command definition
3. **Add to main**: Register the command in `cli/src/main.go`
4. **Add tests**: Create tests in `cli/tests/`
5. **Update documentation**: Update `cli/README.md`

Example command structure:

```go
var newCmd = &cobra.Command{
    Use:   "new [RESOURCE_TYPE] [NAME]",
    Short: "Create new resources",
    Long:  `Create new resources with detailed description.`,
    Args:  cobra.ExactArgs(2),
    RunE: func(cmd *cobra.Command, args []string) error {
        // Command implementation
        return nil
    },
}
```

#### CLI Testing

The CLI tests validate:
- Command help functionality
- Dry-run mode
- Verbose mode
- Environment variable support
- Command-line flag override
- .env file support
- YAML validation
- Environment variable substitution

### Adding New Vector Database Support

To add support for a new vector database:

1. **Create implementation file**: `src/db/vector_db_[name].py`
2. **Create test file**: `tests/test_vector_db_[name].py`
3. **Update factory**: Add new type to `create_vector_database()` in `src/db/vector_db_factory.py`
4. **Update compatibility layer**: Add import to `src/vector_db.py`
5. **Update documentation**: Add new database to `VECTOR_DB_ABSTRACTION.md`
6. **Add environment variables**: Document required environment variables
7. **Create example**: Add `examples/[name]_example.py` following the existing pattern
8. **Implement embedding support**: Add `supported_embeddings()` and update `write_documents()`

Example for adding Pinecone support:

```python
# src/db/vector_db_pinecone.py
from .vector_db_base import VectorDatabase

class PineconeVectorDatabase(VectorDatabase):
    def __init__(self, collection_name: str = "MaestroDocs"):
        super().__init__(collection_name)
        # Initialize Pinecone client
        
    @property
    def db_type(self) -> str:
        return "pinecone"
    
    def supported_embeddings(self) -> List[str]:
        return ["default", "text-embedding-ada-002", "text-embedding-3-small"]
    
    def setup(self):
        # Initialize collection/schema
        pass
        
    def write_documents(self, documents, embedding="default"):
        # Handle different embedding strategies
        # Store documents with vectors
        pass
    
    def list_documents(self, limit=10, offset=0):
        # Retrieve documents
        pass
    
    def count_documents(self) -> int:
        # Get document count
        pass
    
    def delete_documents(self, document_ids):
        # Delete documents by ID
        pass
    
    def delete_collection(self, collection_name=None):
        # Delete entire collection
        pass
    
    def create_query_agent(self):
        # Create query agent
        pass
    
    def cleanup(self):
        # Clean up resources
        pass
```

### Working with Examples

The `examples/` directory contains practical examples for each supported vector database:

- **`milvus_example.py`**: Demonstrates Milvus usage with pre-computed vectors and embedding models
- **`weaviate_example.py`**: Demonstrates Weaviate usage with different embedding models
- **`mcp_example.py`**: Demonstrates MCP server functionality and AI agent integration

When adding a new vector database implementation:

1. **Follow the existing pattern**: Use the same structure as existing examples
2. **Include environment validation**: Check for required environment variables
3. **Add comprehensive error handling**: Use try-catch blocks with helpful error messages
4. **Include cleanup**: Proper resource cleanup in finally blocks
5. **Update examples/README.md**: Document the new example with prerequisites and usage instructions
6. **Test the example**: Ensure it runs successfully with proper configuration
7. **Integration tests**: Examples are automatically validated via `test_integration_examples.py`
8. **Demonstrate embedding functionality**: Show both pre-computed vectors and embedding model usage

The integration tests validate:
- Example file structure and imports
- Execution without errors (with mocked dependencies)
- Environment variable handling
- Error handling patterns
- Cleanup procedures
- Output formatting standards
- Embedding functionality demonstration

Example structure for a new database example:

```python
#!/usr/bin/env python3
"""
[Database Name] Vector Database Example

This example demonstrates how to use the maestro-knowledge library with [Database Name].
"""

import sys
import os
from src.db.vector_db_factory import create_vector_database

def main():
    # Check environment variables
    # Create database instance
    # Display supported embeddings
    # Set up database with specific embedding
    # Write documents with pre-computed vectors
    # Write documents using embedding models
    # List documents
    # Count documents
    # Delete documents (demonstrate CRUD operations)
    # Cleanup

if __name__ == "__main__":
    main()
```

## Style Guides

### Python Style Guide

* Use 4 spaces for indentation rather than tabs
* Keep lines to a maximum of 79 characters
* Use docstrings for all public modules, functions, classes, and methods
* Use spaces around operators and after commas
* Follow PEP 8 guidelines
* Include warning filters for clean output in test files

### Go Style Guide

* Use 4 spaces for indentation
* Follow Go naming conventions
* Use meaningful variable names
* Include proper error handling
* Add comments for exported functions
* Follow Go module conventions

### JavaScript Style Guide

* Use 2 spaces for indentation rather than tabs
* Keep lines to a maximum of 100 characters
* Use semicolons
* Use single quotes for strings unless you are writing JSON
* Follow the Airbnb JavaScript Style Guide

### Documentation Style Guide

* Use [Markdown](https://daringfireball.net/projects/markdown)
* Reference methods and classes in markdown with the following syntax:
  * Reference classes with `ClassName`
  * Reference instance methods with `ClassName#methodName`
  * Reference class methods with `ClassName.methodName`
* Update documentation in the `docs/` directory
* Keep the main `README.md` focused on quick start and overview

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs
* `documentation` - Issues for improving or updating our documentation
* `enhancement` - Issues for enhancing a feature
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `invalid` - Issues that can't be reproduced or are invalid
* `question` - Further information is requested
* `wontfix` - Issues that won't be fixed
* `vector-db` - Issues related to vector database implementations
* `mcp` - Issues related to MCP server functionality
* `embeddings` - Issues related to embedding functionality
* `cli` - Issues related to CLI tool functionality

## Development Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Pre-Pull Request Checklist

Before submitting a pull request, you **MUST** run the following sequence of commands to ensure code quality and functionality:

```bash
./tools/lint.sh && ./test.sh all && ./test-integration.sh
```

This comprehensive test sequence will:
1. **Lint and format code** (`./tools/lint.sh`) - Ensures code follows style guidelines
2. **Start the MCP server** (`./start.sh`) - Prepares the environment for testing
3. **Run all tests** (`./test.sh all`) - Validates unit tests and functionality
4. **Run integration tests** (`./test-integration.sh`) - Tests end-to-end functionality
5. **Run e2e tests** (`./tools/e2e.sh all`) - Tests complete workflows with CLI tool
6. **Stop the MCP server** (`./stop.sh`) - Cleans up the environment
7. **Monitor logs** (`./tools/tail-logs.sh status`) - Verify services are running correctly

**⚠️ Important**: This sequence must pass completely before submitting a PR. If any step fails, fix the issues and run the sequence again.

### Additional Pre-PR Requirements

In addition to the automated checks above, please ensure that:

1. All tests pass (`./test.sh all`)
2. All linting checks pass (`./tools/lint.sh`)
3. The code is properly formatted
4. Documentation is updated
5. New tests are added for new functionality
6. Warning filters are included for clean test output
7. Examples are tested and working (if adding new database support)
8. Embedding functionality is properly tested
9. CLI commands use plural forms for list subcommands
10. Multi-database functionality is properly tested (if applicable)

## Code Quality and Linting

### Running Code Quality Checks

We use Ruff for linting and formatting. Run the comprehensive check:

```bash
./tools/lint.sh
```

This script will:
- Check all source files for linting issues
- Check all test files for linting issues  
- Check all example files for linting issues
- Verify code formatting is correct

### Manual Code Quality Commands

If you need to run individual checks:

```bash

# Run linting only
uv run ruff check src/ tests/ examples/

# Check formatting only
uv run ruff format --check src/ tests/ examples/

# Auto-fix formatting issues
uv run ruff format src/ tests/ examples/

# Run security checks
uv run bandit -r src/
uv run safety check
```

### Integration Tests

We have comprehensive integration tests that validate our examples:

```bash
# Run all tests including integration tests
./test.sh all

# The test suite now includes:
# - Unit tests for core functionality
# - Integration tests for examples
# - Mocked database tests
# - Environment validation tests
# - Embedding functionality tests
# - CLI integration tests
```

### End-to-End Tests

We have end-to-end tests that validate complete workflows with the CLI tool:

```bash
# Show e2e test options
./tools/e2e.sh help

# Run fast e2e workflow (basic functionality)
./tools/e2e.sh fast

# Run complete e2e workflow (with error testing)
./tools/e2e.sh complete

# Run both fast and complete workflows

### Log Monitoring and Debugging

For debugging and monitoring during development, use the log monitoring tools:

```bash
# Show service status with visual indicators
./tools/tail-logs.sh status

# Monitor all logs in real-time
./tools/tail-logs.sh all

# Monitor specific service logs
./tools/tail-logs.sh mcp    # MCP server logs
./tools/tail-logs.sh cli    # CLI logs

# View recent logs
./tools/tail-logs.sh recent
```

**Enhanced Process Management:**
- **✅ Visual status indicators** - Clear service status with checkmarks and X marks
- **📡 Real-time log tailing** - Monitor logs as they're generated
- **🌐 Port monitoring** - Check service availability on ports
- **📄 Log file management** - Automatic detection and size tracking
- **🔄 Graceful restarts** - Proper process cleanup and restart sequencing
./tools/e2e.sh all

# The e2e test suite includes:
# - Vector database creation from YAML
# - Collection management (create, list, delete)
# - Embedding listing
# - Document listing (when write command is implemented)
# - Error handling validation
# - Cleanup and resource management
```

### Test Organization

The test suite follows the modular structure:

- **Base tests**: `test_vector_db_base.py` - Tests for abstract base class
- **Implementation tests**: `test_vector_db_[name].py` - Tests for specific implementations
- **Factory tests**: `test_vector_db_factory.py` - Tests for factory function
- **Compatibility tests**: `test_vector_db.py` - Tests for compatibility layer
- **MCP server tests**: `test_mcp_server.py` - Tests for MCP server functionality
- **Integration tests**: `test_integration_examples.py` - Tests that validate example files work correctly
- **CLI tests**: `cli/tests/` - Tests for CLI functionality

Each test file should:
- Include appropriate warning filters
- Use mocking to avoid external dependencies
- Test both success and error cases
- Include proper cleanup in teardown methods
- Test embedding functionality when applicable

## License

By contributing to Maestro Knowledge, you agree that your contributions will be licensed under its MIT License. 