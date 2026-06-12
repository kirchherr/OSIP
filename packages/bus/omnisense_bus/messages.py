"""Message envelopes used by OmniSense bus adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

PayloadT = TypeVar("PayloadT")


@dataclass(frozen=True, slots=True)
class BusMessage[PayloadT]:
    """A delivered payload with deterministic per-topic sequence metadata."""

    topic: str
    sequence: int
    payload: PayloadT
