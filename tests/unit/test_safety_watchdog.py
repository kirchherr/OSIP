from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from omnisense_osip import AdapterHeartbeat, ContextUpdate, ProfileSafetyCase
from omnisense_safety import SafetyWatchdog, evaluate_safety_case

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "osip"


def load_fixture(filename: str) -> dict[str, Any]:
    data = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def load_safety_case() -> ProfileSafetyCase:
    return ProfileSafetyCase.model_validate(load_fixture("profile_safety_case.json"))


def load_context(*, timestamp: datetime) -> ContextUpdate:
    data = load_fixture("context_update.json")
    data["timestamp"] = timestamp.isoformat()
    return ContextUpdate.model_validate(data)


def load_heartbeat(*, timestamp: datetime, status: str = "alive") -> AdapterHeartbeat:
    data = load_fixture("adapter_heartbeat.json")
    data["timestamp"] = timestamp.isoformat()
    data["status"] = status
    return AdapterHeartbeat.model_validate(data)


def test_watchdog_accepts_fresh_context_and_heartbeat() -> None:
    now = datetime(2026, 6, 12, 14, 31, 9, 400000, tzinfo=UTC)
    context = load_context(timestamp=now - timedelta(milliseconds=50))
    heartbeat = load_heartbeat(timestamp=now - timedelta(milliseconds=20))

    evaluation = SafetyWatchdog(load_safety_case()).evaluate(
        now=now,
        context=context,
        heartbeats=[heartbeat],
    )

    assert evaluation.safe
    assert evaluation.activations == ()


def test_watchdog_activates_context_stale_safe_state() -> None:
    now = datetime(2026, 6, 12, 14, 31, 9, 400000, tzinfo=UTC)
    context = load_context(timestamp=now - timedelta(milliseconds=150))
    heartbeat = load_heartbeat(timestamp=now - timedelta(milliseconds=20))

    evaluation = evaluate_safety_case(
        load_safety_case(),
        now=now,
        context=context,
        heartbeats=[heartbeat],
    )

    assert not evaluation.safe
    assert [(item.target, item.safe_state, item.trigger) for item in evaluation.activations] == [
        ("robot.arm", "robot.safe_stop", "context_stale")
    ]
    assert evaluation.activations[0].age_ms == 150
    assert evaluation.activations[0].requires_hardware_interlock


def test_watchdog_activates_heartbeat_timeout_safe_state() -> None:
    now = datetime(2026, 6, 12, 14, 31, 9, 400000, tzinfo=UTC)
    context = load_context(timestamp=now - timedelta(milliseconds=20))
    heartbeat = load_heartbeat(timestamp=now - timedelta(milliseconds=80))

    evaluation = evaluate_safety_case(
        load_safety_case(),
        now=now,
        context=context,
        heartbeats=[heartbeat],
    )

    assert not evaluation.safe
    assert [(item.target, item.safe_state, item.trigger) for item in evaluation.activations] == [
        ("robot.arm", "robot.safe_stop", "heartbeat_timeout")
    ]
    assert evaluation.activations[0].age_ms == 80


def test_watchdog_maps_adapter_failure_to_adapter_error_safe_state() -> None:
    now = datetime(2026, 6, 12, 14, 31, 9, 400000, tzinfo=UTC)
    context = load_context(timestamp=now - timedelta(milliseconds=20))
    heartbeat = load_heartbeat(timestamp=now - timedelta(milliseconds=20), status="failed")

    evaluation = evaluate_safety_case(
        load_safety_case(),
        now=now,
        context=context,
        heartbeats=[heartbeat],
    )

    assert not evaluation.safe
    assert [(item.target, item.safe_state, item.trigger) for item in evaluation.activations] == [
        ("hvac.living_room", "hvac.off", "adapter_error")
    ]
    assert "status is failed" in evaluation.activations[0].reason


def test_watchdog_activates_bus_disconnect_and_manual_estop_safe_states() -> None:
    now = datetime(2026, 6, 12, 14, 31, 9, 400000, tzinfo=UTC)
    context = load_context(timestamp=now - timedelta(milliseconds=20))
    heartbeat = load_heartbeat(timestamp=now - timedelta(milliseconds=20))

    evaluation = evaluate_safety_case(
        load_safety_case(),
        now=now,
        context=context,
        heartbeats=[heartbeat],
        bus_connected=False,
        manual_estop=True,
    )

    assert not evaluation.safe
    assert [(item.target, item.safe_state, item.trigger) for item in evaluation.activations] == [
        ("hvac.living_room", "hvac.off", "bus_disconnect"),
        ("robot.arm", "robot.safe_stop", "manual_estop"),
    ]


def test_watchdog_rejects_naive_now() -> None:
    with pytest.raises(ValueError, match="timezone"):
        evaluate_safety_case(
            load_safety_case(),
            now=datetime(2026, 6, 12, 14, 31, 9),
        )
