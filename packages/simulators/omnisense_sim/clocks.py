"""Deterministic simulated clocks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(slots=True)
class SimulatedClock:
    """A monotonic virtual clock that never sleeps."""

    start_time: datetime = datetime(2026, 6, 12, tzinfo=UTC)
    current_ms: int = 0

    def __post_init__(self) -> None:
        if self.start_time.tzinfo is None or self.start_time.utcoffset() is None:
            msg = "start_time must include timezone information"
            raise ValueError(msg)
        if self.current_ms < 0:
            msg = "current_ms must be greater than or equal to zero"
            raise ValueError(msg)

    def now(self) -> datetime:
        return self.datetime_at(self.current_ms)

    def datetime_at(self, offset_ms: int) -> datetime:
        if offset_ms < 0:
            msg = "offset_ms must be greater than or equal to zero"
            raise ValueError(msg)
        return self.start_time + timedelta(milliseconds=offset_ms)

    def advance_to(self, target_ms: int) -> datetime:
        if target_ms < self.current_ms:
            msg = "simulated time cannot move backwards"
            raise ValueError(msg)
        self.current_ms = target_ms
        return self.now()

    def advance_by(self, delta_ms: int) -> datetime:
        if delta_ms < 0:
            msg = "delta_ms must be greater than or equal to zero"
            raise ValueError(msg)
        return self.advance_to(self.current_ms + delta_ms)
