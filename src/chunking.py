"""
Chunking utilities for Maestro Knowledge.

Provides a pluggable interface for chunking strategies.
Supported strategies: None, Fixed, Sentence
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class ChunkingConfig:
    strategy: str = "None"
    parameters: Dict[str, object] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


def _none_chunk(text: str, **_kwargs) -> List[Dict[str, object]]:
    return [
        {
            "text": text,
            "offset_start": 0,
            "offset_end": len(text),
            "chunk_size": len(text),
            "sequence": 0,
            "total": 1,
        }
    ]


def _fixed_chunk(
    text: str, chunk_size: int = 512, overlap: int = 0
) -> List[Dict[str, object]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    step = max(1, chunk_size - overlap)
    chunks: List[Dict[str, object]] = []
    length = len(text)
    seq = 0
    for start in range(0, length, step):
        end = min(start + chunk_size, length)
        piece = text[start:end]
        chunks.append(
            {
                "text": piece,
                "offset_start": start,
                "offset_end": end,
                "chunk_size": len(piece),
                "sequence": seq,
                "total": 0,  # filled in later
            }
        )
        seq += 1

    total = len(chunks)
    for c in chunks:
        c["total"] = total

    return chunks


def _split_sentences(text: str) -> List[Tuple[int, int]]:
    # Simple sentence splitter based on punctuation. Keeps offsets.
    # This is intentionally lightweight to avoid extra dependencies.
    sentences: List[Tuple[int, int]] = []
    pattern = re.compile(r"([^.!?\n]+[.!?\n]?)", re.M)
    for m in pattern.finditer(text):
        start = m.start()
        end = m.end()
        sentences.append((start, end))
    # If nothing matched, return one span
    if not sentences and text:
        sentences = [(0, len(text))]
    return sentences


def _sentence_chunk(
    text: str, chunk_size: int = 512, overlap: int = 0
) -> List[Dict[str, object]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    spans = _split_sentences(text)
    chunks: List[Dict[str, object]] = []
    current_text = ""
    current_start = 0
    seq = 0

    def flush(end_idx: int):
        nonlocal current_text, current_start, seq
        if current_text == "":
            return
        end = end_idx
        piece = current_text
        chunks.append(
            {
                "text": piece,
                "offset_start": current_start,
                "offset_end": end,
                "chunk_size": len(piece),
                "sequence": seq,
                "total": 0,
            }
        )
        seq += 1
        current_text = ""

    for start, end in spans:
        sent = text[start:end]
        if current_text == "":
            current_start = start

        # if adding this sentence would exceed chunk_size
        if len(current_text) + len(sent) > chunk_size:
            # if current_text empty, we must split the sentence
            if current_text == "":
                # split the sentence to fit
                i = 0
                while i < len(sent):
                    piece = sent[i : i + chunk_size]
                    sstart = start + i
                    send = min(start + i + chunk_size, end)
                    chunks.append(
                        {
                            "text": piece,
                            "offset_start": sstart,
                            "offset_end": send,
                            "chunk_size": len(piece),
                            "sequence": seq,
                            "total": 0,
                        }
                    )
                    seq += 1
                    i += (
                        chunk_size - overlap if chunk_size - overlap > 0 else chunk_size
                    )
                current_text = ""
            else:
                flush(start)
                # start new with this sentence
                current_text = sent
                current_start = start
                # if sentence itself > chunk_size, loop will split next iteration
                if len(current_text) > chunk_size:
                    # force split
                    i = 0
                    while i < len(current_text):
                        piece = current_text[i : i + chunk_size]
                        sstart = current_start + i
                        send = min(
                            current_start + i + chunk_size,
                            current_start + len(current_text),
                        )
                        chunks.append(
                            {
                                "text": piece,
                                "offset_start": sstart,
                                "offset_end": send,
                                "chunk_size": len(piece),
                                "sequence": seq,
                                "total": 0,
                            }
                        )
                        seq += 1
                        i += (
                            chunk_size - overlap
                            if chunk_size - overlap > 0
                            else chunk_size
                        )
                    current_text = ""
        else:
            current_text += sent

    # flush remainder
    if current_text:
        flush(len(text))

    total = len(chunks)
    for c in chunks:
        c["total"] = total

    return chunks


_STRATEGIES: Dict[str, Callable[..., List[Dict[str, object]]]] = {
    "None": _none_chunk,
    "Fixed": _fixed_chunk,
    "Sentence": _sentence_chunk,
}


def chunk_text(
    text: str, config: Optional[ChunkingConfig] = None
) -> List[Dict[str, object]]:
    """Chunk text according to the provided ChunkingConfig.

    Returns list of dicts containing keys: text, offset_start, offset_end, chunk_size, sequence, total
    """
    if config is None:
        config = ChunkingConfig()

    strategy = config.strategy or "None"
    parameters = config.parameters or {}

    func = _STRATEGIES.get(strategy)
    if func is None:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

    # apply defaults when strategy is set and parameters missing
    if strategy != "None":
        # default chunk size 512 and overlap 0
        params = {"chunk_size": 512, "overlap": 0}
        params.update(parameters)
    else:
        params = {}

    return func(text, **params)
