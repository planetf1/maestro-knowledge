# SPDX-License-Identifier: Apache 2.0

import asyncio
import json
import os
import re
import time
from urllib.parse import urlparse

import html2text
import httpx
from fastmcp import Client

# -- Configuration --
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8030/mcp/")
COLLECTION_NAME = os.getenv("MK_COLLECTION", "qiskit_studio_algo")

# Embedding at collection creation time (write-time embedding is ignored)

# Chunking config (default to Sentence with overlap for continuity)
CHUNK_STRATEGY = os.getenv("MK_CHUNK_STRATEGY", "Sentence")
CHUNK_SIZE = int(os.getenv("MK_CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("MK_CHUNK_OVERLAP", "64"))

# Optional override for the sample query
SAMPLE_QUERY_OVERRIDE = os.getenv("MK_SAMPLE_QUERY", "").strip()

# Document URLs: supports JSON array in MK_DOCUMENT_URLS or newline-separated list
DOCUMENT_URLS = []
_mk_urls = os.getenv("MK_DOCUMENT_URLS", "").strip()
if _mk_urls:
    try:
        DOCUMENT_URLS = json.loads(_mk_urls)
        if not isinstance(DOCUMENT_URLS, list):
            DOCUMENT_URLS = []
    except Exception:
        DOCUMENT_URLS = [u.strip() for u in _mk_urls.splitlines() if u.strip()]


def slug_from_url(url: str) -> str:
    p = urlparse(url)
    path = p.path.strip("/")
    if not path:
        return (p.netloc or "document").replace(".", "_")
    segment = [s for s in path.split("/") if s][-1]
    segment = segment.split("?")[0].split("#")[0]
    return segment.replace(".", "_").replace("-", "_")


async def main():
    start_all = time.perf_counter()
    async with Client(MCP_SERVER_URL, timeout=60) as client:
        print("✅ fastmcp Client initialized successfully.")
        print(f"   • MCP server: {MCP_SERVER_URL}")
        print(f"   • Target collection: {COLLECTION_NAME}")
        print(
            f"   • Chunking: {CHUNK_STRATEGY} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})"
        )

        await cleanup_database_if_exists(client, COLLECTION_NAME)
        await create_vector_db(client, COLLECTION_NAME)

        await create_collection_with_config(
            client,
            COLLECTION_NAME,
            "default",
            chunking_config={
                "strategy": CHUNK_STRATEGY,
                "parameters": {"chunk_size": CHUNK_SIZE, "overlap": CHUNK_OVERLAP},
            },
        )

        await show_collection_info(
            client, COLLECTION_NAME, title="Collection (pre-population)"
        )

        print("\n▶️  Waiting 2 seconds for the collection to be ready...")
        await asyncio.sleep(2)

        write_payload, fetch_meta, docs_added = await add_documents_to_db(
            client, COLLECTION_NAME, DOCUMENT_URLS
        )

        await show_collection_info(
            client, COLLECTION_NAME, title="Collection (post-population)"
        )

        sample_query = (
            SAMPLE_QUERY_OVERRIDE
            or "what are good approaches to handling error mitigation with qiskit"
        )
        limit = 3

        print("\n🔍 Running a sample search")
        print(f"   • Query: {sample_query!r}")
        print(f"   • Limit: {limit}")
        await run_sample_search(
            client, COLLECTION_NAME, query=sample_query, limit=limit
        )

    total_ms = int((time.perf_counter() - start_all) * 1000)
    print(f"\n⏱️  Total script duration: {total_ms} ms")


async def cleanup_database_if_exists(client: Client, db_name: str):
    print(f"\n🧹 Attempting to clean up database '{db_name}'...")
    try:
        params = {"input": {"db_name": db_name}}
        result = await client.call_tool("cleanup", params)
        print(f"   ✓ Cleanup: {result.data}")
    except Exception:
        print("   ⚠️  Cleanup skipped (likely first run).")


async def create_vector_db(client: Client, db_name: str):
    print(f"\n🏗️  Creating vector database handle '{db_name}'...")
    params = {
        "input": {
            "db_name": db_name,
            "db_type": "weaviate",
            "collection_name": db_name,
        }
    }
    result = await client.call_tool("create_vector_database_tool", params)
    print(f"   ✓ DB handle: {result.data}")


async def create_collection_with_config(
    client: Client, db_name: str, embedding: str, chunking_config: dict
):
    print(
        f"\n📦 Creating collection '{db_name}' with embedding '{embedding}' and chunking {chunking_config}..."
    )
    params = {
        "input": {
            "db_name": db_name,
            "collection_name": db_name,
            "embedding": embedding,
            "chunking_config": chunking_config,
        }
    }
    result = await client.call_tool("create_collection", params)
    print(f"   ✓ Collection: {result.data}")


async def show_collection_info(
    client: Client, db_name: str, title: str = "Collection info"
):
    print(f"\nℹ️  {title} for '{db_name}':")
    params = {"input": {"db_name": db_name, "collection_name": db_name}}
    result = await client.call_tool("get_collection_info", params)
    try:
        payload = json.loads(result.data)
        print(json.dumps(payload, indent=2))
    except Exception:
        print(result.data)


async def add_documents_to_db(client: Client, db_name: str, doc_urls: list[str]):
    print(f"\n📝 Adding {len(doc_urls)} document(s) to '{db_name}'...")

    fetch_stats = []
    documents_to_add = []
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as http_client:
        for url in doc_urls:
            per_doc = {
                "url": url,
                "fetch_ms": None,
                "convert_ms": None,
                "html_bytes": None,
                "md_chars": None,
            }
            try:
                print(f"   • Fetching {url} ...")
                t0 = time.perf_counter()
                response = await http_client.get(url)
                response.raise_for_status()
                html_content = response.text
                per_doc["fetch_ms"] = int((time.perf_counter() - t0) * 1000)
                per_doc["html_bytes"] = len(response.content)

                print("     → Converting HTML to Markdown...")
                t1 = time.perf_counter()
                markdown_content = html2text.html2text(html_content)
                per_doc["convert_ms"] = int((time.perf_counter() - t1) * 1000)
                per_doc["md_chars"] = len(markdown_content)

                documents_to_add.append(
                    {
                        "url": url,
                        "text": markdown_content,
                        "metadata": {"doc_name": slug_from_url(url)},
                    }
                )
                print(
                    f"     ✓ Processed: fetch={per_doc['fetch_ms']} ms, convert={per_doc['convert_ms']} ms, "
                    f"size={per_doc['html_bytes']} bytes → {per_doc['md_chars']} chars"
                )
            except httpx.HTTPStatusError as e:
                print(f"     ✗ HTTP error for {url}: {e}")
            except Exception as e:
                print(f"     ✗ Unexpected error for {url}: {e}")
            finally:
                fetch_stats.append(per_doc)

    if not documents_to_add:
        print("⚠️  No documents to add.")
        return None, fetch_stats, []

    print(f"\n📤 Writing {len(documents_to_add)} documents to the database...")
    params = {"input": {"db_name": db_name, "documents": documents_to_add}}
    result = await client.call_tool("write_documents", params)

    payload = None
    try:
        payload = (
            json.loads(result.data) if isinstance(result.data, str) else result.data
        )
    except Exception:
        pass

    if not payload or not isinstance(payload, dict):
        print(f"   ✓ Write (raw): {result.data}")
        print_fetch_summary(fetch_stats)
        return None, fetch_stats, documents_to_add

    print_write_summary(payload, fetch_stats, documents_to_add)
    return payload, fetch_stats, documents_to_add


def print_fetch_summary(fetch_stats: list[dict]):
    print("\n📈 Fetch/convert summary:")
    for s in fetch_stats:
        if not s.get("url"):
            continue
        print(
            f"   - {s['url']}\n"
            f"     fetch: {s.get('fetch_ms')} ms, convert: {s.get('convert_ms')} ms, "
            f"html bytes: {s.get('html_bytes')}, md chars: {s.get('md_chars')}"
        )


def print_write_summary(payload: dict, fetch_stats: list[dict], docs: list[dict]):
    status = payload.get("status")
    message = payload.get("message")
    print(f"   ✓ Write status: {status} — {message}")

    write_stats = payload.get("write_stats") or {}
    per_doc = write_stats.get("per_document") or []
    total_chunks = write_stats.get("chunks")
    print(
        f"   • Backend: {write_stats.get('backend')}"
        f"\n   • Documents: {write_stats.get('documents')}"
        f"\n   • Total chunks (all docs): {total_chunks}"
        f"\n   • Build time: {write_stats.get('duration_ms')} ms"
        f"\n   • Insert time: {write_stats.get('insert_ms') if write_stats.get('insert_ms') is not None else 'n/a'} ms"
    )

    if per_doc:
        print("   • Per-document chunk counts:")
        name_to_url = {
            d["metadata"]["doc_name"]: d["url"]
            for d in docs
            if d.get("metadata", {}).get("doc_name")
        }
        sum_chunks = 0
        for d in per_doc:
            name = d.get("name")
            cc = int(d.get("chunk_count") or 0)
            sum_chunks += cc
            url = name_to_url.get(name)
            url_str = f" (url: {url})" if url else ""
            print(f"     - {name}: {cc} chunk(s){url_str}")
        if total_chunks is not None and sum_chunks != total_chunks:
            print(
                f"     ⚠️  Sum of per-document chunks ({sum_chunks}) != reported total ({total_chunks})"
            )
        else:
            print(f"     ✓ Per-document chunks sum matches total ({sum_chunks})")

    print_fetch_summary(fetch_stats)

    coll = payload.get("collection_info") or {}
    if coll:
        print("\n📚 Collection info after write:")
        print(json.dumps(coll, indent=2))

    sample = payload.get("sample_query_suggestion") or {}
    if sample:
        print("\n💡 Server sample query suggestion:")
        print(json.dumps(sample, indent=2))


async def run_sample_search(client: Client, db_name: str, query: str, limit: int = 3):
    try:
        params = {
            "input": {
                "db_name": db_name,
                "query": query,
                "limit": limit,
                "collection_name": db_name,
            }
        }
        result = await client.call_tool("search", params)
        print("\n🔎 Search results:")
        items = None
        try:
            items = (
                json.loads(result.data) if isinstance(result.data, str) else result.data
            )
        except Exception:
            print(result.data)
            return

        if not items:
            print("   (no results)")
            return

        for i, hit in enumerate(items, start=1):
            meta = hit.get("metadata") or {}
            doc_name = meta.get("doc_name")
            seq = meta.get("chunk_sequence_number")
            total = meta.get("total_chunks")
            score = hit.get("score", None)
            snippet = (hit.get("text") or "")[:200].replace("\n", " ")
            print(
                f"   {i}. doc={doc_name} seq={seq}/{total} score={'{:.4f}'.format(score) if isinstance(score, (int, float)) else score}"
            )
            print(f"      {snippet}{'...' if len(hit.get('text') or '') > 200 else ''}")
    except Exception as e:
        print(f"   ✗ Sample search failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
