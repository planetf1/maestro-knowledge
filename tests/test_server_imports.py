# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""Test that server imports work correctly after fixing relative import issues."""

import pytest

pytestmark = pytest.mark.unit


def test_server_imports_absolute() -> None:
    """Test that server.py imports work with absolute imports."""
    try:
        from src.maestro_mcp.server import create_mcp_server, run_http_server_sync

        assert callable(create_mcp_server)
        assert callable(run_http_server_sync)
    except ImportError as e:
        pytest.fail(f"Server import failed: {e}")


def test_chunking_imports() -> None:
    """Test that chunking imports work."""
    try:
        from src.chunking import ChunkingConfig

        config = ChunkingConfig()
        assert config is not None
    except ImportError as e:
        pytest.fail(f"Chunking import failed: {e}")


def test_db_imports() -> None:
    """Test that vector DB imports work."""
    try:
        from src.db.vector_db_factory import create_vector_database

        assert callable(create_vector_database)
    except ImportError as e:
        pytest.fail(f"DB import failed: {e}")
