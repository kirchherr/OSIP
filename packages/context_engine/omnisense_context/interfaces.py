"""Context fusion interface owned by the OSIP context engine."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from omnisense_osip import ContextUpdate, PerceptPacket


class ContextFusion(Protocol):
    """Application-profile implementation that turns percepts into context."""

    profile_id: str

    def fuse(
        self,
        percepts: list[PerceptPacket],
        *,
        context_id: str,
        timestamp: datetime,
        room: str,
        time_window_ms: int,
    ) -> ContextUpdate:
        """Fuse active percepts into one OSIP context update."""
