"""Context fusion for OmniSense Runtime."""

from typing import Any

from omnisense_context.claim_index import ClaimIndex, ClaimObservation
from omnisense_context.engine import ContextEngine
from omnisense_context.graph import (
    ContextGraph,
    ContextGraphEntityRecord,
    ContextGraphEventRecord,
    ContextGraphSnapshot,
    ContextGraphStats,
)
from omnisense_context.interfaces import ContextFusion
from omnisense_context.registry import ContextFusionRegistry, UnknownApplicationProfileError
from omnisense_context.temporal_window import TemporalWindow

__all__ = [
    "ClaimIndex",
    "ClaimObservation",
    "ContextEngine",
    "ContextFusion",
    "ContextGraph",
    "ContextGraphEntityRecord",
    "ContextGraphEventRecord",
    "ContextGraphSnapshot",
    "ContextGraphStats",
    "ContextFusionRegistry",
    "RoomsFusion",
    "TemporalWindow",
    "UnknownApplicationProfileError",
]


def __getattr__(name: str) -> Any:
    if name == "RoomsFusion":
        from omnisense_profiles.rooms.context_fusion import RoomsFusion

        return RoomsFusion
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
