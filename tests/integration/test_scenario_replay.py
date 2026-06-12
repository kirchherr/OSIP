from __future__ import annotations

import asyncio
from pathlib import Path

from omnisense_bus import InMemoryBus, percept_filter
from omnisense_osip import PerceptPacket
from omnisense_sim import ReplayRunner, ScenarioLoader, SimulatedClock

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


async def test_kitchen_scenario_replays_percepts_with_virtual_timing() -> None:
    bus = InMemoryBus()
    clock = SimulatedClock()
    runner = ReplayRunner(bus, clock=clock)

    async with bus.subscribe(percept_filter()) as subscription:
        result = await runner.run(SCENARIO_DIR / "kitchen_burning_food.yaml")
        received = [
            await asyncio.wait_for(subscription.receive(), timeout=1)
            for _ in result.published_percepts
        ]

    assert [item.at_ms for item in result.published_percepts] == [0, 120, 250, 320]
    assert result.final_time_ms == 3000
    assert clock.current_ms == 3000
    assert [message.topic for message in received] == result.topics
    assert all(isinstance(message.payload, PerceptPacket) for message in received)


async def test_replay_accepts_loaded_scenario_definition() -> None:
    bus = InMemoryBus()
    loader = ScenarioLoader()
    scenario = loader.load(SCENARIO_DIR / "fall_candidate.yaml")
    runner = ReplayRunner(bus)

    result = await runner.run(scenario)

    assert result.scenario.id == "fall_candidate"
    assert [item.at_ms for item in result.published_percepts] == [0, 70, 140]
    assert result.topics == [
        "omnisense.percepts.tactile.tactile.floor_pressure_v1",
        "omnisense.percepts.audio.audio.event_classifier_v1",
        "omnisense.percepts.radar.radar.motion_v1",
    ]


async def test_required_rooms_scenarios_publish_expected_percept_counts() -> None:
    loader = ScenarioLoader()
    scenarios = loader.load_many(
        [
            SCENARIO_DIR / "kitchen_burning_food.yaml",
            SCENARIO_DIR / "fall_candidate.yaml",
            SCENARIO_DIR / "stale_air_high_occupancy.yaml",
        ]
    )

    results = []
    for scenario in scenarios:
        bus = InMemoryBus()
        results.append(await ReplayRunner(bus).run(scenario))

    assert [len(result.published_percepts) for result in results] == [4, 3, 3]
    assert [result.final_time_ms for result in results] == [3000, 2500, 4000]
