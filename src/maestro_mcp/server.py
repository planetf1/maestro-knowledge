# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ..db.vector_db_factory import create_vector_database
from ..db.vector_db_base import VectorDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store vector database instances keyed by name
vector_databases: Dict[str, VectorDatabase] = {}


def get_database_by_name(db_name: str) -> VectorDatabase:
    """Get a vector database instance by name."""
    if db_name not in vector_databases:
        raise ValueError(
            f"Vector database '{db_name}' not found. Please create it first."
        )
    return vector_databases[db_name]


# Pydantic models for tool inputs
class CreateVectorDatabaseInput(BaseModel):
    db_name: str = Field(
        ..., description="Unique name for the vector database instance"
    )
    db_type: str = Field(
        ...,
        description="Type of vector database to create",
        json_schema_extra={"enum": ["weaviate", "milvus"]},
    )
    collection_name: str = Field(
        default="MaestroDocs", description="Name of the collection to use"
    )


class SetupDatabaseInput(BaseModel):
    db_name: str = Field(
        ..., description="Name of the vector database instance to set up"
    )
    embedding: str = Field(
        default="default", description="Embedding model to use for the collection"
    )


class GetSupportedEmbeddingsInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")


class WriteDocumentsInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    documents: List[Dict[str, Any]] = Field(
        ..., description="List of documents to write"
    )
    embedding: str = Field(default="default", description="Embedding strategy to use")


class WriteDocumentInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    url: str = Field(..., description="URL of the document")
    text: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the document"
    )
    vector: List[float] = Field(
        default=None, description="Pre-computed vector embedding (optional, for Milvus)"
    )
    embedding: str = Field(default="default", description="Embedding strategy to use")


class ListDocumentsInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    limit: int = Field(default=10, description="Maximum number of documents to return")
    offset: int = Field(default=0, description="Number of documents to skip")


class CountDocumentsInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")


class DeleteDocumentsInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    document_ids: List[str] = Field(..., description="List of document IDs to delete")


class DeleteDocumentInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    document_id: str = Field(..., description="Document ID to delete")


class DeleteCollectionInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")
    collection_name: str = Field(
        default=None, description="Name of the collection to delete"
    )


class CleanupInput(BaseModel):
    db_name: str = Field(
        ..., description="Name of the vector database instance to clean up"
    )


