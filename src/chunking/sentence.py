"""Sentence-aware chunking strategy that packs sentences up to chunk_size."""

import re
from typing import Dict, List, Tuple


def _split_sentences(text: str) -> List[Tuple[int, int]]:
    """Return list of sentence spans as (start, end) offsets.

    A lightweight regex-based splitter that treats sequences ending with
    punctuation (., !, ?, or newline) as sentences. If no matches are found
    but text is non-empty, returns a single span covering the entire text.

    This avoids heavy NLP deps and is deterministic for tests.
    """
    sentences: List[Tuple[int, int]] = []
    pattern = re.compile(r"([^.!?\n]+[.!?\n]?)", re.M)
    for m in pattern.finditer(text):
        start = m.start()
        end = m.end()
        sentences.append((start, end))
    if not sentences and text:
        sentences = [(0, len(text))]
    return sentences


def sentence_chunk(
    text: str, chunk_size: int = 512, overlap: int = 0
) -> List[Dict[str, object]]:
    """Pack contiguous sentences into chunks near chunk_size.

    Behavior
    - Greedily appends whole sentences to the current chunk until adding the
      next sentence would exceed chunk_size.
    - If a single sentence is longer than chunk_size, it is split into fixed-size
      windows with the given overlap (like the Fixed strategy) so it still fits.
    - Overlap applies only when splitting oversized sentences or oversized
      current_text after a flush.

    Args:
        text: Full document text to chunk.
        chunk_size: Target max characters per chunk; must be > 0.
    overlap: Number of characters to overlap when splitting long segments; 0 <= overlap <= chunk_size.

    Returns:
        A list of chunk dicts with keys: text, offset_start, offset_end,
        chunk_size, sequence, total.

    Notes:
        - This function is intentionally simple and deterministic to keep tests
          stable and avoid external sentence tokenizers.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap > chunk_size:
        raise ValueError("overlap must be <= chunk_size")

    spans = _split_sentences(text)
    chunks: List[Dict[str, object]] = []
    current_text = ""
    current_start = 0
    seq = 0

    def flush(end_idx: int):
        """Close the current chunk into the output list.

        Uses the current_start offset and current_text to construct a chunk
        ending at end_idx, then resets the in-progress buffer.
        """
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

        # Would adding this sentence exceed the target chunk size?
        if len(current_text) + len(sent) > chunk_size:
            if current_text == "":
                # No in-progress chunk: split this oversized sentence into
                # fixed-size windows (with optional overlap) directly.
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
                # We already have content; flush it as a completed chunk,
                # then start a new in-progress chunk with this sentence.
                flush(start)
                current_text = sent
                current_start = start
                if len(current_text) > chunk_size:
                    # Rare case: even a single sentence placed after a flush
                    # is longer than chunk_size; split it into windows.
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

    # Emit any trailing in-progress chunk.
    if current_text:
        flush(len(text))

    total = len(chunks)
    for c in chunks:
        c["total"] = total

    return chunks


# Register
from .common import register_strategy

register_strategy("Sentence", sentence_chunk)
