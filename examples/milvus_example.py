#!/usr/bin/env python3
"""
Example usage of maestro-knowledge with Milvus vector database.

This example demonstrates:
1. Setting up environment variables
2. Creating a vector database instance
3. Writing documents with vectors
4. Listing and querying documents
5. Cleanup
"""

import os
import json
from typing import List, Dict, Any

# Set environment variables for Milvus (optional - these are the defaults)
os.environ.setdefault("VECTOR_DB_TYPE", "milvus")
os.environ.setdefault("MILVUS_HOST", "localhost")
os.environ.setdefault("MILVUS_PORT", "19530")

# Add the project root to the Python path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the factory function
from src.db.vector_db_factory import create_vector_database


def create_sample_documents() -> List[Dict[str, Any]]:
    """Create sample documents with vector embeddings."""
    return [
        {
            "url": "https://example.com/doc1",
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
            "metadata": {
                "type": "article",
                "author": "Dr. Smith",
                "category": "AI/ML",
                "tags": ["machine learning", "artificial intelligence", "algorithms"],
            },
            "vector": [0.1] * 1536,  # 1536-dimensional vector (example)
        },
        {
            "url": "https://example.com/doc2",
            "text": "Vector databases are specialized databases designed to store and query high-dimensional vector data efficiently.",
            "metadata": {
                "type": "tutorial",
                "author": "Jane Doe",
                "category": "Database",
                "tags": ["vector database", "similarity search", "embeddings"],
            },
            "vector": [0.2] * 1536,  # 1536-dimensional vector (example)
        },
        {
            "url": "https://example.com/doc3",
            "text": "Milvus is an open-source vector database that provides high-performance similarity search and analytics.",
            "metadata": {
                "type": "documentation",
                "author": "Milvus Team",
                "category": "Database",
                "tags": [
                    "milvus",
                    "vector database",
                    "open source",
                    "similarity search",
                ],
            },
            "vector": [0.3] * 1536,  # 1536-dimensional vector (example)
        },
    ]


def main():
    """Main example function."""
    print("🚀 Maestro Knowledge - Milvus Vector Database Example")
    print("=" * 60)

    try:
        # Create a vector database instance
        print("\n1. Creating vector database instance...")
        db = create_vector_database("milvus", "ExampleCollection")
        print(f"✅ Created {db.db_type} database with collection: {db.collection_name}")

        # Set up the collection
        print("\n2. Setting up collection...")
        db.setup()
        print("✅ Collection setup complete")

        # Create sample documents
        print("\n3. Creating sample documents...")
        documents = create_sample_documents()
        print(f"✅ Created {len(documents)} sample documents")

        # Write documents to the database
        print("\n4. Writing documents to database...")
        db.write_documents(documents)
        print("✅ Documents written successfully")

        # List documents from the database
        print("\n5. Listing documents from database...")
        retrieved_docs = db.list_documents(limit=5)
        print(f"✅ Retrieved {len(retrieved_docs)} documents:")

        for i, doc in enumerate(retrieved_docs, 1):
            print(f"\n   Document {i}:")
            print(f"   - ID: {doc.get('id', 'N/A')}")
            print(f"   - URL: {doc.get('url', 'N/A')}")
            print(f"   - Text: {doc.get('text', 'N/A')[:100]}...")
            print(f"   - Metadata: {json.dumps(doc.get('metadata', {}), indent=6)}")

        # Demonstrate document count
        print("\n6. Document count:")
        count = db.count_documents()
        print(f"   - Total documents in collection: {count}")

        # Demonstrate document deletion
        print("\n7. Demonstrating document deletion:")
        if retrieved_docs:
            first_doc_id = retrieved_docs[0].get("id")
            print(f"   - Deleting document with ID: {first_doc_id}")
            db.delete_document(str(first_doc_id))

            # Check count after deletion
            new_count = db.count_documents()
            print(f"   - Documents after deletion: {new_count}")

        # Demonstrate environment variable usage
        print("\n8. Environment variable configuration:")
        print(f"   - VECTOR_DB_TYPE: {os.environ.get('VECTOR_DB_TYPE', 'not set')}")
        print(f"   - MILVUS_URI: {os.environ.get('MILVUS_URI', 'not set')}")

        print("\n✅ Example completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   - Milvus server running (or use cloud instance)")
        print("   - pymilvus package installed: pip install pymilvus")
        print("   - Proper environment variables set")

    finally:
        # Clean up resources
        print("\n7. Cleaning up...")
        try:
            db.cleanup()
            print("✅ Cleanup completed")
        except Exception:
            print("⚠️  Cleanup failed (this is normal if db wasn't initialized)")


if __name__ == "__main__":
    main()
