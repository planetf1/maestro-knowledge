# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

"""
Vector Database Abstraction Layer

This package provides a unified interface for working with different vector databases.
"""

from .vector_db_base import VectorDatabase
from .vector_db_factory import create_vector_database
from .vector_db_milvus import MilvusVectorDatabase
from .vector_db_weaviate import WeaviateVectorDatabase

__all__ = [
    "VectorDatabase",
    "create_vector_database", 
    "MilvusVectorDatabase",
    "WeaviateVectorDatabase",
] 