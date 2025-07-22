#!/usr/bin/env python3
"""
Weaviate Vector Database Example

This example demonstrates how to use the maestro-knowledge library with Weaviate.
It shows how to create a vector database, write documents, and list them.

Prerequisites:
- Weaviate cloud instance or local Weaviate server
- Environment variables: WEAVIATE_API_KEY and WEAVIATE_URL

Usage:
    python examples/weaviate_example.py
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the factory function
from src.db.vector_db_factory import create_vector_database


def main():
    """Main function demonstrating Weaviate usage."""
    print("🚀 Weaviate Vector Database Example")
    print("=" * 50)

    # Check if required environment variables are set
    if not os.getenv("WEAVIATE_API_KEY"):
        print("❌ Error: WEAVIATE_API_KEY environment variable is not set")
        print("Please set it to your Weaviate API key")
        return

    if not os.getenv("WEAVIATE_URL"):
        print("❌ Error: WEAVIATE_URL environment variable is not set")
        print("Please set it to your Weaviate cluster URL")
        return

    try:
        # 1. Create a Weaviate vector database instance
        print("\n1. Creating Weaviate vector database...")
        db = create_vector_database("weaviate", "WeaviateExampleCollection")
        print("✅ Weaviate database instance created")

        # 2. Set up the database (creates collection if it doesn't exist)
        print("\n2. Setting up database...")
        db.setup()
        print("✅ Database setup completed")

        # 3. Prepare sample documents
        print("\n3. Preparing sample documents...")
        documents = [
            {
                "url": "https://example.com/doc1",
                "text": "This is the first document about artificial intelligence and machine learning.",
                "metadata": {
                    "title": "AI and ML Introduction",
                    "category": "technology",
                    "author": "Dr. Smith"
                }
            },
            {
                "url": "https://example.com/doc2",
                "text": "Vector databases are essential for modern AI applications and semantic search.",
                "metadata": {
                    "title": "Vector Databases Guide",
                    "category": "technology",
                    "author": "Dr. Johnson"
                }
            },
            {
                "url": "https://example.com/doc3",
                "text": "Weaviate is a powerful vector database that supports semantic search and AI applications.",
                "metadata": {
                    "title": "Weaviate Overview",
                    "category": "database",
                    "author": "Dr. Brown"
                }
            }
        ]
        print(f"✅ Prepared {len(documents)} sample documents")

        # 4. Write documents to the database
        print("\n4. Writing documents to database...")
        db.write_documents(documents)
        print("✅ Documents written successfully")

        # 5. List documents from the database
        print("\n5. Listing documents from database...")
        retrieved_docs = db.list_documents(limit=5, offset=0)
        print(f"✅ Retrieved {len(retrieved_docs)} documents:")
        
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"\n   Document {i}:")
            print(f"   - ID: {doc.get('id', 'N/A')}")
            print(f"   - URL: {doc.get('url', 'N/A')}")
            print(f"   - Text: {doc.get('text', 'N/A')[:100]}...")
            if doc.get('metadata'):
                metadata = doc['metadata']
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        pass
                print(f"   - Title: {metadata.get('title', 'N/A')}")
                print(f"   - Category: {metadata.get('category', 'N/A')}")

        # 6. Test database type property
        print(f"\n6. Database type: {db.db_type}")
        print("✅ Database type retrieved successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("- Make sure WEAVIATE_API_KEY and WEAVIATE_URL are set correctly")
        print("- Verify your Weaviate cluster is running and accessible")
        print("- Check that your API key has the necessary permissions")
        return

    finally:
        # Clean up resources
        print("\n7. Cleaning up...")
        try:
            db.cleanup()
            print("✅ Cleanup completed")
        except Exception:
            print("⚠️  Cleanup failed (this is normal if db wasn't initialized)")

    print("\n🎉 Weaviate example completed successfully!")


if __name__ == "__main__":
    main() 