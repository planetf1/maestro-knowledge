# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Shared E2E test functions for all vector database backends.

These test functions are backend-agnostic and can be used with any
vector database backend (Milvus, Weaviate, etc.) by passing the
appropriate backend configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import Client

from tests.e2e.common import get_backend_config, get_db_name_for_test


async def run_database_management_tests(client: "Client", backend_name: str) -> None:
    """Test database creation, collection management, and list_collections tool."""
    config = get_backend_config(backend_name)
    db_name = get_db_name_for_test(backend_name, "DB_Management")

    # Test create_vector_database_tool
    res = await client.call_tool(
        "create_vector_database_tool",
        {
            "input": {
                "db_name": db_name,
                "db_type": config["db_type"],
                "collection_name": f"{db_name}_Collection",
            }
        },
    )
    assert hasattr(res, "data"), f"create_vector_database_tool failed: {res}"

    # Test create_collection
    res = await client.call_tool(
        "create_collection",
        {
            "input": {
                "db_name": db_name,
                "collection_name": f"{db_name}_Collection",
                "embedding": "default",
            }
        },
    )
    assert hasattr(res, "data"), f"create_collection failed: {res}"

    # Test list_collections
    res = await client.call_tool(
        "list_collections",
        {"input": {"db_name": db_name}}
    )
    assert hasattr(res, "data"), f"list_collections failed: {res}"

    # Test get_collection_info
    res = await client.call_tool(
        "get_collection_info",
        {"input": {"db_name": db_name}}
    )
    assert hasattr(res, "data"), f"get_collection_info failed: {res}"

    # Cleanup
    res = await client.call_tool("cleanup", {"input": {"db_name": db_name}})
    assert hasattr(res, "data"), f"cleanup failed: {res}"


async def run_resync_operations_tests(client: "Client") -> None:
    """Test database resynchronization functionality."""
    # Test resync_databases_tool (note: no input parameter needed)
    res = await client.call_tool("resync_databases_tool")
    assert hasattr(res, "data"), f"resync_databases_tool failed: {res}"

    # Validate the response indicates successful execution
    result_data = res.data if hasattr(res, "data") else ""
    assert isinstance(result_data, (str, dict, list)), f"Unexpected response format: {result_data}"


async def run_configuration_discovery_tests(client: "Client", backend_name: str) -> None:
    """Test configuration discovery operations: get_supported_embeddings, get_supported_chunking_strategies."""
    config = get_backend_config(backend_name)
    db_name = get_db_name_for_test(backend_name, "Config_Test")

    # Create a test database first
    res = await client.call_tool(
        "create_vector_database_tool",
        {
            "input": {
                "db_name": db_name,
                "db_type": config["db_type"],
                "collection_name": db_name,
            }
        },
    )
    assert hasattr(res, "data")

    # Test get_supported_embeddings
    res = await client.call_tool(
        "get_supported_embeddings", {"input": {"db_name": db_name}}
    )
    assert hasattr(res, "data")
    # Should contain embedding options (backend-agnostic check)
    assert res.data and len(str(res.data)) > 0, f"No embeddings returned: {res.data}"

    # Test get_supported_chunking_strategies
    res = await client.call_tool("get_supported_chunking_strategies")
    assert hasattr(res, "data")
    # Should contain chunking strategies
    strategies_mentioned = any(
        strategy in res.data for strategy in ["Fixed", "Sentence", "Semantic"]
    )
    assert strategies_mentioned, f"Expected chunking strategies not found in: {res.data}"

    # Cleanup
    res = await client.call_tool("cleanup", {"input": {"db_name": db_name}})
    assert hasattr(res, "data")