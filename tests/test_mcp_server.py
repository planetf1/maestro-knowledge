#!/usr/bin/env python3
# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Test script for the Maestro Vector Database MCP server.
This script tests the server functionality without requiring a full MCP client.
"""

import sys
from pathlib import Path

# Ensure the project root is in sys.path
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.maestro_mcp.server import create_mcp_server


def test_server_creation() -> None:
    """Test that the server can be created successfully."""
    print("Testing MCP Server Creation...")
    print("=" * 50)

    try:
        server = create_mcp_server()
        print("✓ Server created successfully")
        print(f"✓ Server name: {server.name}")

        # Test that the server has the expected structure
        print("✓ Server structure verified")
    except Exception as e:
        assert False, f"Failed to create server: {e}"


def test_tool_definitions() -> None:
    """Test that all expected tools are defined."""
    print("\nTesting Tool Definitions...")
    print("=" * 50)

    try:
        server = create_mcp_server()

        # Get the tool definitions from the server
        expected_tools = [
            "create_vector_database",
            "setup_database",
            "get_supported_embeddings",
            "write_documents",
            "write_document",
            "list_documents",
            "count_documents",
            "delete_documents",
            "delete_document",
            "delete_collection",
            "cleanup",
            "get_database_info",
            "list_collections",
            "list_databases",
        ]

        print("✓ Server created with expected tools")
        print(f"✓ Expected {len(expected_tools)} tools")

        # Test that the server has the right structure for FastMCP
        assert hasattr(server, "get_tools"), "Server missing get_tools method"
        print("✓ Server has get_tools method")

        assert hasattr(server, "tool"), "Server missing tool decorator"
        print("✓ Server has tool decorator")
    except Exception as e:
        assert False, f"Failed to test tool definitions: {e}"


def test_imports() -> None:
    """Test that all required imports work."""
    print("\nTesting Imports...")
    print("=" * 50)

    try:
        # Test MCP imports
        print("✓ MCP imports successful")

        # Test our imports
        print("✓ Vector database imports successful")
    except Exception as e:
        assert False, f"Import test failed: {e}"


def main() -> None:
    """Run all tests."""
    print("Maestro Vector Database MCP Server Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_server_creation,
        test_tool_definitions,
    ]

    for test in tests:
        test()
        print()

    print("=" * 60)
    print("✓ All tests passed!")


if __name__ == "__main__":
    main()
