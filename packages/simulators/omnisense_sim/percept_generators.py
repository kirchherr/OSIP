"""Build OSIP percept packets from scenario events."""

from __future__ import annotations

from omnisense_bus import percept_topic
from omnisense_osip import PerceptPacket
from omnisense_osip.schemas import EmbeddingRef

from omnisense_sim.clocks import SimulatedClock
from omnisense_sim.schemas import ScenarioDefinition, ScenarioPercept


def scenario_topic(percept: ScenarioPercept) -> str:
    return percept_topic(percept.modality, percept.source_model)


def build_percept_packet(
    scenario: ScenarioDefinition,
    percept: ScenarioPercept,
    *,
    index: int,
    clock: SimulatedClock,
) -> PerceptPacket:
    timestamp = clock.datetime_at(percept.at_ms)
    received_at = clock.datetime_at(percept.at_ms + percept.latency_ms)
    packet_id = percept.id or f"{scenario.id}:percept:{index:04d}"
    embedding = None
    if percept.embedding is not None:
        embedding = EmbeddingRef.model_validate(percept.embedding)

    return PerceptPacket(
        id=packet_id,
        source_model=percept.source_model,
        modality=percept.modality,
        timestamp=timestamp,
        received_at=received_at,
        valid_for_ms=percept.valid_for_ms,
        latency_ms=percept.latency_ms,
        location=percept.location,
        claims=percept.claims,
        embedding=embedding,
        quality=percept.quality.to_sensor_quality(),
    )
