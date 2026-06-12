"""Context engine orchestration."""

from __future__ import annotations

from omnisense_bus import AsyncMessageBus, context_update_topic
from omnisense_osip import ContextUpdate, PerceptPacket

from omnisense_context.interfaces import ContextFusion
from omnisense_context.registry import ContextFusionRegistry
from omnisense_context.temporal_window import TemporalWindow


class ContextEngine:
    """Ingests OSIP percepts, fuses profile context, and publishes updates."""

    def __init__(
        self,
        bus: AsyncMessageBus,
        *,
        application_profile: str = "rooms",
        fusion: ContextFusion | None = None,
        registry: ContextFusionRegistry | None = None,
        window_ms: int = 1000,
    ) -> None:
        self._bus = bus
        self._fusion = fusion or (registry or ContextFusionRegistry.with_defaults()).get(
            application_profile
        )
        self._application_profile = self._fusion.profile_id
        self._window = TemporalWindow(window_ms)
        self._counter = 0

    @property
    def application_profile(self) -> str:
        return self._application_profile

    @property
    def window(self) -> TemporalWindow:
        return self._window

    async def ingest(self, percept: PerceptPacket) -> ContextUpdate:
        self._window.add(percept)
        timestamp = percept.received_at or percept.timestamp
        room = self._room_for(percept)
        active = self._window.active_at(timestamp, room=room)
        self._counter += 1
        update = self._fusion.fuse(
            active,
            context_id=f"ctx_{room}_{self._counter:06d}",
            timestamp=timestamp,
            room=room,
            time_window_ms=self._window.window_ms,
        )
        update = update.model_copy(
            update={
                "trace_id": percept.trace_id or percept.id,
                "correlation_id": percept.correlation_id or percept.trace_id or percept.id,
            }
        )
        await self._bus.publish(context_update_topic(update.room), update)
        return update

    @staticmethod
    def _room_for(percept: PerceptPacket) -> str:
        if percept.location is not None and percept.location.room is not None:
            return percept.location.room
        return "unknown_room"
