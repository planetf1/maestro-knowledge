# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import asyncio
import json
import logging
import sys
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

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


def create_mcp_server() -> Server:
    """Create and configure the MCP server with vector database tools."""

    server = Server("maestro-vector-db")

    @server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        """List all available tools for vector database operations."""
        return ListToolsResult(
            tools=[
                Tool(
                    name="create_vector_database",
                    description="Create a new vector database instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Unique name for the vector database instance",
                            },
                            "db_type": {
                                "type": "string",
                                "enum": ["weaviate", "milvus"],
                                "description": "Type of vector database to create",
                            },
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection to use",
                                "default": "MaestroDocs",
                            },
                        },
                        "required": ["db_name", "db_type"],
                    },
                ),
                Tool(
                    name="setup_database",
                    description="Set up a vector database and create collections",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance to set up",
                            },
                            "embedding": {
                                "type": "string",
                                "description": "Embedding model to use for the collection (e.g., 'default', 'text-embedding-ada-002')",
                                "default": "default",
                            },
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="get_supported_embeddings",
                    description="Get list of supported embedding models for a vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            }
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="write_documents",
                    description="Write documents to a vector database with specified embedding strategy",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "documents": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string"},
                                        "text": {"type": "string"},
                                        "metadata": {"type": "object"},
                                        "vector": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "description": "Pre-computed vector embedding (optional, for Milvus)",
                                        },
                                    },
                                    "required": ["url", "text"],
                                },
                                "description": "List of documents to write",
                            },
                            "embedding": {
                                "type": "string",
                                "description": "Embedding strategy to use: 'default' or specific model name (e.g., 'text-embedding-ada-002')",
                                "default": "default",
                            },
                        },
                        "required": ["db_name", "documents"],
                    },
                ),
                Tool(
                    name="write_document",
                    description="Write a single document to a vector database with specified embedding strategy",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "url": {
                                "type": "string",
                                "description": "URL of the document",
                            },
                            "text": {
                                "type": "string",
                                "description": "Text content of the document",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata for the document",
                            },
                            "vector": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Pre-computed vector embedding (optional, for Milvus)",
                            },
                            "embedding": {
                                "type": "string",
                                "description": "Embedding strategy to use: 'default' or specific model name",
                                "default": "default",
                            },
                        },
                        "required": ["db_name", "url", "text"],
                    },
                ),
                Tool(
                    name="list_documents",
                    description="List documents from a vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of documents to return",
                                "default": 10,
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Number of documents to skip",
                                "default": 0,
                            },
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="count_documents",
                    description="Get the current count of documents in a collection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            }
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="delete_documents",
                    description="Delete documents from a vector database by their IDs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "document_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of document IDs to delete",
                            },
                        },
                        "required": ["db_name", "document_ids"],
                    },
                ),
                Tool(
                    name="delete_document",
                    description="Delete a single document from a vector database by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "document_id": {
                                "type": "string",
                                "description": "Document ID to delete",
                            },
                        },
                        "required": ["db_name", "document_id"],
                    },
                ),
                Tool(
                    name="delete_collection",
                    description="Delete an entire collection from a database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            },
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection to delete. If not provided, uses the database's collection.",
                            },
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="cleanup",
                    description="Clean up resources and close database connections for a specific database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance to clean up",
                            }
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="get_database_info",
                    description="Get information about a vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Name of the vector database instance",
                            }
                        },
                        "required": ["db_name"],
                    },
                ),
                Tool(
                    name="list_databases",
                    description="List all available vector database instances",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]
        )

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls for vector database operations."""

        try:
            if name == "create_vector_database":
                db_name = arguments.get("db_name")
                db_type = arguments.get("db_type")
                collection_name = arguments.get("collection_name", "MaestroDocs")

                # Check if database with this name already exists
                if db_name in vector_databases:
                    raise ValueError(f"Vector database '{db_name}' already exists")

                # Create new database instance
                vector_databases[db_name] = create_vector_database(
                    db_type, collection_name
                )

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully created {db_type} vector database '{db_name}' with collection '{collection_name}'",
                        )
                    ]
                )

            elif name == "setup_database":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                embedding = arguments.get("embedding", "default")

                # Check if the database supports the setup method with embedding parameter
                if hasattr(db, "setup") and len(db.setup.__code__.co_varnames) > 1:
                    db.setup(embedding=embedding)
                else:
                    db.setup()

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully set up {db.db_type} vector database '{db_name}' with embedding '{embedding}'",
                        )
                    ]
                )

            elif name == "get_supported_embeddings":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                embeddings = db.supported_embeddings()

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Supported embeddings for {db.db_type} vector database '{db_name}': {json.dumps(embeddings, indent=2)}",
                        )
                    ]
                )

            elif name == "write_documents":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                documents = arguments.get("documents", [])
                embedding = arguments.get("embedding", "default")
                db.write_documents(documents, embedding=embedding)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully wrote {len(documents)} documents to vector database '{db_name}' using embedding '{embedding}'",
                        )
                    ]
                )

            elif name == "write_document":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                document = {
                    "url": arguments.get("url"),
                    "text": arguments.get("text"),
                    "metadata": arguments.get("metadata", {}),
                }

                # Add vector if provided (for Milvus)
                if "vector" in arguments:
                    document["vector"] = arguments["vector"]

                embedding = arguments.get("embedding", "default")
                db.write_document(document, embedding=embedding)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully wrote document '{document['url']}' to vector database '{db_name}' using embedding '{embedding}'",
                        )
                    ]
                )

            elif name == "list_documents":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                limit = arguments.get("limit", 10)
                offset = arguments.get("offset", 0)
                documents = db.list_documents(limit, offset)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Found {len(documents)} documents in vector database '{db_name}':\n"
                            + json.dumps(documents, indent=2, default=str),
                        )
                    ]
                )

            elif name == "count_documents":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                count = db.count_documents()

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Document count in vector database '{db_name}': {count}",
                        )
                    ]
                )

            elif name == "delete_documents":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                document_ids = arguments.get("document_ids", [])
                db.delete_documents(document_ids)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted {len(document_ids)} documents from vector database '{db_name}'",
                        )
                    ]
                )

            elif name == "delete_document":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                document_id = arguments.get("document_id")
                db.delete_document(document_id)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted document '{document_id}' from vector database '{db_name}'",
                        )
                    ]
                )

            elif name == "delete_collection":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                collection_name = arguments.get("collection_name")
                db.delete_collection(collection_name)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted collection '{collection_name or db.collection_name}' from vector database '{db_name}'",
                        )
                    ]
                )

            elif name == "cleanup":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)
                db.cleanup()
                del vector_databases[db_name]

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully cleaned up vector database '{db_name}'",
                        )
                    ]
                )

            elif name == "get_database_info":
                db_name = arguments.get("db_name")
                db = get_database_by_name(db_name)

                info = {
                    "db_name": db_name,
                    "db_type": db.db_type,
                    "collection_name": db.collection_name,
                    "document_count": db.count_documents(),
                    "supported_embeddings": db.supported_embeddings(),
                }

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Database Information for '{db_name}':\n{json.dumps(info, indent=2)}",
                        )
                    ]
                )

            elif name == "list_databases":
                if not vector_databases:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text="No vector databases are currently active",
                            )
                        ]
                    )

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

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Available vector databases:\n{json.dumps(db_list, indent=2)}",
                        )
                    ]
                )

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Error in tool {name}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    return server


async def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="maestro-vector-db",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


def run_server():
    """Entry point for running the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