class GetDatabaseInfoInput(BaseModel):
    db_name: str = Field(..., description="Name of the vector database instance")


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server with vector database tools."""

    # Create a FastAPI app with OpenAPI documentation
    fastapi_app = FastAPI(
        title="Maestro Vector Database MCP Server",
        description="A Model Context Protocol server for vector database operations",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Create FastMCP server from the FastAPI app
    app = FastMCP.from_fastapi(fastapi_app, name="maestro-vector-db")

    @app.tool()
    async def create_vector_database_tool(input: CreateVectorDatabaseInput) -> str:
        """Create a new vector database instance."""
        # Check if database with this name already exists
        if input.db_name in vector_databases:
            raise ValueError(f"Vector database '{input.db_name}' already exists")

        # Create new database instance
        vector_databases[input.db_name] = create_vector_database(
            input.db_type, input.collection_name
        )

        return f"Successfully created {input.db_type} vector database '{input.db_name}' with collection '{input.collection_name}'"

    @app.tool()
    async def setup_database(input: SetupDatabaseInput) -> str:
        """Set up a vector database and create collections."""
        db = get_database_by_name(input.db_name)

        # Check if the database supports the setup method with embedding parameter
        if hasattr(db, "setup") and len(db.setup.__code__.co_varnames) > 1:
            db.setup(embedding=input.embedding)
        else:
            db.setup()

        return f"Successfully set up {db.db_type} vector database '{input.db_name}' with embedding '{input.embedding}'"

    @app.tool()
    async def get_supported_embeddings(input: GetSupportedEmbeddingsInput) -> str:
        """Get list of supported embedding models for a vector database."""
        db = get_database_by_name(input.db_name)
        embeddings = db.supported_embeddings()

        return f"Supported embeddings for {db.db_type} vector database '{input.db_name}': {json.dumps(embeddings, indent=2)}"

    @app.tool()
    async def write_documents(input: WriteDocumentsInput) -> str:
        """Write documents to a vector database with specified embedding strategy."""
        db = get_database_by_name(input.db_name)
        db.write_documents(input.documents, embedding=input.embedding)

        return f"Successfully wrote {len(input.documents)} documents to vector database '{input.db_name}' using embedding '{input.embedding}'"

    @app.tool()
    async def write_document(input: WriteDocumentInput) -> str:
        """Write a single document to a vector database with specified embedding strategy."""
        db = get_database_by_name(input.db_name)
        document = {
            "url": input.url,
            "text": input.text,
            "metadata": input.metadata,
        }

        # Add vector if provided (for Milvus)
        if input.vector is not None:
            document["vector"] = input.vector

        db.write_document(document, embedding=input.embedding)

        return f"Successfully wrote document '{input.url}' to vector database '{input.db_name}' using embedding '{input.embedding}'"

    @app.tool()
    async def list_documents(input: ListDocumentsInput) -> str:
        """List documents from a vector database."""
        db = get_database_by_name(input.db_name)
        documents = db.list_documents(input.limit, input.offset)

        return f"Found {len(documents)} documents in vector database '{input.db_name}':\n{json.dumps(documents, indent=2, default=str)}"

    @app.tool()
    async def count_documents(input: CountDocumentsInput) -> str:
        """Get the current count of documents in a collection."""
        db = get_database_by_name(input.db_name)
        count = db.count_documents()

        return f"Document count in vector database '{input.db_name}': {count}"

    @app.tool()
    async def delete_documents(input: DeleteDocumentsInput) -> str:
        """Delete documents from a vector database by their IDs."""
        db = get_database_by_name(input.db_name)
        db.delete_documents(input.document_ids)

        return f"Successfully deleted {len(input.document_ids)} documents from vector database '{input.db_name}'"

    @app.tool()
    async def delete_document(input: DeleteDocumentInput) -> str:
        """Delete a single document from a vector database by its ID."""
        db = get_database_by_name(input.db_name)
        db.delete_document(input.document_id)

        return f"Successfully deleted document '{input.document_id}' from vector database '{input.db_name}'"

    @app.tool()
    async def delete_collection(input: DeleteCollectionInput) -> str:
        """Delete an entire collection from a database."""
        db = get_database_by_name(input.db_name)
        db.delete_collection(input.collection_name)

        return f"Successfully deleted collection '{input.collection_name or db.collection_name}' from vector database '{input.db_name}'"

    @app.tool()
    async def cleanup(input: CleanupInput) -> str:
        """Clean up resources and close database connections for a specific database."""
        db = get_database_by_name(input.db_name)
        db.cleanup()
        del vector_databases[input.db_name]

        return f"Successfully cleaned up vector database '{input.db_name}'"

    @app.tool()
    async def get_database_info(input: GetDatabaseInfoInput) -> str:
        """Get information about a vector database."""
        db = get_database_by_name(input.db_name)

        info = {
            "db_name": input.db_name,
            "db_type": db.db_type,
            "collection_name": db.collection_name,
            "document_count": db.count_documents(),
            "supported_embeddings": db.supported_embeddings(),
        }

        return (
            f"Database Information for '{input.db_name}':\n{json.dumps(info, indent=2)}"
        )

    @app.tool()
    async def list_databases() -> str:
        """List all available vector database instances."""
        if not vector_databases:
            return "No vector databases are currently active"

        db_list = []
        for db_name, db in vector_databases.items():
            db_list.append(
                {
                    "name": db_name,
                    "type": db.db_type,
                    "collection": db.collection_name,
                    "document_count": db.count_documents(),
                }
            )

        return f"Available vector databases:\n{json.dumps(db_list, indent=2)}"

    return app


async def main():
    """Main entry point for the MCP server."""
    app = create_mcp_server()
    await app.run()


async def run_http_server(host: str = "localhost", port: int = 8000):
    """Run the MCP server with HTTP interface."""
    # Create a FastAPI app with OpenAPI documentation
    fastapi_app = FastAPI(
        title="Maestro Vector Database MCP Server",
        description="A Model Context Protocol server for vector database operations",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Create the MCP server
    mcp_app = create_mcp_server()

    # Mount the MCP server on the FastAPI app
    fastapi_app.mount("/mcp", mcp_app.http_app())

    # Add a root endpoint that redirects to docs
    @fastapi_app.get("/")
    async def root():
        return HTMLResponse("""
        <html>
            <head>
                <title>Maestro Vector Database MCP Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .button { display: inline-block; padding: 10px 20px; margin: 10px; 
                             background-color: #007bff; color: white; text-decoration: none; 
                             border-radius: 5px; }
                    .button:hover { background-color: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Maestro Vector Database MCP Server</h1>
                    <p>Welcome to the Maestro Vector Database MCP Server!</p>
                    <p>This server provides tools for managing vector databases including Weaviate and Milvus.</p>
                    <h2>Available Endpoints:</h2>
                    <ul>
                        <li><a href="/docs" class="button">📖 OpenAPI Documentation</a></li>
                        <li><a href="/redoc" class="button">📚 ReDoc Documentation</a></li>
                        <li><a href="/mcp/" class="button">🔧 MCP Endpoint</a></li>
                    </ul>
                    <h2>Tools Available:</h2>
                    <ul>
                        <li>create_vector_database_tool - Create a new vector database instance</li>
                        <li>setup_database - Set up a vector database and create collections</li>
                        <li>get_supported_embeddings - Get list of supported embedding models</li>
                        <li>write_documents - Write documents to a vector database</li>
                        <li>write_document - Write a single document to a vector database</li>
                        <li>list_documents - List documents from a vector database</li>
                        <li>count_documents - Get the current count of documents</li>
                        <li>delete_documents - Delete documents from a vector database</li>
                        <li>delete_document - Delete a single document</li>
                        <li>delete_collection - Delete an entire collection</li>
                        <li>cleanup - Clean up resources and close connections</li>
                        <li>get_database_info - Get information about a vector database</li>
                        <li>list_databases - List all available vector database instances</li>
                    </ul>
                </div>
            </body>
        </html>
        """)

    print(f"Starting FastMCP HTTP server on http://{host}:{port}")
    print(f"Open your browser to http://{host}:{port} to access the MCP server")
    print(f"📖 OpenAPI docs: http://{host}:{port}/docs")
    print(f"📚 ReDoc docs: http://{host}:{port}/redoc")

    # Run the FastAPI app
    import uvicorn

    config = uvicorn.Config(fastapi_app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()


def run_server():
    """Entry point for running the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)


def run_http_server_sync(host: str = "localhost", port: int = 8000):
    """Synchronous entry point for running the HTTP server."""
    try:
        asyncio.run(run_http_server(host, port))
    except KeyboardInterrupt:
        print("\nHTTP server stopped by user")
    except Exception as e:
        print(f"Error running HTTP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
