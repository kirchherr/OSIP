from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters.sensor import SensorReading, SensorToPerceptAdapter
from omnisense_bus import InMemoryBus, percept_topic
from omnisense_osip import ModelCapabilityDescriptor, PerceptPacket
from pydantic import ValidationError

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


class QueuedSensorSource:
    def __init__(self, readings: list[SensorReading]) -> None:
        self.readings = list(readings)

    async def receive(self) -> SensorReading | None:
        if not self.readings:
            return None
        return self.readings.pop(0)


def _load_fixture(name: str) -> dict[str, object]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        msg = f"{name} must decode to a JSON object"
        raise TypeError(msg)
    return cast(dict[str, object], decoded)


def _capability() -> ModelCapabilityDescriptor:
    return ModelCapabilityDescriptor.model_validate(_load_fixture("model_capability.json"))


def _reading(**updates: object) -> SensorReading:
    payload = _load_fixture("percept_packet.json")
    data: dict[str, object] = {
        "reading_id": "reading_0001",
        "modality": "rgb",
        "timestamp": payload["timestamp"],
        "received_at": payload["received_at"],
        "valid_for_ms": payload["valid_for_ms"],
        "latency_ms": payload["latency_ms"],
        "location": payload["location"],
        "claims": [
            {"label": "person.presence", "confidence": 0.91, "value": True},
            {"label": "person.pose", "confidence": 0.74, "value": {"state": "standing"}},
        ],
        "quality": payload["quality"],
        "trace_id": "trace_sensor_001",
        "correlation_id": "corr_sensor_001",
        "raw": {"frame_id": "frame_001"},
        "metadata": {"adapter": "test_camera"},
    }
    data.update(updates)
    return SensorReading.model_validate(data)


def test_sensor_adapter_builds_percept_from_reading() -> None:
    adapter = SensorToPerceptAdapter(QueuedSensorSource([]), _capability(), profile_id="rooms")
    reading = _reading()

    percept = adapter.build_percept(reading)

    assert percept.id == "reading_0001"
    assert percept.source_model == "vision.pose_activity_v1"
    assert percept.modality == "rgb"
    assert percept.trace_id == "trace_sensor_001"
    assert percept.correlation_id == "corr_sensor_001"
    assert [claim.label for claim in percept.claims] == ["person.presence", "person.pose"]
    assert adapter.metadata.adapter_id == "sensor.percept_source"
    assert adapter.metadata.role == "source"
    assert adapter.metadata.requires_hardware is False


@pytest.mark.asyncio
async def test_sensor_adapter_publishes_readings_to_bus() -> None:
    source = QueuedSensorSource([_reading(), _reading(reading_id="reading_0002")])
    adapter = SensorToPerceptAdapter(source, _capability())
    bus = InMemoryBus()
    topic = percept_topic("rgb", "vision.pose_activity_v1")

    async with bus.subscribe("omnisense.>") as subscription:
        result = await adapter.publish_to(bus)
        first = await subscription.receive()
        second = await subscription.receive()

    assert result.published_count == 2
    assert result.topics == (topic, topic)
    assert result.message_types == ("percept.packet", "percept.packet")
    assert isinstance(first.payload, PerceptPacket)
    assert isinstance(second.payload, PerceptPacket)
    assert first.payload.id == "reading_0001"
    assert second.payload.id == "reading_0002"


@pytest.mark.asyncio
async def test_sensor_adapter_honors_max_readings() -> None:
    source = QueuedSensorSource([_reading(), _reading(reading_id="reading_0002")])
    adapter = SensorToPerceptAdapter(source, _capability())

    result = await adapter.publish_to(InMemoryBus(), max_readings=1)

    assert result.published_count == 1
    assert len(source.readings) == 1


@pytest.mark.asyncio
async def test_sensor_adapter_rejects_invalid_max_readings() -> None:
    adapter = SensorToPerceptAdapter(QueuedSensorSource([]), _capability())

    with pytest.raises(ValueError, match="max_readings"):
        await adapter.publish_to(InMemoryBus(), max_readings=-1)


def test_sensor_adapter_rejects_undeclared_modality() -> None:
    adapter = SensorToPerceptAdapter(QueuedSensorSource([]), _capability())

    with pytest.raises(ValueError, match="modality"):
        adapter.build_percept(_reading(modality="thermal"))


def test_sensor_adapter_rejects_undeclared_claims() -> None:
    adapter = SensorToPerceptAdapter(QueuedSensorSource([]), _capability())

    with pytest.raises(ValueError, match="not declared"):
        adapter.build_percept(
            _reading(claims=[{"label": "audio.impact_sound", "confidence": 0.8, "value": True}])
        )


def test_sensor_adapter_requires_percept_message_support() -> None:
    with pytest.raises(ValueError, match="percept.packet"):
        SensorToPerceptAdapter(
            QueuedSensorSource([]),
            _capability(),
            supported_message_types=("model.capability",),
        )


def test_sensor_reading_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        _reading(timestamp="2026-06-12T12:00:00")
