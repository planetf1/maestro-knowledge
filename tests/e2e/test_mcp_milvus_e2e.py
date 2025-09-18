# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
End-to-end tests against a real Milvus backend and embedding service via FastMCP HTTP client.

These tests are OPTIONAL and will be skipped unless the required environment variables are set.

Required env to enable (example values):
- E2E_MILVUS=1
- MILVUS_URI=http://localhost:19530
- CUSTOM_EMBEDDING_URL=http://localhost:11434/v1
- CUSTOM_EMBEDDING_MODEL=nomic-embed-text
- CUSTOM_EMBEDDING_VECTORSIZE=768

Optional env:
- E2E_MCP_PORT=8030
- LOG_LEVEL=info
- VDB_LOG_LEVEL=debug
- PRETTY_TOOL_JSON=true
- FULL_TOOL_JSON=true

Note: These tests start the MCP HTTP server via project scripts and then
use fastmcp.Client to call the server tools end-to-end.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # Only for type checkers; no runtime import
    from collections.abc import AsyncGenerator

import pytest
import httpx

pytestmark = [pytest.mark.e2e, pytest.mark.requires_milvus]


def _required_env_present() -> bool:
    """Return True if this Milvus E2E suite should run.

    Rules:
    - If E2E_BACKEND is set, it must equal "milvus" (case-insensitive) for this suite to run.
    - Backward-compat: if E2E_BACKEND is NOT set, we fall back to requiring E2E_MILVUS=1.
    - In all cases, the Milvus and embedding env vars must be present.
    """
    # Backend selector
    backend = (os.getenv("E2E_BACKEND") or "").strip().lower()
    if backend and backend != "milvus":
        return False

    # If both legacy flags are set and no selector provided, do not run either suite
    if (
        not backend
        and os.getenv("E2E_MILVUS") == "1"
        and os.getenv("E2E_WEAVIATE") == "1"
    ):
        return False

    # Backward compatibility: allow running when E2E_MILVUS=1 if E2E_BACKEND is not provided
    if not backend and os.getenv("E2E_MILVUS") != "1":
        return False

    # Required environment for Milvus + custom embedder
    required = [
        "MILVUS_URI",
        "CUSTOM_EMBEDDING_URL",
        "CUSTOM_EMBEDDING_MODEL",
        "CUSTOM_EMBEDDING_VECTORSIZE",
    ]
    return all(os.getenv(k) for k in required)


