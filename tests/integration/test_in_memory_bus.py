from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from omnisense_bus import InMemoryBus, percept_filter, percept_topic, replay_jsonl
from omnisense_osip import PerceptPacket, validate_osip_message

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


async def test_percept_can_be_published_and_received() -> None:
    bus = InMemoryBus()
    percept = PerceptPacket.model_validate(
        load_json(FIXTURE_DIR / "osip" / "percept_packet.json")
    )
    topic = percept_topic(percept.modality, percept.source_model)

    async with bus.subscribe(topic) as subscription:
        published = await bus.publish(topic, percept)
        received = await asyncio.wait_for(subscription.receive(), timeout=1)

    assert received == published
    assert received.payload == percept
    assert received.sequence == 1


async def test_multiple_subscribers_receive_same_message() -> None:
    bus = InMemoryBus()
    topic = percept_topic("audio", "audio.event_classifier_v1")

    async with bus.subscribe(percept_filter("audio")) as first:
        async with bus.subscribe(percept_filter()) as second:
            published = await bus.publish(topic, {"id": "perc_1"})
            received_first = await asyncio.wait_for(first.receive(), timeout=1)
            received_second = await asyncio.wait_for(second.receive(), timeout=1)

    assert received_first == published
    assert received_second == published


async def test_order_is_deterministic_within_topic() -> None:
    bus = InMemoryBus()
    topic = percept_topic("audio", "audio.event_classifier_v1")

    async with bus.subscribe(topic) as subscription:
        await bus.publish(topic, "first")
        await bus.publish(topic, "second")
        first = await asyncio.wait_for(subscription.receive(), timeout=1)
        second = await asyncio.wait_for(subscription.receive(), timeout=1)

    assert [first.payload, second.payload] == ["first", "second"]
    assert [first.sequence, second.sequence] == [1, 2]


async def test_unmatched_topic_is_not_delivered() -> None:
    bus = InMemoryBus()

    async with bus.subscribe(percept_filter("audio")) as subscription:
        await bus.publish(percept_topic("rgb", "vision.pose_activity_v1"), {"id": "perc_vision"})
        assert subscription.pending_count == 0


async def test_jsonl_replay_publishes_validated_payloads() -> None:
    bus = InMemoryBus()

    async with bus.subscribe(percept_filter("audio")) as subscription:
        published = await replay_jsonl(
            bus,
            FIXTURE_DIR / "bus" / "percept_trace.jsonl",
            payload_parser=validate_osip_message,
        )
        received = await asyncio.wait_for(subscription.receive(), timeout=1)

    assert len(published) == 1
    assert received == published[0]
    assert isinstance(received.payload, PerceptPacket)
