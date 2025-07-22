# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

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

# Global variable to store the current vector database instance
current_db: Optional[VectorDatabase] = None


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
                        "required": ["db_type"],
                    },
                ),
                Tool(
                    name="setup_database",
                    description="Set up the current vector database and create collections",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="write_documents",
                    description="Write documents to the vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "documents": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string"},
                                        "text": {"type": "string"},
                                        "metadata": {"type": "object"},
                                    },
                                    "required": ["url", "text"],
                                },
                                "description": "List of documents to write",
                            }
                        },
                        "required": ["documents"],
                    },
                ),
                Tool(
                    name="write_document",
                    description="Write a single document to the vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
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
                        },
                        "required": ["url", "text"],
                    },
                ),
                Tool(
                    name="list_documents",
                    description="List documents from the vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
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
                        "required": [],
                    },
                ),
                Tool(
                    name="count_documents",
                    description="Get the current count of documents in the collection",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="delete_documents",
                    description="Delete documents from the vector database by their IDs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of document IDs to delete",
                            }
                        },
                        "required": ["document_ids"],
                    },
                ),
                Tool(
                    name="delete_document",
                    description="Delete a single document from the vector database by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "Document ID to delete",
                            }
                        },
                        "required": ["document_id"],
                    },
                ),
                Tool(
                    name="delete_collection",
                    description="Delete an entire collection from the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection to delete. If not provided, uses the current collection.",
                            }
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="cleanup",
                    description="Clean up resources and close database connections",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="get_database_info",
                    description="Get information about the current vector database",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]
        )

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls for vector database operations."""
        global current_db

        try:
            if name == "create_vector_database":
                db_type = arguments.get("db_type")
                collection_name = arguments.get("collection_name", "MaestroDocs")

                # Clean up existing database if any
                if current_db:
                    try:
                        current_db.cleanup()
                    except Exception as e:
                        logger.warning(f"Error cleaning up previous database: {e}")

                current_db = create_vector_database(db_type, collection_name)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully created {db_type} vector database with collection '{collection_name}'",
                        )
                    ]
                )

            elif name == "setup_database":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                current_db.setup()

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully set up {current_db.db_type} vector database",
                        )
                    ]
                )

            elif name == "write_documents":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                documents = arguments.get("documents", [])
                current_db.write_documents(documents)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully wrote {len(documents)} documents to the vector database",
                        )
                    ]
                )

            elif name == "write_document":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                document = {
                    "url": arguments.get("url"),
                    "text": arguments.get("text"),
                    "metadata": arguments.get("metadata", {}),
                }
                current_db.write_document(document)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully wrote document '{document['url']}' to the vector database",
                        )
                    ]
                )

            elif name == "list_documents":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                limit = arguments.get("limit", 10)
                offset = arguments.get("offset", 0)
                documents = current_db.list_documents(limit, offset)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Found {len(documents)} documents:\n"
                            + json.dumps(documents, indent=2, default=str),
                        )
                    ]
                )

            elif name == "count_documents":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                count = current_db.count_documents()

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Current document count: {count}"
                        )
                    ]
                )

            elif name == "delete_documents":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                document_ids = arguments.get("document_ids", [])
                current_db.delete_documents(document_ids)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted {len(document_ids)} documents",
                        )
                    ]
                )

            elif name == "delete_document":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                document_id = arguments.get("document_id")
                current_db.delete_document(document_id)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted document '{document_id}'",
                        )
                    ]
                )

            elif name == "delete_collection":
                if not current_db:
                    raise ValueError(
                        "No vector database created. Please create one first."
                    )

                collection_name = arguments.get("collection_name")
                current_db.delete_collection(collection_name)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted collection '{collection_name or current_db.collection_name}'",
                        )
                    ]
                )

            elif name == "cleanup":
                if current_db:
                    current_db.cleanup()
                    current_db = None

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Successfully cleaned up vector database resources",
                        )
                    ]
                )

            elif name == "get_database_info":
                if not current_db:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text="No vector database is currently active",
                            )
                        ]
                    )

                info = {
                    "db_type": current_db.db_type,
                    "collection_name": current_db.collection_name,
                    "document_count": current_db.count_documents(),
                }

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Database Information:\n{json.dumps(info, indent=2)}",
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
