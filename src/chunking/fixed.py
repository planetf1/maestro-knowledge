"""Fixed-size chunking strategy with optional overlap."""


def fixed_chunk(
    text: str, chunk_size: int = 512, overlap: int = 0
) -> list[dict[str, object]]:
    """Split text into fixed-size windows with optional overlap.

    Behavior
    - Produces chunks of up to `chunk_size` characters by sliding a window with
      step `chunk_size - overlap` (minimum effective step is 1).
    - Overlap must be in the range 0 <= overlap < chunk_size.

    Args:
        text: Full document text to chunk.
        chunk_size: Target max characters per chunk; must be > 0.
        overlap: Characters overlapped between consecutive windows; 0 <= overlap < chunk_size.

    Returns:
        A list of chunk dicts with keys: text, offset_start, offset_end,
        chunk_size, sequence, total.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be < chunk_size")

    step = max(1, chunk_size - overlap)
    chunks: list[dict[str, object]] = []
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


# Register
from .common import register_strategy

register_strategy("Fixed", fixed_chunk)
