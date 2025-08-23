import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.chunking import ChunkingConfig, chunk_text


def test_none_chunk():
    text = "Hello world"
    cfg = ChunkingConfig()
    res = chunk_text(text, cfg)
    assert len(res) == 1
    assert res[0]["text"] == text
