from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from omnisense_context import RoomsFusion
from omnisense_osip import PerceptPacket
from omnisense_sim import ScenarioLoader, SimulatedClock, build_percept_packet

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


def build_percepts(scenario_name: str) -> list[PerceptPacket]:
    scenario = ScenarioLoader().load(SCENARIO_DIR / scenario_name)
    clock = SimulatedClock(start_time=datetime(2026, 6, 12, tzinfo=UTC))
    return [
        build_percept_packet(scenario, event, index=index, clock=clock)
        for index, event in enumerate(scenario.percepts, start=1)
    ]


def event_labels_for(scenario_name: str) -> list[str]:
    percepts = build_percepts(scenario_name)
    timestamp = percepts[-1].received_at or percepts[-1].timestamp
    location = percepts[-1].location
    room = location.room if location is not None and location.room is not None else "unknown_room"
    update = RoomsFusion().fuse(
        percepts,
        context_id="ctx_test",
        timestamp=timestamp,
        room=room,
        time_window_ms=1000,
    )
    return [event.label for event in update.events]


def test_rooms_fusion_detects_burning_food() -> None:
    assert "context.possible_burning_food" in event_labels_for("kitchen_burning_food.yaml")


def test_rooms_fusion_detects_fall_candidate() -> None:
    assert "context.possible_fall" in event_labels_for("fall_candidate.yaml")


def test_rooms_fusion_detects_stale_air() -> None:
    assert "context.high_occupancy_stale_air" in event_labels_for(
        "stale_air_high_occupancy.yaml"
    )


def test_rooms_fusion_keeps_normal_cooking_quiet() -> None:
    assert event_labels_for("normal_cooking_no_alarm.yaml") == []


def test_rooms_fusion_reports_sensor_conflict() -> None:
    assert event_labels_for("sensor_conflict_smoke.yaml") == ["context.sensor_conflict"]
