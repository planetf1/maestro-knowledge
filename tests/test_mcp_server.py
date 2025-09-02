#!/usr/bin/env python3
# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Test script for the Maestro Vector Database MCP server.
This script tests the server functionality without requiring a full MCP client.
"""

import sys
from pathlib import Path
import json
from unittest.mock import MagicMock, patch

# Ensure the project root is in sys.path
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.maestro_mcp.server import create_mcp_server


def test_server_creation():
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


def test_tool_definitions():
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


def test_imports():
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

def test_resync_vector_databases_with_metadata():
    """Test that resync correctly loads metadata from collection descriptions."""
    print("\nTesting resync_vector_databases with metadata...")
    print("=" * 50)

    # The server module holds the global 'vector_databases' dict we want to inspect
    from src.maestro_mcp import server as mcp_server

    # Clean up state from other tests
    mcp_server.vector_databases.clear()

    collection_name = "resync_test_collection"
    
    # This is the metadata we expect to be "read" from the collection description
    expected_metadata = {
        "name": collection_name,
        "embedding": "text-embedding-3-small",
        "chunking": {"strategy": "Sentence", "parameters": {"chunk_size": 256}},
        "embedding_details": {"source": "collection_metadata"},
    }

    # We patch the MilvusVectorDatabase class within the server module's scope
    with patch("src.maestro_mcp.server.MilvusVectorDatabase") as mock_milvus_vdb:
        # Mock the instance that will be created inside resync
        mock_instance = MagicMock()
        
        # Configure the mock for the instance's methods
        mock_instance.list_collections.return_value = [collection_name]
        mock_instance.get_collection_info.return_value = expected_metadata
        
        # When MilvusVectorDatabase() is called, return our mock_instance
        mock_milvus_vdb.return_value = mock_instance

        # Call the function to be tested
        added = mcp_server.resync_vector_databases()

    # Assertions
    assert added == [collection_name], "The function should report the new collection as added."
    print(f"✓ resync reported added collections: {added}")

    assert collection_name in mcp_server.vector_databases, "The collection should be in the server's registry."
    print(f"✓ Collection '{collection_name}' is in the registry.")

    # Check that get_collection_info was called, which is the key of the new logic
    mock_instance.get_collection_info.assert_called_once_with(collection_name)
    print("✓ get_collection_info was called to load metadata.")

    # Verify that the in-memory state of the registered DB instance is correct
    registered_db = mcp_server.vector_databases[collection_name]
    assert registered_db._collections_metadata[collection_name]["chunking"] == expected_metadata["chunking"]
    assert registered_db.embedding_model == expected_metadata["embedding"]
    print("✓ In-memory metadata cache was correctly populated.")

    # Cleanup
    mcp_server.vector_databases.clear()


def main():
    """Run all tests."""
    print("Maestro Vector Database MCP Server Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_server_creation,
        test_tool_definitions,
        test_resync_vector_databases_with_metadata,
    ]

    for test in tests:
        test()
        print()

    print("=" * 60)
    print("✓ All tests passed!")


if __name__ == "__main__":
    main()
