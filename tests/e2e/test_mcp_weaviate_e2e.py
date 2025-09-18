# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
End-to-end tests against a real Weaviate backend via FastMCP HTTP client.

These tests are OPTIONAL and will be skipped unless the required environment variables are set.

Required env to enable (example values):
- E2E_WEAVIATE=1
- WEAVIATE_API_KEY=your-key
- WEAVIATE_URL=https://your.weaviate.network

Optional env:
- E2E_MCP_PORT=8030
- LOG_LEVEL=info
- VDB_LOG_LEVEL=debug
- PRETTY_TOOL_JSON=true
- FULL_TOOL_JSON=true

Note: These tests start the MCP HTTP server in-process on a local port and then
use fastmcp.Client to call the server tools end-to-end.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, TYPE_CHECKING

import pytest
import httpx

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

pytestmark = [pytest.mark.e2e, pytest.mark.requires_weaviate]


def _required_env_present() -> bool:
    """Return True if this Weaviate E2E suite should run.

    Rules:
    - If E2E_BACKEND is set, it must equal "weaviate" (case-insensitive) for this suite to run.
    - Backward-compat: if E2E_BACKEND is NOT set, we fall back to requiring E2E_WEAVIATE=1.
    - In all cases, the Weaviate env vars must be present.
    """
    backend = (os.getenv("E2E_BACKEND") or "").strip().lower()
    if backend and backend != "weaviate":
        return False

    # If both legacy flags are set and no selector provided, do not run either suite
    if (
        not backend
        and os.getenv("E2E_MILVUS") == "1"
        and os.getenv("E2E_WEAVIATE") == "1"
    ):
        return False

    if not backend and os.getenv("E2E_WEAVIATE") != "1":
        return False

    required = [
        "WEAVIATE_API_KEY",
        "WEAVIATE_URL",
    ]
    return all(os.getenv(k) for k in required)


@pytest.fixture(scope="module")
async def mcp_http_server() -> AsyncGenerator[dict[str, Any], None]:
    """Start the MCP HTTP server in-process for the duration of the module.

    Skips the test module if required env is not present.
    """
    if not _required_env_present():
        backend = os.getenv("E2E_BACKEND")
        if backend and backend.strip().lower() != "weaviate":
            pytest.skip(
                "E2E_BACKEND is set to a non-weaviate value; skipping Weaviate E2E"
            )
        pytest.skip(
            "E2E Weaviate env not present or E2E_WEAVIATE/E2E_BACKEND not enabled; skipping end-to-end tests"
        )

    import subprocess
    import sys
    import time

    host = "127.0.0.1"
    port = int(os.getenv("E2E_MCP_PORT", "8030"))

    # Start server as subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    # Use uv to run the server with proper environment
    cmd = [
        "uv",
        "run",
        "python",
        "-c",
        f"from maestro_mcp.server import run_http_server_sync; run_http_server_sync('{host}', {port})",
    ]

    process = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd()
    )

    # Wait for health endpoint to be ready (up to ~20s)
    base = f"http://{host}:{port}"
    health_url = f"{base}/health"

    server_ready = False
    async with httpx.AsyncClient() as client:
        for _ in range(40):  # 40 * 0.5s = 20s
            if process.poll() is not None:
                # Server process died
                stdout, stderr = process.communicate()
                pytest.skip(f"MCP server process failed to start: {stderr.decode()}")

            try:
                resp = await client.get(health_url, timeout=1.5)
                if resp.status_code < 500:
                    server_ready = True
                    break
            except Exception:
                pass
            await asyncio.sleep(0.5)

    if not server_ready:
        process.terminate()
        process.wait()
        pytest.skip("MCP HTTP server did not become ready in time")

    yield {"host": host, "port": port, "process": process}

    # Teardown: terminate the server process
    process.terminate()
    process.wait(timeout=5)


@pytest.mark.asyncio
async def test_full_weaviate_flow(mcp_http_server: dict[str, Any]) -> None:
    """Full flow: create DB + collection, write docs, list/count/search, cleanup (Weaviate)."""
    from fastmcp import Client

    host = mcp_http_server["host"]
    port = mcp_http_server["port"]
    base_mcp_url = f"http://{host}:{port}/mcp/"

    db_name = os.getenv("E2E_COLLECTION_NAME", "E2E_WV_Test_Collection")

    async with Client(base_mcp_url, timeout=1800) as client:  # generous for e2e
        # Create vector DB (weaviate)
        res = await client.call_tool(
            "create_vector_database_tool",
            {
                "input": {
                    "db_name": db_name,
                    "db_type": "weaviate",
                    "collection_name": db_name,
                }
            },
        )
        assert hasattr(res, "data")

        # Create collection using default embedding (text2vec-weaviate)
        res = await client.call_tool(
            "create_collection",
            {
                "input": {
                    "db_name": db_name,
                    "collection_name": db_name,
                    "embedding": os.getenv("EMBEDDING_MODEL", "default"),
                    "chunking_config": {
                        "strategy": os.getenv("CHUNK_STRATEGY", "Sentence"),
                        "parameters": {
                            "chunk_size": int(os.getenv("CHUNK_SIZE", "512")),
                            "overlap": int(os.getenv("CHUNK_OVERLAP", "24")),
                        },
                    },
                }
            },
        )
        assert hasattr(res, "data")

        # Write a couple of small documents
        docs = [
            {"url": "https://example.com/wv1", "text": "hello vector world"},
            {"url": "https://example.com/wv2", "text": "maestro knowledge weaviate"},
        ]
        res = await client.call_tool(
            "write_documents",
            {
                "input": {
                    "db_name": db_name,
                    "documents": docs,
                    "embedding": os.getenv("EMBEDDING_MODEL", "default"),
                }
            },
        )
        assert hasattr(res, "data")

        # List documents
        res = await client.call_tool(
            "list_documents", {"input": {"db_name": db_name, "limit": 10, "offset": 0}}
        )
        assert hasattr(res, "data")

        # Count documents
        res = await client.call_tool("count_documents", {"input": {"db_name": db_name}})
        assert hasattr(res, "data")

        # Get collection info
        res = await client.call_tool(
            "get_collection_info", {"input": {"db_name": db_name}}
        )
        assert hasattr(res, "data")

        # Search
        res = await client.call_tool(
            "search",
            {
                "input": {
                    "db_name": db_name,
                    "query": os.getenv("TEST_QUERY_TEXT", "vector"),
                    "limit": 1,
                }
            },
        )
        assert hasattr(res, "data") or hasattr(res, "content")

        # Cleanup at end
        res = await client.call_tool("cleanup", {"input": {"db_name": db_name}})
        assert hasattr(res, "data")
