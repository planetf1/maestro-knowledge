# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Service integration tests for MCP server with real databases.
These tests require actual Milvus/Weaviate databases to be running.
"""

import pytest
import os
from src.maestro_mcp.server import create_mcp_server, QueryInput


class TestMCPServerServiceIntegration:
    """Service integration tests requiring real databases."""

    def _check_milvus_available(self) -> bool:
        """Check if Milvus is available for testing."""
        # Check if Milvus environment variables are set
        return bool(os.getenv("MILVUS_URI") or os.getenv("MILVUS_HOST"))

    def _check_weaviate_available(self) -> bool:
        """Check if Weaviate environment variables are set."""
        return bool(os.getenv("WEAVIATE_URL") and os.getenv("WEAVIATE_API_KEY"))

    @pytest.mark.service
    @pytest.mark.requires_milvus
    @pytest.mark.slow
    async def test_real_milvus_connection(self) -> None:
        """Test MCP server creation with real Milvus database."""
        if not self._check_milvus_available():
            pytest.skip("Milvus not available - set MILVUS_URI environment variable")

        # Create server without mocking - should connect to real Milvus
        server = await create_mcp_server()

        assert server is not None
        assert server.name == "maestro-vector-db"

        # The server should have auto-discovered existing collections
        # In a real test, we'd verify collections were found:
        # collections_found = len(server.vector_databases) > 0

    @pytest.mark.service
    @pytest.mark.requires_weaviate
    @pytest.mark.slow
    async def test_real_weaviate_connection(self) -> None:
        """Test MCP server creation with real Weaviate database."""
        if not self._check_weaviate_available():
            pytest.skip(
                "Weaviate not available - set WEAVIATE_URL and WEAVIATE_API_KEY"
            )

        # Create server without mocking - should connect to real Weaviate
        server = await create_mcp_server()

        assert server is not None
        assert server.name == "maestro-vector-db"

    @pytest.mark.service
    @pytest.mark.requires_milvus
    @pytest.mark.slow
    async def test_real_query_workflow(self) -> None:
        """Test complete query workflow with real database."""
        if not self._check_milvus_available():
            pytest.skip("Milvus not available")

        server = await create_mcp_server()

        # Create a test collection and query it
        # This would be a real end-to-end test:
        # 1. Create collection
        # 2. Add test documents
        # 3. Query documents
        # 4. Verify results
        # 5. Cleanup

        # For now, just verify server creation
        assert server is not None


class TestRealDatabaseOperations:
    """Test real database operations when databases are available."""

    @pytest.mark.service
    @pytest.mark.requires_milvus
    @pytest.mark.slow
    async def test_milvus_collection_operations(self) -> None:
        """Test Milvus collection creation, querying, and cleanup."""
        # This would test the full workflow:
        # 1. Create MCP server (connects to real Milvus)
        # 2. Create a test collection
        # 3. Add test documents
        # 4. Query the collection
        # 5. Verify results
        # 6. Delete the test collection
        pytest.skip("Real database operations test - implement when needed")

    @pytest.mark.service
    @pytest.mark.requires_weaviate
    @pytest.mark.slow
    async def test_weaviate_collection_operations(self) -> None:
        """Test Weaviate collection creation, querying, and cleanup."""
        # Similar to Milvus test but for Weaviate
        pytest.skip("Real database operations test - implement when needed")
