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

import sys
import os
import pytest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.vector_db_base import VectorDatabase


class TestVectorDatabase:
    """Test cases for the VectorDatabase abstract base class."""

    def test_vector_database_abstract(self):
        """Test that VectorDatabase is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            VectorDatabase()


class ConcreteVectorDatabase(VectorDatabase):
    """Concrete implementation for testing abstract methods."""

    def __init__(self, collection_name: str = "TestCollection"):
        super().__init__(collection_name)
        self.documents = []
        self.next_id = 0

    @property
    def db_type(self) -> str:
        return "test"

    def supported_embeddings(self):
        return ["default", "test-embedding"]

    def setup(self):
        pass

    def write_documents(self, documents, embedding="default"):
        for doc in documents:
            doc_copy = doc.copy()
            doc_copy["id"] = str(self.next_id)
            doc_copy["embedding_used"] = embedding
            self.documents.append(doc_copy)
            self.next_id += 1

    def list_documents(self, limit=10, offset=0):
        return self.documents[offset : offset + limit]

    def count_documents(self) -> int:
        return len(self.documents)

    def delete_documents(self, document_ids):
        self.documents = [
            doc for doc in self.documents if doc["id"] not in document_ids
        ]

    def delete_collection(self, collection_name=None):
        target_collection = collection_name or self.collection_name
        if target_collection == self.collection_name:
            self.documents = []
            self.collection_name = None

    def create_query_agent(self):
        return self

    def cleanup(self):
        self.documents = []


class TestConcreteVectorDatabase:
    """Test cases for the concrete implementation of VectorDatabase."""

    def test_supported_embeddings(self):
        """Test the supported_embeddings method."""
        db = ConcreteVectorDatabase()
        embeddings = db.supported_embeddings()
        assert "default" in embeddings
        assert "test-embedding" in embeddings
        assert len(embeddings) == 2

    def test_write_document_singular(self):
        """Test the singular write_document method."""
        db = ConcreteVectorDatabase()
        doc = {"url": "test.com", "text": "test", "metadata": {"key": "value"}}

        db.write_document(doc)
        assert len(db.documents) == 1
        assert db.documents[0]["url"] == "test.com"
        assert db.documents[0]["embedding_used"] == "default"

    def test_write_document_with_embedding(self):
        """Test the write_document method with custom embedding."""
        db = ConcreteVectorDatabase()
        doc = {"url": "test.com", "text": "test", "metadata": {"key": "value"}}

        db.write_document(doc, embedding="test-embedding")
        assert len(db.documents) == 1
        assert db.documents[0]["embedding_used"] == "test-embedding"

    def test_write_documents_with_embedding(self):
        """Test the write_documents method with custom embedding."""
        db = ConcreteVectorDatabase()
        docs = [
            {"url": "test1.com", "text": "test1", "metadata": {}},
            {"url": "test2.com", "text": "test2", "metadata": {}},
        ]

        db.write_documents(docs, embedding="test-embedding")
        assert len(db.documents) == 2
        assert all(doc["embedding_used"] == "test-embedding" for doc in db.documents)

    def test_delete_document_singular(self):
        """Test the singular delete_document method."""
        db = ConcreteVectorDatabase()
        doc = {"url": "test.com", "text": "test", "metadata": {"key": "value"}}

        db.write_document(doc)
        assert len(db.documents) == 1

        db.delete_document("0")
        assert len(db.documents) == 0

    def test_count_documents(self):
        """Test the count_documents method."""
        db = ConcreteVectorDatabase()
        assert db.count_documents() == 0

        doc1 = {"url": "test1.com", "text": "test1", "metadata": {}}
        doc2 = {"url": "test2.com", "text": "test2", "metadata": {}}

        db.write_documents([doc1, doc2])
        assert db.count_documents() == 2

    def test_delete_documents_multiple(self):
        """Test the delete_documents method with multiple IDs."""
        db = ConcreteVectorDatabase()
        doc1 = {"url": "test1.com", "text": "test1", "metadata": {}}
        doc2 = {"url": "test2.com", "text": "test2", "metadata": {}}
        doc3 = {"url": "test3.com", "text": "test3", "metadata": {}}

        db.write_documents([doc1, doc2, doc3])
        assert db.count_documents() == 3

        db.delete_documents(["0", "2"])
        assert db.count_documents() == 1
        assert db.documents[0]["url"] == "test2.com"

    def test_delete_collection(self):
        """Test the delete_collection method."""
        db = ConcreteVectorDatabase("TestCollection")
        doc = {"url": "test.com", "text": "test", "metadata": {}}

        db.write_document(doc)
        assert db.count_documents() == 1
        assert db.collection_name == "TestCollection"

        db.delete_collection()
        assert db.count_documents() == 0
        assert db.collection_name is None

    def test_delete_collection_specific_name(self):
        """Test the delete_collection method with specific collection name."""
        db = ConcreteVectorDatabase("TestCollection")
        doc = {"url": "test.com", "text": "test", "metadata": {}}

        db.write_document(doc)
        assert db.count_documents() == 1

        # Delete a different collection name (should not affect current collection)
        db.delete_collection("DifferentCollection")
        assert db.count_documents() == 1
        assert db.collection_name == "TestCollection"
