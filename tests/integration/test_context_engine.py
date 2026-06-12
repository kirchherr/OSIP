from __future__ import annotations

import asyncio
from pathlib import Path

from omnisense_bus import InMemoryBus, context_update_filter
from omnisense_context import ContextEngine
from omnisense_osip import ContextUpdate
from omnisense_sim import ReplayRunner, ScenarioLoader

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


async def run_scenario_through_context_engine(scenario_name: str) -> list[ContextUpdate]:
    bus = InMemoryBus()
    engine = ContextEngine(bus)
    scenario = ScenarioLoader().load(SCENARIO_DIR / scenario_name)

    async with bus.subscribe(context_update_filter()) as context_updates:
        replay = await ReplayRunner(bus).run(scenario)
        updates: list[ContextUpdate] = []
        for published in replay.published_percepts:
            expected = await engine.ingest(published.message.payload)
            delivered = await asyncio.wait_for(context_updates.receive(), timeout=1)
            assert delivered.payload == expected
            assert isinstance(delivered.payload, ContextUpdate)
            updates.append(delivered.payload)

    return updates


async def test_context_engine_detects_required_rooms_contexts() -> None:
    expectations = {
        "kitchen_burning_food.yaml": "context.possible_burning_food",
        "fall_candidate.yaml": "context.possible_fall",
        "stale_air_high_occupancy.yaml": "context.high_occupancy_stale_air",
    }

    for scenario_name, expected_context in expectations.items():
        updates = await run_scenario_through_context_engine(scenario_name)
        labels = [event.label for update in updates for event in update.events]
        assert expected_context in labels


async def test_context_engine_keeps_normal_cooking_without_alarm() -> None:
    updates = await run_scenario_through_context_engine("normal_cooking_no_alarm.yaml")

    assert [event.label for update in updates for event in update.events] == []


async def test_context_engine_publishes_evidence_and_contradictions() -> None:
    updates = await run_scenario_through_context_engine("sensor_conflict_smoke.yaml")
    conflict_events = [
        event
        for update in updates
        for event in update.events
        if event.label == "context.sensor_conflict"
    ]

    assert conflict_events
    assert conflict_events[-1].evidence == ["chemical.air.smoke_like_pattern"]
    assert conflict_events[-1].contradictions == ["vision.no_smoke_visible"]
