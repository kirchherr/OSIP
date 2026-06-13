from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from omnisense_context import ContextGraph, ContextGraphSnapshot
from omnisense_osip import ContextUpdate
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]


def load_context() -> ContextUpdate:
    data = json.loads((ROOT / "tests" / "fixtures" / "osip" / "context_update.json").read_text())
    assert isinstance(data, dict)
    return ContextUpdate.model_validate(data)


def context_variant(**updates: Any) -> ContextUpdate:
    return load_context().model_copy(update=updates)


def test_context_graph_tracks_latest_context_per_room() -> None:
    first = load_context()
    second = context_variant(
        context_id="ctx_20260612_143110_002",
        timestamp=first.timestamp + timedelta(seconds=1),
    )
    graph = ContextGraph(graph_id="rooms")

    graph.apply(second)
    graph.apply(first)

    assert graph.latest(room="living_room") == second
    assert graph.latest() == second
    assert graph.updates(room="living_room") == (first, second)
    assert graph.stats().total_updates == 2
    assert graph.stats().rooms == ("living_room",)


def test_context_graph_returns_entity_and_event_records_with_provenance() -> None:
    update = load_context()
    graph = ContextGraph(graph_id="rooms", updates=(update,))

    entity_records = graph.entity_records(entity_id="person_anon_1")
    event_records = graph.event_records(label="event.fall_candidate")

    assert len(entity_records) == 1
    assert entity_records[0].context_id == update.context_id
    assert entity_records[0].room == "living_room"
    assert entity_records[0].entity.state == "possibly_on_floor"
    assert len(event_records) == 1
    assert event_records[0].event.evidence == [
        "tactile.floor_pressure_spike",
        "audio.impact_sound",
        "radar.motion_drop",
    ]


def test_context_graph_snapshot_roundtrips_through_json() -> None:
    first = load_context()
    second = context_variant(
        context_id="ctx_kitchen_001",
        room="kitchen",
        timestamp=first.timestamp + timedelta(seconds=2),
    )
    graph = ContextGraph(graph_id="replay", updates=(first, second))
    generated_at = second.timestamp + timedelta(milliseconds=10)

    payload = graph.to_json(generated_at=generated_at)
    restored = ContextGraph.from_json(payload)

    assert restored.graph_id == "replay"
    assert restored.latest(room="living_room") == first
    assert restored.latest(room="kitchen") == second
    assert restored.snapshot(generated_at=generated_at) == graph.snapshot(generated_at=generated_at)


def test_context_graph_rejects_duplicate_context_ids() -> None:
    update = load_context()
    graph = ContextGraph(updates=(update,))

    with pytest.raises(ValueError, match="already exists"):
        graph.apply(update)


def test_context_graph_snapshot_validates_latest_context_references() -> None:
    update = load_context()

    with pytest.raises(ValidationError, match="does not exist"):
        ContextGraphSnapshot.model_validate(
            {
                "graph_id": "bad_snapshot",
                "generated_at": update.timestamp.isoformat(),
                "updates": [update.model_dump(mode="json")],
                "latest_context_by_room": {"living_room": "missing_context"},
            }
        )

    with pytest.raises(ValidationError, match="not 'kitchen'"):
        ContextGraphSnapshot.model_validate(
            {
                "graph_id": "bad_room",
                "generated_at": update.timestamp.isoformat(),
                "updates": [update.model_dump(mode="json")],
                "latest_context_by_room": {"kitchen": update.context_id},
            }
        )


def test_context_graph_snapshot_rejects_naive_generated_at() -> None:
    update = load_context()

    with pytest.raises(ValidationError, match="timezone"):
        ContextGraphSnapshot.model_validate(
            {
                "graph_id": "bad_time",
                "generated_at": "2026-06-12T14:31:09.350",
                "updates": [update.model_dump(mode="json")],
                "latest_context_by_room": {"living_room": update.context_id},
            }
        )


def test_context_graph_empty_snapshot_is_deterministic() -> None:
    graph = ContextGraph(graph_id="empty")
    snapshot = graph.snapshot()

    assert snapshot.generated_at.isoformat() == "1970-01-01T00:00:00+00:00"
    assert snapshot.updates == ()
    assert snapshot.latest_context_by_room == {}
