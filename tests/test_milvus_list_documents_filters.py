# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

import warnings
from typing import Any

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.vector_db_milvus import MilvusVectorDatabase
import inspect


@patch("pymilvus.MilvusClient")
def test_list_documents_respects_offset_pagination(
    mock_milvus_client: MagicMock,
) -> None:
    """
    list_documents should pass offset/limit to backend and return non-repeating pages when backend responds accordingly.
    """
    mock_client = MagicMock()

    def _fake_query(collection: str, **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        # Touch collection to avoid unused-arg warnings
        assert isinstance(collection, str)
        off = kwargs.get("offset", 0) or 0
        lim = kwargs.get("limit", 2) or 2
        start = off
        rows = []
        for i in range(start, start + lim):
            rows.append(
                {
                    "id": i,
                    "url": f"http://doc/{i}",
                    "text": f"content-{i}",
                    "metadata": '{"doc_name": "x", "content_sha256": "h"}',
                }
            )
        return rows

    mock_client.query.side_effect = _fake_query
    mock_milvus_client.return_value = mock_client

    db = MilvusVectorDatabase()
    # Current API: list_documents(limit, offset)
    page1 = db.list_documents(limit=2, offset=0)
    page2 = db.list_documents(limit=2, offset=2)

    assert [d["id"] for d in page1] == [0, 1]
    assert [d["id"] for d in page2] == [2, 3]
    assert mock_client.query.call_count == 2
    first_call = mock_client.query.call_args_list[0].kwargs
    second_call = mock_client.query.call_args_list[1].kwargs
    assert first_call.get("offset") == 0
    assert second_call.get("offset") == 2


@patch("pymilvus.MilvusClient")
def test_list_documents_in_collection_respects_offset(
    mock_milvus_client: MagicMock,
) -> None:
    """Existing API: list_documents_in_collection should propagate limit/offset and not repeat first page."""
    mock_client = MagicMock()

    def _fake_query(collection: str, **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        assert collection == "ColZ"
        off = kwargs.get("offset", 0) or 0
        lim = kwargs.get("limit", 2) or 2
        return [
            {
                "id": off + j,
                "url": f"u{off + j}",
                "text": f"t{off + j}",
                "metadata": '{"doc_name": "z"}',
            }
            for j in range(lim)
        ]

    mock_client.has_collection.return_value = True
    mock_client.query.side_effect = _fake_query
    mock_milvus_client.return_value = mock_client

    db = MilvusVectorDatabase()
    page1 = db.list_documents_in_collection("ColZ", limit=2, offset=0)
    page2 = db.list_documents_in_collection("ColZ", limit=2, offset=2)

    assert [d["id"] for d in page1] == [0, 1]
    assert [d["id"] for d in page2] == [2, 3]
    assert mock_client.query.call_count == 2
    c1 = mock_client.query.call_args_list[0]
    c2 = mock_client.query.call_args_list[1]
    assert c1.kwargs.get("offset") == 0 and c1.args[0] == "ColZ"
    assert c2.kwargs.get("offset") == 2 and c2.args[0] == "ColZ"
