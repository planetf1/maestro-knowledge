# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import warnings

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

# Suppress Milvus connection warnings during tests
warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*Failed to connect to Milvus.*"
)
warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*Milvus client is not available.*"
)

import sys  # noqa: E402
import os  # noqa: E402

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the new modular structure
from src.vector_db_base import VectorDatabase  # noqa: E402
from src.vector_db_weaviate import WeaviateVectorDatabase  # noqa: E402
from src.vector_db_milvus import MilvusVectorDatabase  # noqa: E402
from src.vector_db_factory import create_vector_database  # noqa: E402

# Check if pymilvus is available
try:
    import pymilvus  # noqa: F401

    PYMILVUS_AVAILABLE = True
except ImportError:
    PYMILVUS_AVAILABLE = False


# This file now serves as a compatibility layer and re-exports the tests
# The actual test implementations are in the separate test files:
# - test_vector_db_base.py
# - test_vector_db_weaviate.py
# - test_vector_db_milvus.py
# - test_vector_db_factory.py

# Re-export for backward compatibility
__all__ = [
    "VectorDatabase",
    "WeaviateVectorDatabase",
    "MilvusVectorDatabase",
    "create_vector_database",
    "PYMILVUS_AVAILABLE",
]
