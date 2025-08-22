"""Sentence-aware chunking strategy that packs sentences up to chunk_size."""

import re
from typing import Dict, List, Tuple


def _split_sentences(text: str) -> List[Tuple[int, int]]:
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

        if len(current_text) + len(sent) > chunk_size:
            if current_text == "":
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
                current_text = sent
                current_start = start
                if len(current_text) > chunk_size:
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

    if current_text:
        flush(len(text))

    total = len(chunks)
    for c in chunks:
        c["total"] = total

    return chunks


# Register
from .common import register_strategy

register_strategy("Sentence", sentence_chunk)
