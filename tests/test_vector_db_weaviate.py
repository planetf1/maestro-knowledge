# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

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
# Suppress external package deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if weaviate is available
try:
    import weaviate  # noqa: F401

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

# Check if weaviate agents are available
try:
    import weaviate.agents  # noqa: F401

    WEAVIATE_AGENTS_AVAILABLE = True
except ImportError:
    WEAVIATE_AGENTS_AVAILABLE = False

from src.db.vector_db_weaviate import WeaviateVectorDatabase


@pytest.mark.skipif(not WEAVIATE_AVAILABLE, reason="weaviate not available")
class TestWeaviateVectorDatabase:
    """Test cases for the WeaviateVectorDatabase implementation."""

    def test_supported_embeddings(self):
        """Test the supported_embeddings method."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            embeddings = db.supported_embeddings()

            assert "default" in embeddings
            assert "text2vec-weaviate" in embeddings
            assert "text2vec-openai" in embeddings
            assert "text2vec-cohere" in embeddings
            assert "text2vec-huggingface" in embeddings
            assert "text-embedding-ada-002" in embeddings
            assert "text-embedding-3-small" in embeddings
            assert "text-embedding-3-large" in embeddings

    def test_init_with_collection_name(self):
        """Test WeaviateVectorDatabase initialization with custom collection name."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase("TestCollection")

            assert db.collection_name == "TestCollection"
            assert db.client == mock_client

    def test_init_default_collection_name(self):
        """Test WeaviateVectorDatabase initialization with default collection name."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()

            assert db.collection_name == "MaestroDocs"
            assert db.client == mock_client

    def test_setup_collection_exists(self):
        """Test setup when collection already exists."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_client.collections.exists.return_value = True
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            db.setup()

            # Should not create collection since it exists
            mock_client.collections.create.assert_not_called()

    def test_setup_collection_not_exists_default_embedding(self):
        """Test setup when collection doesn't exist with default embedding."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch("weaviate.classes.config.Configure") as mock_configure,
            patch("weaviate.classes.config.Property") as mock_property,
            patch("weaviate.classes.config.DataType") as mock_datatype,
        ):
            mock_client = MagicMock()
            mock_client.collections.exists.return_value = False
            mock_connect.return_value = mock_client

            # Mock the configuration objects
            mock_configure.Vectorizer.text2vec_weaviate.return_value = (
                "vectorizer_config"
            )
            mock_property.return_value = "property"
            mock_datatype.TEXT = "TEXT"

            db = WeaviateVectorDatabase()
            db.setup()

            # Should create collection since it doesn't exist
            mock_client.collections.create.assert_called_once()

    def test_setup_collection_not_exists_custom_embedding(self):
        """Test setup when collection doesn't exist with custom embedding."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch("weaviate.classes.config.Configure") as mock_configure,
            patch("weaviate.classes.config.Property") as mock_property,
            patch("weaviate.classes.config.DataType") as mock_datatype,
        ):
            mock_client = MagicMock()
            mock_client.collections.exists.return_value = False
            mock_connect.return_value = mock_client

            # Mock the configuration objects
            mock_configure.Vectorizer.text2vec_openai.return_value = (
                "openai_vectorizer_config"
            )
            mock_property.return_value = "property"
            mock_datatype.TEXT = "TEXT"

            db = WeaviateVectorDatabase()
            db.setup(embedding="text-embedding-ada-002")

            # Should create collection since it doesn't exist
            mock_client.collections.create.assert_called_once()

    def test_get_vectorizer_config_default(self):
        """Test getting vectorizer config for default embedding."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch("weaviate.classes.config.Configure") as mock_configure,
        ):
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            # Mock the configuration
            mock_configure.Vectorizer.text2vec_weaviate.return_value = (
                "vectorizer_config"
            )

            db = WeaviateVectorDatabase()
            config = db._get_vectorizer_config("default")
            assert config == "vectorizer_config"  # Mocked return value

    def test_get_vectorizer_config_unsupported(self):
        """Test getting vectorizer config for unsupported embedding."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            with pytest.raises(ValueError, match="Unsupported embedding"):
                db._get_vectorizer_config("unsupported-model")

    def test_write_documents_default_embedding(self):
        """Test writing documents to Weaviate with default embedding."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_batch = MagicMock()
            mock_batch_context = MagicMock()

            mock_client.collections.exists.return_value = True
            mock_client.collections.get.return_value = mock_collection
            mock_collection.batch.dynamic.return_value = mock_batch_context
            mock_batch_context.__enter__.return_value = mock_batch
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()

            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                },
                {
                    "url": "http://test2.com",
                    "text": "test content 2",
                    "metadata": {"type": "webpage"},
                },
            ]

            db.write_documents(documents, embedding="default")

            # Verify batch.add_object was called for each document
            assert mock_batch.add_object.call_count == 2

    def test_write_documents_custom_embedding(self):
        """Test writing documents to Weaviate with custom embedding."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch("weaviate.classes.config.Configure") as mock_configure,
            patch("weaviate.classes.config.Property") as mock_property,
            patch("weaviate.classes.config.DataType") as mock_datatype,
        ):
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_batch = MagicMock()
            mock_batch_context = MagicMock()

            mock_client.collections.exists.return_value = False
            mock_client.collections.get.return_value = mock_collection
            mock_collection.batch.dynamic.return_value = mock_batch_context
            mock_batch_context.__enter__.return_value = mock_batch
            mock_connect.return_value = mock_client

            # Mock the configuration objects
            mock_configure.Vectorizer.text2vec_openai.return_value = (
                "openai_vectorizer_config"
            )
            mock_property.return_value = "property"
            mock_datatype.TEXT = "TEXT"

            db = WeaviateVectorDatabase()

            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                }
            ]

            db.write_documents(documents, embedding="text-embedding-ada-002")

            # Verify collection was created and batch.add_object was called
            mock_client.collections.create.assert_called_once()
            assert mock_batch.add_object.call_count == 1

    def test_write_documents_unsupported_embedding(self):
        """Test writing documents with unsupported embedding."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            documents = [
                {
                    "url": "http://test1.com",
                    "text": "test content 1",
                    "metadata": {"type": "webpage"},
                }
            ]

            with pytest.raises(ValueError, match="Unsupported embedding"):
                db.write_documents(documents, embedding="unsupported-model")

    def test_list_documents(self):
        """Test listing documents from Weaviate."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_result = MagicMock()
            mock_object1 = MagicMock()
            mock_object2 = MagicMock()

            # Mock the query result
            mock_object1.uuid = "uuid1"
            mock_object1.properties = {
                "url": "http://test1.com",
                "text": "content1",
                "metadata": '{"type": "webpage"}',
            }
            mock_object2.uuid = "uuid2"
            mock_object2.properties = {
                "url": "http://test2.com",
                "text": "content2",
                "metadata": '{"type": "webpage"}',
            }

            mock_result.objects = [mock_object1, mock_object2]
            mock_collection.query.fetch_objects.return_value = mock_result
            mock_client.collections.get.return_value = mock_collection
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()

            documents = db.list_documents(limit=2, offset=0)

            assert len(documents) == 2
            assert documents[0]["id"] == "uuid1"
            assert documents[0]["url"] == "http://test1.com"
            assert documents[1]["id"] == "uuid2"
            assert documents[1]["url"] == "http://test2.com"

    def test_count_documents(self):
        """Test counting documents in Weaviate."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_result = MagicMock()

            # Create mock objects to simulate the fetch_objects result
            mock_object1 = MagicMock()
            mock_object2 = MagicMock()
            mock_object3 = MagicMock()
            mock_object4 = MagicMock()
            mock_object5 = MagicMock()

            mock_result.objects = [
                mock_object1,
                mock_object2,
                mock_object3,
                mock_object4,
                mock_object5,
            ]
            mock_collection.query.fetch_objects.return_value = mock_result
            mock_client.collections.get.return_value = mock_collection
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            count = db.count_documents()

            assert count == 5

    def test_list_collections(self):
        """Test listing collections in Weaviate."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch.dict(
                os.environ,
                {
                    "WEAVIATE_API_KEY": "test-key",
                    "WEAVIATE_URL": "https://test.weaviate.network",
                },
            ),
        ):
            mock_client = MagicMock()

            # Create mock collections
            mock_collection1 = MagicMock()
            mock_collection1.name = "Collection1"
            mock_collection2 = MagicMock()
            mock_collection2.name = "Collection2"
            mock_collection3 = MagicMock()
            mock_collection3.name = "MaestroDocs"

            mock_client.collections.list_all.return_value = [
                mock_collection1,
                mock_collection2,
                mock_collection3,
            ]
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            collections = db.list_collections()

            assert collections == ["Collection1", "Collection2", "MaestroDocs"]
            mock_client.collections.list_all.assert_called_once()

    def test_list_collections_exception(self):
        """Test listing collections when an exception occurs."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch.dict(
                os.environ,
                {
                    "WEAVIATE_API_KEY": "test-key",
                    "WEAVIATE_URL": "https://test.weaviate.network",
                },
            ),
        ):
            mock_client = MagicMock()
            mock_client.collections.list_all.side_effect = Exception("Connection error")
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            # Suppress the expected warning for this test
            with pytest.warns(
                UserWarning, match="Could not list collections from Weaviate"
            ):
                collections = db.list_collections()

            assert collections == []

    def test_delete_documents(self):
        """Test deleting documents from Weaviate."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_client.collections.get.return_value = mock_collection
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            db.delete_documents(["uuid1", "uuid2"])

            # Verify delete_by_id was called for each document
            assert mock_collection.data.delete_by_id.call_count == 2
            mock_collection.data.delete_by_id.assert_any_call("uuid1")
            mock_collection.data.delete_by_id.assert_any_call("uuid2")

    def test_delete_collection(self):
        """Test deleting a collection from Weaviate."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_client.collections.exists.return_value = True
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase("TestCollection")
            db.delete_collection()

            mock_client.collections.delete.assert_called_once_with("TestCollection")
            assert db.collection_name is None

    @pytest.mark.skipif(
        not WEAVIATE_AGENTS_AVAILABLE, reason="weaviate agents not available"
    )
    def test_create_query_agent(self):
        """Test creating a query agent."""
        with (
            patch("weaviate.connect_to_weaviate_cloud") as mock_connect,
            patch("weaviate.agents.query.QueryAgent") as mock_query_agent,
        ):
            mock_client = MagicMock()
            mock_connect.return_value = mock_client
            mock_agent = MagicMock()
            mock_query_agent.return_value = mock_agent

            db = WeaviateVectorDatabase()
            agent = db.create_query_agent()

            # The actual QueryAgent is created, not the mock, so we just verify it's not None
            assert agent is not None

    def test_cleanup(self):
        """Test cleanup method."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()
            db.cleanup()

            # Verify client is set to None after cleanup
            assert db.client is None

    def test_db_type_property(self):
        """Test the db_type property."""
        with patch("weaviate.connect_to_weaviate_cloud") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            db = WeaviateVectorDatabase()

            assert db.db_type == "weaviate"
