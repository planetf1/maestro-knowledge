# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import warnings
from abc import ABC, abstractmethod
from typing import List, Dict, Any

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


class VectorDatabase(ABC):
    """Abstract base class for vector database implementations."""

    @abstractmethod
    def __init__(self, collection_name: str = "MaestroDocs"):
        """Initialize the vector database with a collection name."""
        self.collection_name = collection_name

    @property
    @abstractmethod
    def db_type(self) -> str:
        """Return the type/name of the vector database."""
        pass

    @abstractmethod
    def setup(self):
        """Set up the database and create collections if they don't exist."""
        pass

    @abstractmethod
    def write_documents(self, documents: List[Dict[str, Any]]):
        """
        Write documents to the vector database.

        Args:
            documents: List of documents with 'url', 'text', and 'metadata' fields
        """
        pass

    def write_document(self, document: Dict[str, Any]):
        """
        Write a single document to the vector database.

        Args:
            document: Document with 'url', 'text', and 'metadata' fields
        """
        return self.write_documents([document])

    @abstractmethod
    def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents from the vector database.

        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of documents with their properties
        """
        pass

    @abstractmethod
    def count_documents(self) -> int:
        """
        Get the current count of documents in the collection.

        Returns:
            Number of documents in the collection
        """
        pass

    @abstractmethod
    def delete_documents(self, document_ids: List[str]):
        """
        Delete documents from the vector database by their IDs.

        Args:
            document_ids: List of document IDs to delete
        """
        pass

    def delete_document(self, document_id: str):
        """
        Delete a single document from the vector database by its ID.

        Args:
            document_id: Document ID to delete
        """
        return self.delete_documents([document_id])

    @abstractmethod
    def delete_collection(self, collection_name: str = None):
        """
        Delete an entire collection from the database.

        Args:
            collection_name: Name of the collection to delete. If None, uses the current collection.
        """
        pass

    @abstractmethod
    def create_query_agent(self):
        """Create and return a query agent for this vector database."""
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up resources and close connections."""
        pass
