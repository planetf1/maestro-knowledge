# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import json
import warnings
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

from .vector_db_base import VectorDatabase


class WeaviateVectorDatabase(VectorDatabase):
    """Weaviate implementation of the vector database interface."""

    def __init__(self, collection_name: str = "MaestroDocs"):
        super().__init__(collection_name)
        self.client = None
        self._create_client()

    def supported_embeddings(self) -> List[str]:
        """
        Return a list of supported embedding model names for Weaviate.

        Weaviate supports various vectorizers and can also work with external
        embedding services.

        Returns:
            List of supported embedding model names
        """
        return [
            "default",  # Uses text2vec-weaviate
            "text2vec-weaviate",
            "text2vec-openai",
            "text2vec-cohere",
            "text2vec-huggingface",
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]

    def _create_client(self):
        """Create the Weaviate client."""
        import os
        import weaviate
        from weaviate.auth import Auth

        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        weaviate_url = os.getenv("WEAVIATE_URL")

        if not weaviate_api_key:
            raise ValueError("WEAVIATE_API_KEY is not set")
        if not weaviate_url:
            raise ValueError("WEAVIATE_URL is not set")

        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(weaviate_api_key),
        )

    def _get_vectorizer_config(self, embedding: str):
        """
        Get the appropriate vectorizer configuration for the embedding model.

        Args:
            embedding: Name of the embedding model to use

        Returns:
            Vectorizer configuration object
        """
        from weaviate.classes.config import Configure

        # Map embedding names to Weaviate vectorizer configurations
        vectorizer_mapping = {
            "default": Configure.Vectorizer.text2vec_weaviate(),
            "text2vec-weaviate": Configure.Vectorizer.text2vec_weaviate(),
            "text2vec-openai": Configure.Vectorizer.text2vec_openai(
                model="text-embedding-ada-002",
                model_version="002",
                type_="text",
                vectorize_collection_name=False,
            ),
            "text2vec-cohere": Configure.Vectorizer.text2vec_cohere(
                model="embed-multilingual-v3.0", vectorize_collection_name=False
            ),
            "text2vec-huggingface": Configure.Vectorizer.text2vec_huggingface(
                model="sentence-transformers/all-MiniLM-L6-v2",
                vectorize_collection_name=False,
            ),
        }

        # For OpenAI embedding models, use text2vec-openai with appropriate model
        if embedding in [
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]:
            return Configure.Vectorizer.text2vec_openai(
                model=embedding, vectorize_collection_name=False
            )

        if embedding not in vectorizer_mapping:
            raise ValueError(
                f"Unsupported embedding: {embedding}. Supported: {self.supported_embeddings()}"
            )

        return vectorizer_mapping[embedding]

    def setup(self, embedding: str = "default"):
        """
        Set up Weaviate collection if it doesn't exist.

        Args:
            embedding: Embedding model to use for the collection
        """
        from weaviate.classes.config import Property, DataType

        if not self.client.collections.exists(self.collection_name):
            vectorizer_config = self._get_vectorizer_config(embedding)

            self.client.collections.create(
                self.collection_name,
                description="A dataset with the contents of Maestro Knowledge docs and website",
                vectorizer_config=vectorizer_config,
                properties=[
                    Property(
                        name="url",
                        data_type=DataType.TEXT,
                        description="the source URL of the webpage",
                    ),
                    Property(
                        name="text",
                        data_type=DataType.TEXT,
                        description="the content of the webpage",
                    ),
                    Property(
                        name="metadata",
                        data_type=DataType.TEXT,
                        description="additional metadata in JSON format",
                    ),
                ],
            )

    def write_documents(
        self, documents: List[Dict[str, Any]], embedding: str = "default"
    ):
        """
        Write documents to Weaviate.

        Args:
            documents: List of documents with 'url', 'text', and 'metadata' fields
            embedding: Embedding strategy to use:
                      - "default": Use Weaviate's default text2vec-weaviate
                      - Specific model name: Use the specified embedding model
        """
        # Validate embedding parameter
        if embedding not in self.supported_embeddings():
            raise ValueError(
                f"Unsupported embedding: {embedding}. Supported: {self.supported_embeddings()}"
            )

        # Ensure collection exists with the correct embedding configuration
        if not self.client.collections.exists(self.collection_name):
            self.setup(embedding)

        collection = self.client.collections.get(self.collection_name)
        with collection.batch.dynamic() as batch:
            for doc in documents:
                metadata_text = json.dumps(doc.get("metadata", {}), ensure_ascii=False)
                batch.add_object(
                    properties={
                        "url": doc.get("url", ""),
                        "text": doc.get("text", ""),
                        "metadata": metadata_text,
                    }
                )

    def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List documents from Weaviate."""
        collection = self.client.collections.get(self.collection_name)

        # Query the collection
        result = collection.query.fetch_objects(
            limit=limit,
            offset=offset,
            include_vector=False,  # Don't include vector data in response
        )

        # Process the results
        documents = []
        for obj in result.objects:
            doc = {
                "id": obj.uuid,
                "url": obj.properties.get("url", ""),
                "text": obj.properties.get("text", ""),
                "metadata": obj.properties.get("metadata", "{}"),
            }

            # Try to parse metadata if it's a JSON string
            try:
                doc["metadata"] = json.loads(doc["metadata"])
            except json.JSONDecodeError:
                pass

            documents.append(doc)

        return documents

    def count_documents(self) -> int:
        """Get the current count of documents in the collection."""
        collection = self.client.collections.get(self.collection_name)

        # Query to get the count - use a simple approach
        try:
            # Get all objects and count them (with a reasonable limit)
            result = collection.query.fetch_objects(limit=10000)
            return len(result.objects)
        except Exception as e:
            # If we can't get the count, return 0
            import warnings

            warnings.warn(f"Could not get document count for Weaviate collection: {e}")
            return 0

    def list_collections(self) -> List[str]:
        """List all collections in Weaviate."""
        try:
            # Get all collections from the client
            collections = self.client.collections.list_all()
            return [collection.name for collection in collections]
        except Exception as e:
            import warnings

            warnings.warn(f"Could not list collections from Weaviate: {e}")
            return []

    def get_collection_info(self, collection_name: str = None) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        target_collection = collection_name or self.collection_name

        try:
            # Check if collection exists
            if not self.client.collections.exists(target_collection):
                return {
                    "name": target_collection,
                    "document_count": 0,
                    "db_type": "weaviate",
                    "embedding": "unknown",
                    "metadata": {"error": "Collection does not exist"},
                }

            # Get collection object
            collection = self.client.collections.get(target_collection)

            # Get document count
            try:
                result = collection.query.fetch_objects(limit=10000)
                document_count = len(result.objects)
            except Exception as e:
                import warnings

                warnings.warn(
                    f"Could not get document count for Weaviate collection: {e}"
                )
                document_count = 0

            # Get collection configuration
            config = collection.config.get()

            # Extract embedding information from vectorizer config
            embedding_info = "unknown"
            if hasattr(config, "vectorizer") and config.vectorizer:
                embedding_info = config.vectorizer
            elif hasattr(config, "vectorizer_config") and config.vectorizer_config:
                embedding_info = str(config.vectorizer_config)

            # Get additional metadata
            metadata = {
                "description": config.description
                if hasattr(config, "description")
                else None,
                "vectorizer": config.vectorizer
                if hasattr(config, "vectorizer")
                else None,
                "properties_count": len(config.properties)
                if hasattr(config, "properties")
                else 0,
                "module_config": config.module_config
                if hasattr(config, "module_config")
                else None,
            }

            return {
                "name": target_collection,
                "document_count": document_count,
                "db_type": "weaviate",
                "embedding": embedding_info,
                "metadata": metadata,
            }
        except Exception as e:
            import warnings

            warnings.warn(f"Could not get collection info from Weaviate: {e}")
            return {
                "name": target_collection,
                "document_count": 0,
                "db_type": "weaviate",
                "embedding": "unknown",
                "metadata": {"error": str(e)},
            }

    def delete_documents(self, document_ids: List[str]):
        """Delete documents from Weaviate by their IDs."""
        collection = self.client.collections.get(self.collection_name)

        # Delete documents by UUID
        for doc_id in document_ids:
            try:
                collection.data.delete_by_id(doc_id)
            except Exception as e:
                import warnings

                warnings.warn(f"Failed to delete document {doc_id}: {e}")

    def delete_collection(self, collection_name: str = None):
        """Delete an entire collection from Weaviate."""
        target_collection = collection_name or self.collection_name

        try:
            if self.client.collections.exists(target_collection):
                self.client.collections.delete(target_collection)
                if target_collection == self.collection_name:
                    self.collection_name = None
        except Exception as e:
            import warnings

            warnings.warn(f"Failed to delete collection {target_collection}: {e}")

    def create_query_agent(self):
        """Create a Weaviate query agent."""
        from weaviate.agents.query import QueryAgent

        return QueryAgent(client=self.client, collections=[self.collection_name])

    def cleanup(self):
        """Clean up Weaviate client."""
        if self.client:
            try:
                # Close any open connections
                if hasattr(self.client, "close"):
                    self.client.close()
                # Also try to close the underlying connection if it exists
                if hasattr(self.client, "_connection") and self.client._connection:
                    if hasattr(self.client._connection, "close"):
                        try:
                            self.client._connection.close()
                        except TypeError:
                            # Some connection objects don't take arguments
                            pass
            except Exception as e:
                # Log the error but don't raise it to avoid breaking shutdown
                import warnings

                warnings.warn(f"Error during Weaviate cleanup: {e}")
            finally:
                self.client = None

    @property
    def db_type(self) -> str:
        return "weaviate"
