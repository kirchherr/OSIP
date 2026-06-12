from __future__ import annotations

from datetime import datetime

import pytest
from omnisense_context import (
    ContextFusionRegistry,
    RoomsFusion,
    UnknownApplicationProfileError,
)
from omnisense_osip import ContextUpdate, GlobalRisk, PerceptPacket


class DummyFusion:
    profile_id = "dummy"

    def fuse(
        self,
        percepts: list[PerceptPacket],
        *,
        context_id: str,
        timestamp: datetime,
        room: str,
        time_window_ms: int,
    ) -> ContextUpdate:
        return ContextUpdate(
            context_id=context_id,
            timestamp=timestamp,
            time_window_ms=time_window_ms,
            room=room,
            entities=[],
            events=[],
            global_risk=GlobalRisk(safety=0.0, comfort=0.0, maintenance=0.0),
        )


def test_default_registry_resolves_rooms_profile() -> None:
    registry = ContextFusionRegistry.with_defaults()

    fusion = registry.get("rooms")

    assert isinstance(fusion, RoomsFusion)
    assert registry.profile_ids == ("rooms",)


def test_registry_rejects_unknown_profile() -> None:
    registry = ContextFusionRegistry()

    with pytest.raises(UnknownApplicationProfileError) as error:
        registry.get("physical-ai")

    assert error.value.profile_id == "physical-ai"


def test_registry_rejects_duplicate_profile_registration() -> None:
    registry = ContextFusionRegistry([DummyFusion()])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyFusion())


def test_registry_rejects_empty_profile_id() -> None:
    class EmptyProfileFusion(DummyFusion):
        profile_id = " "

    registry = ContextFusionRegistry()

    with pytest.raises(ValueError, match="must not be empty"):
        registry.register(EmptyProfileFusion())
