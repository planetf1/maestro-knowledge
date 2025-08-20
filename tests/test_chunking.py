import os
import sys

# Ensure the project root is on sys.path so tests can import `src.*` (matches other tests)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking import ChunkingConfig, chunk_text


def test_none_chunk():
    text = "Hello world"
    cfg = ChunkingConfig()
    res = chunk_text(text, cfg)
    assert len(res) == 1
    assert res[0]["text"] == text


def test_fixed_chunk():
    text = "a" * 1200
    cfg = ChunkingConfig(
        strategy="Fixed", parameters={"chunk_size": 500, "overlap": 100}
    )
    res = chunk_text(text, cfg)
    assert len(res) >= 2
    # ensure overlap behavior: step = 400
    assert res[0]["offset_start"] == 0
    assert res[1]["offset_start"] == 400


def test_sentence_chunk_simple():
    text = "This is one sentence. This is another! And a third?"
    cfg = ChunkingConfig(
        strategy="Sentence", parameters={"chunk_size": 50, "overlap": 0}
    )
    res = chunk_text(text, cfg)
    assert len(res) >= 1
    # ensure sequences are ordered
    seqs = [c["sequence"] for c in res]
    assert seqs == sorted(seqs)


def test_sentence_split_long_sentence():
    text = "A" * 1200
    cfg = ChunkingConfig(
        strategy="Sentence", parameters={"chunk_size": 500, "overlap": 50}
    )
    res = chunk_text(text, cfg)
    assert len(res) >= 2
    # total should be set on each chunk
    assert all("total" in c for c in res)
