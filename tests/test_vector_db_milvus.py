# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

import warnings

# Suppress all deprecation warnings from external packages immediately
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
# Suppress external package deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.vector_db_milvus import MilvusVectorDatabase


class TestMilvusVectorDatabase:
    """Test cases for the MilvusVectorDatabase implementation."""

    def test_supported_embeddings(self):
        """Test the supported_embeddings method."""
        db = MilvusVectorDatabase()
        embeddings = db.supported_embeddings()
        assert "default" in embeddings
        assert "text-embedding-ada-002" in embeddings
        assert "text-embedding-3-small" in embeddings
        assert "text-embedding-3-large" in embeddings

    @patch("pymilvus.MilvusClient")
    def test_init_with_collection_name(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase("TestCollection")
        assert db.collection_name == "TestCollection"
        # Client is not created until needed due to lazy initialization
        assert db.client is None
        # Trigger client creation
        db._ensure_client()
        assert db.client == mock_client

    @patch("pymilvus.MilvusClient")
    def test_setup_collection_exists(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.has_collection.return_value = True
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        db.setup()
        mock_client.create_collection.assert_not_called()

    @patch("pymilvus.MilvusClient")
    def test_setup_collection_not_exists(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.has_collection.return_value = False
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        db.setup()
        mock_client.create_collection.assert_called_once()

    @patch("pymilvus.MilvusClient")
    def test_write_documents_with_precomputed_vector(self, mock_milvus_client):
        """Test writing documents with pre-computed vectors."""
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        documents = [
            {
                "url": "http://test1.com",
                "text": "test content 1",
                "metadata": {"type": "webpage"},
                "vector": [0.1] * 1536,
            },
            {
                "url": "http://test2.com",
                "text": "test content 2",
                "metadata": {"type": "webpage"},
                "vector": [0.2] * 1536,
            },
        ]
        db.write_documents(documents, embedding="default")
        assert mock_client.insert.called

    @patch("pymilvus.MilvusClient")
    def test_write_documents_with_embedding_model(self, mock_milvus_client):
        """Test writing documents with embedding model generation."""
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client

        db = MilvusVectorDatabase()

        # Mock the _generate_embedding method to return a test vector
        with patch.object(db, "_generate_embedding", return_value=[0.1] * 1536):
            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                }
            ]

            # Set environment variable for OpenAI API key
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                db.write_documents(documents, embedding="text-embedding-ada-002")
                assert mock_client.insert.called

    @patch("pymilvus.MilvusClient")
    def test_write_documents_unsupported_embedding(self, mock_milvus_client):
        """Test writing documents with unsupported embedding model."""
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        documents = [
            {
                "url": "http://test1.com",
                "text": "test content 1",
                "metadata": {"type": "webpage"},
            }
        ]
        with pytest.raises(ValueError, match="Unsupported embedding"):
            db.write_documents(documents, embedding="unsupported-model")

    @patch("pymilvus.MilvusClient")
    def test_write_documents_missing_openai_key(self, mock_milvus_client):
        """Test writing documents without OpenAI API key."""
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()

        # Mock the _generate_embedding method to simulate missing openai module
        with patch.object(
            db,
            "_generate_embedding",
            side_effect=ImportError("No module named 'openai'"),
        ):
            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                }
            ]

            # Ensure no OpenAI API key is set
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ImportError, match="No module named 'openai'"):
                    db.write_documents(documents, embedding="text-embedding-ada-002")

    @patch("pymilvus.MilvusClient")
    def test_write_documents_real_openai_integration(self, mock_milvus_client):
        """Test writing documents with real OpenAI integration when available."""
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()

        # Only run this test if openai module is available
        import importlib.util

        if importlib.util.find_spec("openai") is None:
            pytest.skip("openai module not available")

        # Mock the OpenAI client to return a test embedding
        with patch("openai.OpenAI") as mock_openai:
            mock_client_instance = MagicMock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.embeddings.create.return_value.data = [
                MagicMock(embedding=[0.1] * 1536)
            ]

            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                }
            ]

            # Set environment variable for OpenAI API key
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                db.write_documents(documents, embedding="text-embedding-ada-002")
                assert mock_client.insert.called
                # Verify that the OpenAI client was called correctly
                mock_openai.assert_called_once_with(api_key="test-key")
                mock_client_instance.embeddings.create.assert_called_once_with(
                    model="text-embedding-ada-002", input="test content 1"
                )

    @patch("pymilvus.MilvusClient")
    def test_list_documents(self, mock_milvus_client):
        mock_client = MagicMock()
        # Milvus query returns a list of dictionaries directly
        mock_client.query.return_value = [
            {
                "id": 1,
                "url": "http://test1.com",
                "text": "content1",
                "metadata": '{"type": "webpage"}',
            },
            {
                "id": 2,
                "url": "http://test2.com",
                "text": "content2",
                "metadata": '{"type": "webpage"}',
            },
        ]
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        docs = db.list_documents(limit=2)
        assert len(docs) == 2
        assert docs[0]["id"] == 1
        assert docs[0]["url"] == "http://test1.com"

    @patch("pymilvus.MilvusClient")
    def test_count_documents(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.get_collection_stats.return_value = {"row_count": 5}
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        count = db.count_documents()
        assert count == 5

    @patch("pymilvus.MilvusClient")
    def test_list_collections(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.list_collections.return_value = [
            "Collection1",
            "Collection2",
            "MaestroDocs",
        ]
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        collections = db.list_collections()
        assert collections == ["Collection1", "Collection2", "MaestroDocs"]
        mock_client.list_collections.assert_called_once()

    @patch("pymilvus.MilvusClient")
    def test_list_collections_exception(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.list_collections.side_effect = Exception("Connection error")
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        # Suppress the expected warning for this test
        with pytest.warns(UserWarning, match="Could not list collections from Milvus"):
            collections = db.list_collections()
        assert collections == []

    @patch("pymilvus.MilvusClient")
    def test_list_collections_no_client(self, mock_milvus_client):
        mock_milvus_client.return_value = None
        db = MilvusVectorDatabase()
        # Suppress the expected warning for this test
        with pytest.warns(UserWarning, match="Milvus client is not available"):
            collections = db.list_collections()
        assert collections == []

    @patch("pymilvus.MilvusClient")
    def test_delete_documents(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        db.delete_documents(["1", "2", "3"])
        mock_client.delete.assert_called_once_with(db.collection_name, ids=[1, 2, 3])

    @patch("pymilvus.MilvusClient")
    def test_delete_documents_invalid_ids(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        with pytest.raises(
            ValueError, match="Milvus document IDs must be convertible to integers"
        ):
            db.delete_documents(["1", "invalid", "3"])

    @patch("pymilvus.MilvusClient")
    def test_delete_collection(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_client.has_collection.return_value = True
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase("TestCollection")
        db.delete_collection()
        mock_client.drop_collection.assert_called_once_with("TestCollection")
        assert db.collection_name is None

    @patch("pymilvus.MilvusClient")
    def test_cleanup(self, mock_milvus_client):
        mock_client = MagicMock()
        mock_milvus_client.return_value = mock_client
        db = MilvusVectorDatabase()
        db.cleanup()
        assert db.client is None

    def test_db_type_property(self):
        """Test the db_type property."""
        db = MilvusVectorDatabase()
        assert db.db_type == "milvus"

    @patch("pymilvus.MilvusClient")
    def test_get_document_success(self, mock_milvus_client):
        """Test successfully getting a document by name."""
        mock_client = MagicMock()
        mock_client.has_collection.return_value = True
        mock_client.query.return_value = [
            {
                "id": "doc123",
                "url": "test_url",
                "text": "test content",
                "metadata": '{"doc_name": "test_doc", "collection_name": "test_collection"}',
            }
        ]
        mock_milvus_client.return_value = mock_client

        db = MilvusVectorDatabase()
        result = db.get_document("test_doc", "test_collection")

        assert result["id"] == "doc123"
        assert result["url"] == "test_url"
        assert result["text"] == "test content"
        assert result["metadata"]["doc_name"] == "test_doc"
        assert result["metadata"]["collection_name"] == "test_collection"

        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once_with(
            "test_collection",
            filter='metadata["doc_name"] == "test_doc"',
            output_fields=["id", "url", "text", "metadata"],
            limit=1,
        )

    @patch("pymilvus.MilvusClient")
    def test_get_document_collection_not_found(self, mock_milvus_client):
        """Test getting a document when collection doesn't exist."""
        mock_client = MagicMock()
        mock_client.has_collection.return_value = False
        mock_milvus_client.return_value = mock_client

        db = MilvusVectorDatabase()

        with pytest.raises(ValueError, match="Collection 'test_collection' not found"):
            db.get_document("test_doc", "test_collection")

    @patch("pymilvus.MilvusClient")
    def test_get_document_document_not_found(self, mock_milvus_client):
        """Test getting a document when document doesn't exist."""
        mock_client = MagicMock()
        mock_client.has_collection.return_value = True
        mock_client.query.return_value = []  # No documents found
        mock_milvus_client.return_value = mock_client

        db = MilvusVectorDatabase()

        with pytest.raises(
            ValueError,
            match="Document 'test_doc' not found in collection 'test_collection'",
        ):
            db.get_document("test_doc", "test_collection")

    @patch("pymilvus.MilvusClient")
    def test_get_document_no_client(self, mock_milvus_client):
        """Test getting a document when client is not available."""
        mock_milvus_client.side_effect = Exception("Connection failed")

        db = MilvusVectorDatabase()

        with pytest.raises(ValueError, match="Milvus client is not available"):
            db.get_document("test_doc", "test_collection")

    @patch("pymilvus.MilvusClient")
    def test_get_document_invalid_metadata(self, mock_milvus_client):
        """Test getting a document with invalid metadata JSON."""
        mock_client = MagicMock()
        mock_client.has_collection.return_value = True
        mock_client.query.return_value = [
            {
                "id": "doc123",
                "url": "test_url",
                "text": "test content",
                "metadata": "invalid json",
            }
        ]
        mock_milvus_client.return_value = mock_client

        db = MilvusVectorDatabase()
        result = db.get_document("test_doc", "test_collection")

        # Should handle invalid JSON gracefully
        assert result["id"] == "doc123"
        assert result["url"] == "test_url"
        assert result["text"] == "test content"
        assert result["metadata"] == {}  # Should be empty dict for invalid JSON
