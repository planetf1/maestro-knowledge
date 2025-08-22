"""None chunking strategy: return a single chunk with full text."""

from typing import Dict, List


def none_chunk(text: str, **_kwargs) -> List[Dict[str, object]]:
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


# Register with package registry to make strategy discoverable
from .common import register_strategy

register_strategy("None", none_chunk)
