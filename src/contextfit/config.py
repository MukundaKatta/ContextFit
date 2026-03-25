"""Configuration models for ContextFit."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContextFitConfig(BaseModel):
    """Configuration for the ContextFit packing engine."""

    tokens_per_word: float = Field(
        default=1.33,
        gt=0,
        description="Average number of tokens per whitespace-delimited word.",
    )
    separator: str = Field(
        default="\n\n",
        description="String used to join chunks when rendering packed output.",
    )
    default_priority: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Default priority assigned to chunks when none is specified.",
    )
