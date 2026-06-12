from __future__ import annotations

import json
from pathlib import Path

from omnisense_context import TemporalWindow
from omnisense_osip import PerceptPacket

ROOT = Path(__file__).resolve().parents[2]


def load_percept() -> PerceptPacket:
    data = json.loads((ROOT / "tests" / "fixtures" / "osip" / "percept_packet.json").read_text())
    return PerceptPacket.model_validate(data)


def test_temporal_window_returns_active_percepts() -> None:
    percept = load_percept()
    window = TemporalWindow(window_ms=1000)
    window.add(percept)

    active = window.active_at(percept.timestamp)

    assert active == [percept]


def test_temporal_window_prunes_expired_percepts() -> None:
    percept = load_percept()
    window = TemporalWindow(window_ms=1000)
    window.add(percept)
    after_expiry = percept.timestamp.replace(second=percept.timestamp.second + 2)

    assert window.active_at(after_expiry) == []
