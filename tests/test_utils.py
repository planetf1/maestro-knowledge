# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Test utilities for maestro-knowledge tests.
Provides common mocking functionality to prevent database connections during tests.
"""

from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def mock_resync_functions() -> Generator[None, None, None]:
    """
    Context manager that mocks both resync functions to prevent database connections during tests.
    
    This prevents tests from hanging when they try to connect to Milvus or Weaviate databases
    that aren't running during the test execution.
    
    Usage:
        with mock_resync_functions():
            server = await create_mcp_server()
    """
    with patch("src.maestro_mcp.server.resync_vector_databases", return_value=[]):
        with patch("src.maestro_mcp.server.resync_weaviate_databases", return_value=[]):
            yield