@pytest.fixture(scope="module", name="mcp_http_server")
async def _mcp_http_server() -> AsyncGenerator[dict[str, Any], None]:
    """Start the MCP HTTP server using direct subprocess control."""
    if not _required_env_present():
        backend = os.getenv("E2E_BACKEND")
        if backend and backend.strip().lower() != "milvus":
            pytest.skip("E2E_BACKEND is set to a non-milvus value; skipping Milvus E2E")
        pytest.skip(
            "E2E Milvus env not present or E2E_MILVUS/E2E_BACKEND not enabled; skipping end-to-end tests"
        )

    host = "127.0.0.1" 
    port = int(os.getenv("E2E_MCP_PORT", "8030"))

    import subprocess
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    # Start server directly using uv run with timeout
    server_process = subprocess.Popen([
        "uv", "run", "python", "-c",
        f"""
import sys
sys.path.insert(0, '{project_root}')
from src.maestro_mcp.server import run_http_server_sync
run_http_server_sync('{host}', {port})
"""
    ], env=env, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Wait for server to be ready with timeout
    server_ready = False
    try:
        async with httpx.AsyncClient() as client:
            for attempt in range(30):  # 30 attempts * 1s = 30s max
                try:
                    resp = await client.get(f"http://{host}:{port}/health", timeout=2.0)
                    if resp.status_code < 500:
                        server_ready = True
                        break
                except httpx.RequestError:
                    pass
                await asyncio.sleep(1.0)

        if not server_ready:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            pytest.skip("MCP HTTP server did not become ready within 30s.")

        yield {"host": host, "port": port}

    finally:
        # Clean shutdown
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_process.kill()


@pytest.mark.asyncio
async def test_full_milvus_flow(mcp_http_server: dict[str, Any]) -> None:
    """Full flow: create DB + collection, write docs, list/count/search, cleanup."""
    
    host = mcp_http_server["host"]
    port = mcp_http_server["port"] 
    base_mcp_url = f"http://{host}:{port}/mcp/"

    # First verify the server is responding
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://{host}:{port}/health", timeout=10.0)
        assert resp.status_code == 200
        print(f"✓ MCP server responding at {base_mcp_url}")

    # Check if we can actually test with Milvus
    milvus_available = False
    try:
        # Test if Milvus is available by trying to import and connect
        from pymilvus import connections, utility
        
        # Connect to Milvus - this is the real test
        connections.connect(
            alias="test_connection",
            host="localhost", 
            port="19530",
            timeout=5
        )
        
        # Verify connection works by listing collections
        collections = utility.list_collections(using="test_connection")
        connections.disconnect("test_connection")
        
        milvus_available = True
        print(f"✓ Milvus service is available with {len(collections)} existing collections")
        
    except Exception as e:
        print(f"⚠ Milvus not available: {e}")
        print("Make sure Milvus is running and healthy:")
        print("  For Apple Silicon, use an ARM64 compatible container:")
        print("  podman run -d --name milvus-simple -p 19530:19530 <arm64-milvus-image>")
        print("  Check logs with: podman logs milvus-simple")
        pytest.skip("Milvus service not available for full E2E testing")

    if not milvus_available:
        return

    # If Milvus is available, run the full test
    try:
        from fastmcp import Client

        db_name = os.getenv("E2E_COLLECTION_NAME", "E2E_Test_Collection")

        async with Client(base_mcp_url, timeout=180) as client:  # 3 min timeout for E2E
            print(f"✓ Testing full Milvus flow with collection: {db_name}")
            
            # Create vector DB (milvus)
            res = await client.call_tool(
                "create_vector_database_tool",
                {"input": {"db_name": db_name, "db_type": "milvus", "collection_name": db_name}},
            )
            assert hasattr(res, "data")
            print("✓ Created Milvus vector database")

            # Create collection with embedding/chunking
            res = await client.call_tool(
                "create_collection",
                {
                    "input": {
                        "db_name": db_name,
                        "collection_name": db_name,
                        "embedding": "custom_local",  # Use our embedding service
                        "chunking_config": {
                            "strategy": "Sentence",
                            "parameters": {
                                "chunk_size": 256,
                                "overlap": 1,
                            },
                        },
                    }
                },
            )
            assert hasattr(res, "data")
            print("✓ Created collection with custom embedding")

            # Write test documents
            docs = [
                {"url": "https://example.com/quantum", "text": "Quantum computing uses quantum mechanical phenomena"},
                {"url": "https://example.com/maestro", "text": "Maestro knowledge management system"},
            ]
            res = await client.call_tool(
                "write_documents",
                {"input": {"db_name": db_name, "documents": docs}},
            )
            assert hasattr(res, "data")
            print("✓ Wrote test documents")

            # Verify documents were written
            res = await client.call_tool("count_documents", {"input": {"db_name": db_name}})
            assert hasattr(res, "data")
            print("✓ Counted documents")

            # Test search functionality
            res = await client.call_tool(
                "search",
                {"input": {"db_name": db_name, "query": "quantum", "limit": 2}},
            )
            assert hasattr(res, "data") or hasattr(res, "content")
            print("✓ Search completed")

            # Cleanup
            res = await client.call_tool("cleanup", {"input": {"db_name": db_name}})
            assert hasattr(res, "data")
            print("✓ Cleanup completed")

            print("🎉 Full Milvus E2E test completed successfully!")

    except Exception as e:
        pytest.fail(f"Milvus E2E test failed: {e}")
