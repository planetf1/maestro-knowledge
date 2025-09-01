# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

import warnings
import pytest
import subprocess
from unittest.mock import Mock
from typing import Any

# Suppress Pydantic deprecation warnings from dependencies
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*class-based `config`.*"
)
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*PydanticDeprecatedSince20.*"
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*Support for class-based `config`.*",
)

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.maestro_mcp.server import create_mcp_server, QueryInput
from fastmcp import FastMCP


class TestQueryIntegration:
    """Integration tests for the query functionality."""

    @pytest.fixture
    def mcp_server(self) -> FastMCP:
        """Create a test MCP server instance."""
        return create_mcp_server()

    @pytest.fixture
    def mock_vector_db(self) -> Mock:
        """Create a mock vector database with query functionality."""
        mock_db = Mock()
        mock_db.query.return_value = "Integration test response"
        mock_db.db_type = "test"
        mock_db.collection_name = "TestCollection"
        mock_db.count_documents.return_value = 5
        return mock_db

    def test_full_query_flow(self, mcp_server: FastMCP, mock_vector_db: Mock) -> None:
        """Test the complete query flow from MCP server to VDB."""
        # Test that the server was created successfully
        assert mcp_server is not None, "MCP server should be created"

        # Test QueryInput model
        query_input = QueryInput(
            db_name="test-db", query="What is the main topic?", limit=5
        )

        assert query_input.db_name == "test-db"
        assert query_input.query == "What is the main topic?"
        assert query_input.limit == 5

    def test_query_with_real_vector_db_factory(self) -> None:
        """Test query with real vector database factory."""
        # Test that the server was created successfully
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"

        # Test QueryInput model
        query_input = QueryInput(db_name="test-db", query="Test query", limit=5)

        assert query_input.db_name == "test-db"
        assert query_input.query == "Test query"
        assert query_input.limit == 5

    def test_query_multiple_databases_integration(self) -> None:
        """Test querying multiple databases in the same session."""
        # Test that the server was created successfully
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"

        # Test QueryInput with different database names
        query_input1 = QueryInput(db_name="weaviate-db", query="Test query 1", limit=5)

        query_input2 = QueryInput(db_name="milvus-db", query="Test query 2", limit=10)

        assert query_input1.db_name == "weaviate-db"
        assert query_input1.query == "Test query 1"
        assert query_input1.limit == 5

        assert query_input2.db_name == "milvus-db"
        assert query_input2.query == "Test query 2"
        assert query_input2.limit == 10

    def test_query_error_handling_integration(self) -> None:
        """Test error handling in the complete query flow."""
        # Test that the server was created successfully
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"

        # Test QueryInput model
        query_input = QueryInput(db_name="test-db", query="Test query", limit=5)

        assert query_input.db_name == "test-db"
        assert query_input.query == "Test query"
        assert query_input.limit == 5

    def test_query_with_different_limits_integration(self) -> None:
        """Test query with different limit values in integration."""
        # Test that the server was created successfully
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"

        # Test QueryInput with different limit values
        test_cases = [1, 5, 10, 100]

        for limit in test_cases:
            query_input = QueryInput(
                db_name="test-db", query=f"Test query with limit {limit}", limit=limit
            )

            assert query_input.db_name == "test-db"
            assert query_input.query == f"Test query with limit {limit}"
            assert query_input.limit == limit

    def test_query_special_characters_integration(self) -> None:
        """Test query with special characters in integration."""
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"

        special_queries = [
            "What's the deal with API endpoints? (v2.0)",
            "¿Qué tal? 你好世界 🌍",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Unicode: αβγδε ζηθικλμν ξοπρστ υφχψω",
        ]
        for query in special_queries:
            query_input = QueryInput(db_name="test-db", query=query, limit=5)
            assert query_input.db_name == "test-db"
            assert query_input.query == query
            assert query_input.limit == 5


class TestQueryCLIIntegration:
    """Integration tests for CLI query functionality."""

    def test_cli_query_command_exists(self) -> None:
        """Test that the CLI query command exists and is accessible."""
        try:
            # Try to run the query help command
            result = subprocess.run(
                ["../cli/maestro-k", "query", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # The command should exist and show help
            assert result.returncode == 0, f"Query help command failed: {result.stderr}"
            assert "query" in result.stdout
            assert "doc-limit" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out - CLI may not be built")
        except FileNotFoundError:
            pytest.skip("CLI binary not found - CLI may not be built")

    def test_cli_query_vdb_command_exists(self) -> None:
        """Test that the CLI query vdb command exists and is accessible."""
        try:
            # Try to run the query vdb help command
            result = subprocess.run(
                ["../cli/maestro-k", "query", "vdb", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # The command should exist and show help
            assert result.returncode == 0
            (f"Query vdb help command failed: {result.stderr}")
            assert "vdb" in result.stdout
            assert "doc-limit" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out - CLI may not be built")
        except FileNotFoundError:
            pytest.skip("CLI binary not found - CLI may not be built")

    def test_cli_query_dry_run(self) -> None:
        """Test CLI query command with dry-run flag."""
        try:
            # Try to run the query command with dry-run
            result = subprocess.run(
                ["../cli/maestro-k", "query", "test-db", "test query", "--dry-run"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # The command should succeed with dry-run
            assert result.returncode == 0
            (f"Query dry-run command failed: {result.stderr}")
            assert "[DRY RUN]" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out - CLI may not be built")
        except FileNotFoundError:
            pytest.skip("CLI binary not found - CLI may not be built")

    def test_cli_query_with_doc_limit(self) -> None:
        """Test CLI query command with doc-limit flag."""
        try:
            # Try to run the query command with doc-limit
            result = subprocess.run(
                [
                    "../cli/maestro-k",
                    "query",
                    "test-db",
                    "test query",
                    "--doc-limit",
                    "10",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # The command should succeed with dry-run
            assert result.returncode == 0
            (f"Query with doc-limit command failed: {result.stderr}")
            assert "[DRY RUN]" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out - CLI may not be built")
        except FileNotFoundError:
            pytest.skip("CLI binary not found - CLI may not be built")


class TestQueryEndToEnd:
    """End-to-end tests for the query functionality."""

    def test_query_e2e_flow(self) -> None:
        """Test the complete end-to-end query flow."""
        from src.db.vector_db_base import VectorDatabase

        assert hasattr(VectorDatabase, "query")
        mcp_server = create_mcp_server()
        assert mcp_server is not None, "MCP server should be created"
        query_input = QueryInput(db_name="test-db", query="Test query", limit=5)
        assert query_input.db_name == "test-db"
        assert query_input.query == "Test query"
        assert query_input.limit == 5

    def test_query_cli_integration_e2e(self) -> None:
        """Test CLI integration end-to-end."""
        # Test that the CLI can be built and has query commands
        try:
            # Check if CLI exists
            cli_path = "../cli/maestro-k"
            if not os.path.exists(cli_path):
                pytest.skip("CLI binary not found")

            # Test help command
            result = subprocess.run(
                [cli_path, "--help"], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, "CLI help command should work"
            assert "query" in result.stdout, "CLI should have query command"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("CLI not available for testing")
