"""ContextFit — context window packing optimizer for LLMs."""

from contextfit.config import ContextFitConfig
from contextfit.core import Chunk, ContextFit, PackResult

__all__ = [
    "ContextFit",
    "ContextFitConfig",
    "Chunk",
    "PackResult",
]

__version__ = "0.1.0"
