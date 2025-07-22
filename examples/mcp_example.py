#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 dr.max

"""
Example demonstrating how to use the Maestro Vector Database MCP server.
This example shows how an AI agent might interact with the vector database.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.maestro_mcp.server import create_mcp_server
from src.db.vector_db_factory import create_vector_database


def demonstrate_mcp_server():
    """Demonstrate the MCP server functionality."""
    print("Maestro Vector Database MCP Server Example")
    print("=" * 50)

    # Create the MCP server
    print("\n1. Creating MCP server...")
    server = create_mcp_server()
    print(f"✓ Server created: {server.name}")

    # Show what tools are available
    print("\n2. Available tools in the MCP server:")
    expected_tools = [
        "create_vector_database",
        "setup_database",
        "write_documents",
        "write_document",
        "list_documents",
        "count_documents",
        "delete_documents",
        "delete_document",
        "delete_collection",
        "cleanup",
        "get_database_info",
    ]

    for tool in expected_tools:
        print(f"   - {tool}")

    print(f"\n✓ Total tools available: {len(expected_tools)}")

    # Demonstrate direct vector database usage (what the MCP server does internally)
    print("\n3. Demonstrating vector database operations:")

    try:
        # Create a vector database
        print("\n   Creating Weaviate vector database...")
        db = create_vector_database("weaviate", "ExampleDocs")
        print(f"   ✓ Created {db.db_type} database with collection 'ExampleDocs'")

        # Set up the database
        print("\n   Setting up database...")
        db.setup()
        print("   ✓ Database setup complete")

        # Write some documents
        documents = [
            {
                "url": "https://example.com/doc1",
                "text": "This is the first document about machine learning.",
                "metadata": {"topic": "ML", "author": "Alice"},
            },
            {
                "url": "https://example.com/doc2",
                "text": "This is the second document about data science.",
                "metadata": {"topic": "Data Science", "author": "Bob"},
            },
            {
                "url": "https://example.com/doc3",
                "text": "This is the third document about artificial intelligence.",
                "metadata": {"topic": "AI", "author": "Charlie"},
            },
        ]

        for doc in documents:
            db.write_document(doc)
            print(f"   ✓ Wrote document: {doc['url']}")

        # Get database info
        print("\n   Getting database info...")
        count = db.count_documents()
        print(f"   ✓ Document count: {count}")

        # List documents
        print("\n   Listing documents...")
        docs = db.list_documents(limit=5)
        print(f"   ✓ Found {len(docs)} documents")
        for doc in docs:
            print(
                f"      - {doc.get('url', 'No URL')}: {doc.get('text', 'No text')[:50]}..."
            )

        # Clean up
        print("\n   Cleaning up...")
        db.cleanup()
        print("   ✓ Cleanup complete")

    except Exception as e:
        print(f"   ✗ Error during database operations: {e}")
        print("   Note: This is expected if Weaviate/Milvus is not running")

    print("\n" + "=" * 50)
    print("Example completed!")
    print("\nTo use this MCP server with an AI agent:")
    print("1. Start the server: ./start.sh")
    print("2. Configure your MCP client with the server")
    print("3. Use the tools listed above to interact with vector databases")
    print("4. Stop the server: ./stop.sh")


def main():
    """Main entry point."""
    try:
        demonstrate_mcp_server()
    except Exception as e:
        print(f"Error running example: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
