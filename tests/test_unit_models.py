# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Unit tests for MCP server models and basic functionality.
These tests should run fast with no external dependencies.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock
from src.maestro_mcp.server import QueryInput


@pytest.mark.unit
class TestQueryInputModel:
    """Unit tests for QueryInput Pydantic model."""

    @pytest.mark.unit
    def test_query_input_valid(self) -> None:
        """Test QueryInput with valid parameters."""
        query_input = QueryInput(
            db_name="test-db", query="What is the main topic?", limit=10
        )

        assert query_input.db_name == "test-db"
        assert query_input.query == "What is the main topic?"
        assert query_input.limit == 10

    @pytest.mark.unit
    def test_query_input_defaults(self) -> None:
        """Test QueryInput with default values."""
        query_input = QueryInput(db_name="test-db", query="Test query")

        assert query_input.db_name == "test-db"
        assert query_input.query == "Test query"
        assert query_input.limit == 5  # Default value

    @pytest.mark.unit
    def test_query_input_validation_missing_db_name(self) -> None:
        """Test QueryInput validation fails when db_name is missing."""
        with pytest.raises(ValueError):
            QueryInput(query="test")  # type: ignore[call-arg]

    @pytest.mark.unit
    def test_query_input_validation_missing_query(self) -> None:
        """Test QueryInput validation fails when query is missing."""
        with pytest.raises(ValueError):
            QueryInput(db_name="test-db")  # type: ignore[call-arg]

    @pytest.mark.unit
    def test_query_input_special_characters(self) -> None:
        """Test QueryInput handles special characters properly."""
        special_query = "What's the deal with API endpoints? (v2.0) & more!"
        query_input = QueryInput(db_name="test-db", query=special_query, limit=5)

        assert query_input.db_name == "test-db"
        assert query_input.query == special_query
        assert query_input.limit == 5

    @pytest.mark.unit
    @pytest.mark.parametrize("limit", [1, 5, 10, 100])
    def test_query_input_different_limits(self, limit: int) -> None:
        """Test QueryInput with different limit values."""
        query_input = QueryInput(db_name="test-db", query="Test query", limit=limit)

        assert query_input.db_name == "test-db"
        assert query_input.query == "Test query"
        assert query_input.limit == limit
