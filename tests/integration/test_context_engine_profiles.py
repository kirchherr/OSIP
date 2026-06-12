from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from omnisense_bus import InMemoryBus, context_update_filter, context_update_topic
from omnisense_context import (
    ContextEngine,
    ContextFusionRegistry,
    UnknownApplicationProfileError,
)
from omnisense_osip import (
    Claim,
    ContextEvent,
    ContextUpdate,
    GlobalRisk,
    Location,
    PerceptPacket,
    SensorQuality,
)


class ProfileTestFusion:
    profile_id = "xxx"

    def __init__(self) -> None:
        self.seen_percept_ids: list[str] = []

    def fuse(
        self,
        percepts: list[PerceptPacket],
        *,
        context_id: str,
        timestamp: datetime,
        room: str,
        time_window_ms: int,
    ) -> ContextUpdate:
        self.seen_percept_ids = [percept.id for percept in percepts]
        return ContextUpdate(
            context_id=context_id,
            timestamp=timestamp,
            time_window_ms=time_window_ms,
            room=room,
            entities=[],
            events=[
                ContextEvent(
                    label="context.profile_test",
                    confidence=0.9,
                    urgency=0.1,
                    evidence=["profile.input"],
                    contradictions=[],
                )
            ],
            global_risk=GlobalRisk(safety=0.0, comfort=0.0, maintenance=0.0),
        )


def build_test_percept() -> PerceptPacket:
    timestamp = datetime(2026, 6, 12, 8, 0, tzinfo=UTC)
    return PerceptPacket(
        trace_id="trace_profile_test",
        correlation_id="corr_profile_test",
        id="percept_profile_test",
        source_model="profile_test_model",
        modality="test",
        timestamp=timestamp,
        received_at=timestamp,
        valid_for_ms=1000,
        latency_ms=0,
        location=Location(room="lab"),
        claims=[Claim(label="profile.input", confidence=1.0, value=True)],
        quality=SensorQuality(status="usable"),
    )


async def test_context_engine_uses_registered_application_profile() -> None:
    bus = InMemoryBus()
    fusion = ProfileTestFusion()
    engine = ContextEngine(
        bus,
        application_profile="xxx",
        registry=ContextFusionRegistry([fusion]),
    )

    async with bus.subscribe(context_update_filter()) as context_updates:
        update = await engine.ingest(build_test_percept())
        delivered = await asyncio.wait_for(context_updates.receive(), timeout=1)

    assert engine.application_profile == "xxx"
    assert fusion.seen_percept_ids == ["percept_profile_test"]
    assert update.trace_id == "trace_profile_test"
    assert update.correlation_id == "corr_profile_test"
    assert [event.label for event in update.events] == ["context.profile_test"]
    assert delivered.topic == context_update_topic("lab")
    assert delivered.payload == update


def test_context_engine_rejects_unregistered_application_profile() -> None:
    with pytest.raises(UnknownApplicationProfileError) as error:
        ContextEngine(
            InMemoryBus(),
            application_profile="physical-ai",
            registry=ContextFusionRegistry(),
        )

    assert error.value.profile_id == "physical-ai"
