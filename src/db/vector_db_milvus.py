# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import json
import os
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


class MilvusVectorDatabase(VectorDatabase):
    """Milvus implementation of the vector database interface."""

    def __init__(self, collection_name: str = "MaestroDocs"):
        super().__init__(collection_name)
        self.client = None
        self.collection_name = collection_name
        self._client_created = False

    def supported_embeddings(self) -> List[str]:
        """
        Return a list of supported embedding model names for Milvus.

        Milvus supports both pre-computed vectors and can work with external
        embedding services, but doesn't have built-in embedding models.

        Returns:
            List of supported embedding model names
        """
        return [
            "default",
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]

    def _ensure_client(self):
        """Ensure the client is created, handling import-time issues."""
        if not self._client_created:
            self._create_client()
            self._client_created = True

    def _create_client(self):
        import os
        import warnings

        # Temporarily unset MILVUS_URI to prevent pymilvus from auto-connecting during import
        original_milvus_uri = os.environ.pop("MILVUS_URI", None)

        try:
            # Import pymilvus after unsetting the environment variable
            from pymilvus import MilvusClient

            milvus_uri = original_milvus_uri or "milvus_demo.db"
            milvus_token = os.getenv("MILVUS_TOKEN", None)

            # For local Milvus Lite, try different URI formats
            try:
                if milvus_token:
                    self.client = MilvusClient(uri=milvus_uri, token=milvus_token)
                else:
                    self.client = MilvusClient(uri=milvus_uri)
            except Exception as e:
                # If the URI format fails, try with file:// prefix
                if not milvus_uri.startswith(("http://", "https://", "file://")):
                    file_uri = f"file://{milvus_uri}"
                    try:
                        if milvus_token:
                            self.client = MilvusClient(uri=file_uri, token=milvus_token)
                        else:
                            self.client = MilvusClient(uri=file_uri)
                    except Exception as file_e:
                        # If both attempts fail, create a mock client that warns about connection issues
                        warnings.warn(
                            f"Failed to connect to Milvus at {milvus_uri} or {file_uri}. "
                            f"Milvus operations will be disabled. Error: {file_e}"
                        )
                        self.client = None
                else:
                    # For HTTP URIs, if connection fails, create a mock client
                    warnings.warn(
                        f"Failed to connect to Milvus server at {milvus_uri}. "
                        f"Milvus operations will be disabled. Error: {e}"
                    )
                    self.client = None
        finally:
            # Restore the environment variable
            if original_milvus_uri:
                os.environ["MILVUS_URI"] = original_milvus_uri

    def _generate_embedding(self, text: str, embedding_model: str) -> List[float]:
        """
        Generate embeddings for text using the specified model.

        Args:
            text: Text to embed
            embedding_model: Name of the embedding model to use

        Returns:
            List of floats representing the embedding vector
        """
        try:
            import openai

            # Map model names to OpenAI model names
            model_mapping = {
                "text-embedding-ada-002": "text-embedding-ada-002",
                "text-embedding-3-small": "text-embedding-3-small",
                "text-embedding-3-large": "text-embedding-3-large",
            }

            if embedding_model not in model_mapping:
                raise ValueError(f"Unsupported embedding model: {embedding_model}")

            openai_model = model_mapping[embedding_model]

            # Get OpenAI API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required for embedding generation"
                )

            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(model=openai_model, input=text)

            return response.data[0].embedding

        except ImportError:
            raise ImportError(
                "openai package is required for embedding generation. Install with: pip install openai"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")

    def setup(self):
        """Set up Milvus collection if it doesn't exist."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Setup skipped.")
            return

        # Create collection if it doesn't exist
        if not self.client.has_collection(self.collection_name):
            # Use the correct API for MilvusClient
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=1536,  # Vector dimension
                primary_field_name="id",
                vector_field_name="vector",
            )

    def write_documents(
        self, documents: List[Dict[str, Any]], embedding: str = "default"
    ):
        """
        Write documents to Milvus.

        Args:
            documents: List of documents with 'url', 'text', and 'metadata' fields.
                      Documents may also include a 'vector' field for pre-computed embeddings.
            embedding: Embedding strategy to use:
                      - "default": Use pre-computed vector if available, otherwise use text-embedding-ada-002
                      - Specific model name: Use the specified embedding model to generate vectors
        """
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Documents not written.")
            return

        # Validate embedding parameter
        if embedding not in self.supported_embeddings():
            raise ValueError(
                f"Unsupported embedding: {embedding}. Supported: {self.supported_embeddings()}"
            )

        # Process documents
        data = []
        for i, doc in enumerate(documents):
            doc_vector = None

            # Determine how to get the vector
            if embedding == "default":
                # For default, use pre-computed vector if available
                if "vector" in doc:
                    doc_vector = doc["vector"]
                else:
                    # Generate embedding using default model
                    doc_vector = self._generate_embedding(
                        doc.get("text", ""), "text-embedding-ada-002"
                    )
            else:
                # Use specified embedding model
                doc_vector = self._generate_embedding(doc.get("text", ""), embedding)

            if doc_vector is None:
                raise ValueError(f"Failed to generate vector for document {i}")

            data.append(
                {
                    "id": i,
                    "url": doc.get("url", ""),
                    "text": doc.get("text", ""),
                    "metadata": json.dumps(doc.get("metadata", {}), ensure_ascii=False),
                    "vector": doc_vector,
                }
            )
        self.client.insert(self.collection_name, data)

    def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List documents from Milvus."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Returning empty list.")
            return []

        # Query all documents, paginated
        results = self.client.query(
            self.collection_name,
            output_fields=["id", "url", "text", "metadata"],
            limit=limit,
            offset=offset,
        )

        docs = []
        for doc in results:
            try:
                metadata = json.loads(doc.get("metadata", "{}"))
            except Exception:
                metadata = {}
            docs.append(
                {
                    "id": doc.get("id"),
                    "url": doc.get("url", ""),
                    "text": doc.get("text", ""),
                    "metadata": metadata,
                }
            )
        return docs

    def count_documents(self) -> int:
        """Get the current count of documents in the collection."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Returning 0.")
            return 0

        # Get collection statistics
        stats = self.client.get_collection_stats(self.collection_name)
        return stats.get("row_count", 0)

    def list_collections(self) -> List[str]:
        """List all collections in Milvus."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Returning empty list.")
            return []

        try:
            # Get all collections from the client
            collections = self.client.list_collections()
            return collections
        except Exception as e:
            warnings.warn(f"Could not list collections from Milvus: {e}")
            return []

    def get_collection_info(self, collection_name: str = None) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Returning empty info.")
            return {
                "name": collection_name or self.collection_name,
                "document_count": 0,
                "db_type": "milvus",
                "embedding": "unknown",
                "metadata": {},
            }

        target_collection = collection_name or self.collection_name

        try:
            # Check if collection exists
            if not self.client.has_collection(target_collection):
                return {
                    "name": target_collection,
                    "document_count": 0,
                    "db_type": "milvus",
                    "embedding": "unknown",
                    "metadata": {"error": "Collection does not exist"},
                }

            # Get collection statistics
            stats = self.client.get_collection_stats(target_collection)
            document_count = stats.get("row_count", 0)

            # Get collection schema information
            collection_info = self.client.describe_collection(target_collection)

            # Extract embedding information from schema if available
            embedding_info = "unknown"
            if hasattr(collection_info, "fields"):
                for field in collection_info.fields:
                    if field.name == "vector":
                        embedding_info = (
                            f"vector_dim_{field.params.get('dim', 'unknown')}"
                        )
                        break

            return {
                "name": target_collection,
                "document_count": document_count,
                "db_type": "milvus",
                "embedding": embedding_info,
                "metadata": {
                    "collection_id": collection_info.id
                    if hasattr(collection_info, "id")
                    else None,
                    "created_time": collection_info.created_time
                    if hasattr(collection_info, "created_time")
                    else None,
                    "description": collection_info.description
                    if hasattr(collection_info, "description")
                    else None,
                    "fields_count": len(collection_info.fields)
                    if hasattr(collection_info, "fields")
                    else 0,
                },
            }
        except Exception as e:
            warnings.warn(f"Could not get collection info from Milvus: {e}")
            return {
                "name": target_collection,
                "document_count": 0,
                "db_type": "milvus",
                "embedding": "unknown",
                "metadata": {"error": str(e)},
            }

    def delete_documents(self, document_ids: List[str]):
        """Delete documents from Milvus by their IDs."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Documents not deleted.")
            return

        # Convert string IDs to integers for Milvus
        try:
            int_ids = [int(doc_id) for doc_id in document_ids]
        except ValueError:
            raise ValueError("Milvus document IDs must be convertible to integers.")

        # Delete documents by ID
        self.client.delete(self.collection_name, ids=int_ids)

    def delete_collection(self, collection_name: str = None):
        """Delete an entire collection from Milvus."""
        self._ensure_client()
        if self.client is None:
            warnings.warn("Milvus client is not available. Collection not deleted.")
            return

        target_collection = collection_name or self.collection_name

        if self.client.has_collection(target_collection):
            self.client.drop_collection(target_collection)
            if target_collection == self.collection_name:
                self.collection_name = None

    def create_query_agent(self):
        """Create a query agent for Milvus."""
        # Placeholder: Milvus does not have a built-in query agent like Weaviate
        # You would implement your own search logic here
        return self

    def cleanup(self):
        """Clean up Milvus client."""
        # No explicit cleanup needed for MilvusClient
        if self.client is not None:
            self.client = None

    @property
    def db_type(self) -> str:
        return "milvus"
