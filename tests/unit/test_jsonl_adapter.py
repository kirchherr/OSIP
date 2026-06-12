from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters import JSONLOSIPSourceAdapter
from omnisense_bus import InMemoryBus, model_capabilities_topic, percept_topic
from omnisense_osip import ModelCapabilityDescriptor, PerceptPacket
from pydantic import ValidationError

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


def _load_fixture(name: str) -> dict[str, object]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        msg = f"{name} must decode to a JSON object"
        raise TypeError(msg)
    return cast(dict[str, object], decoded)


def _write_trace(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, separators=(",", ":")) for record in records),
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_jsonl_source_adapter_validates_and_publishes_osip_messages(
    tmp_path: Path,
) -> None:
    trace_path = tmp_path / "trace.jsonl"
    _write_trace(
        trace_path,
        [
            {
                "topic": model_capabilities_topic(),
                "payload": _load_fixture("model_capability.json"),
            },
            {
                "topic": percept_topic("audio", "audio.event_classifier_v1"),
                "payload": _load_fixture("percept_packet.json"),
            },
        ],
    )
    adapter = JSONLOSIPSourceAdapter(trace_path, profile_id="rooms")
    bus = InMemoryBus()

    async with bus.subscribe("omnisense.>") as subscription:
        result = await adapter.publish_to(bus)
        capability_message = await subscription.receive()
        percept_message = await subscription.receive()

    assert adapter.metadata.adapter_id == "jsonl.osip_source"
    assert adapter.metadata.role == "source"
    assert adapter.metadata.requires_hardware is False
    assert result.published_count == 2
    assert result.topics == (
        model_capabilities_topic(),
        percept_topic("audio", "audio.event_classifier_v1"),
    )
    assert result.target_topics == ()
    assert result.message_types == ("model.capability", "percept.packet")
    assert isinstance(capability_message.payload, ModelCapabilityDescriptor)
    assert isinstance(percept_message.payload, PerceptPacket)


@pytest.mark.asyncio
async def test_jsonl_source_adapter_rejects_disallowed_message_type(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    _write_trace(
        trace_path,
        [
            {
                "topic": model_capabilities_topic(),
                "payload": _load_fixture("model_capability.json"),
            }
        ],
    )
    adapter = JSONLOSIPSourceAdapter(trace_path, allowed_message_types=("percept.packet",))

    with pytest.raises(ValueError, match="not allowed"):
        await adapter.publish_to(InMemoryBus())


def test_adapter_metadata_rejects_invalid_adapter_id(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        JSONLOSIPSourceAdapter(tmp_path / "trace.jsonl", adapter_id="Bad Adapter")


def test_jsonl_source_adapter_requires_allowed_message_types(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="allowed_message_types"):
        JSONLOSIPSourceAdapter(tmp_path / "trace.jsonl", allowed_message_types=())
