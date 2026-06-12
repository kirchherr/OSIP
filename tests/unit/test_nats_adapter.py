from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters import (
    NatsBridgeCodec,
    NatsInboundBridge,
    NatsInboundMessage,
    NatsOutboundBridge,
    NatsPublishRecord,
    NatsSubjectMapper,
    ensure_nats_subject,
)
from omnisense_bus import (
    InMemoryBus,
    model_capabilities_topic,
    percept_filter,
    percept_topic,
    profile_safety_case_topic,
)
from omnisense_osip import PerceptPacket, ProfileSafetyCase

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


class RecordingNatsTransport:
    def __init__(self) -> None:
        self.records: list[NatsPublishRecord] = []

    async def publish(self, record: NatsPublishRecord) -> None:
        self.records.append(record)


class QueuedNatsSource:
    def __init__(self, messages: list[NatsInboundMessage]) -> None:
        self.messages = list(messages)

    async def receive(self) -> NatsInboundMessage | None:
        if not self.messages:
            return None
        return self.messages.pop(0)


def _load_fixture(name: str) -> dict[str, object]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        msg = f"{name} must decode to a JSON object"
        raise TypeError(msg)
    return cast(dict[str, object], decoded)


def test_nats_subject_mapper_roundtrips_publish_subjects() -> None:
    mapper = NatsSubjectMapper()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    nats_subject = mapper.nats_subject_for_bus_topic(bus_topic)

    assert nats_subject == "omnisense.percepts.audio.audio.event_classifier_v1"
    assert mapper.bus_topic_for_nats_subject(nats_subject) == bus_topic


def test_nats_subject_mapper_supports_deployment_prefixes_and_wildcards() -> None:
    mapper = NatsSubjectMapper(subject_prefix="site_a.osip")

    assert mapper.nats_filter_for_bus_filter(percept_filter("audio")) == (
        "site_a.osip.percepts.audio.>"
    )
    assert mapper.bus_filter_for_nats_filter("site_a.osip.percepts.*.>") == (
        "omnisense.percepts.*.>"
    )


def test_nats_subject_mapper_rejects_invalid_wildcards() -> None:
    mapper = NatsSubjectMapper()

    with pytest.raises(ValueError, match="final segment"):
        mapper.bus_filter_for_nats_filter("omnisense.percepts.>.bad")


def test_nats_subject_validation_rejects_publish_wildcards() -> None:
    with pytest.raises(ValueError, match="wildcards"):
        ensure_nats_subject("omnisense.percepts.>")


def test_nats_bridge_codec_encodes_percept_as_core_subject() -> None:
    codec = NatsBridgeCodec()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    record = codec.encode_publish(bus_topic, _load_fixture("percept_packet.json"))

    assert record.nats_subject == "omnisense.percepts.audio.audio.event_classifier_v1"
    assert record.bus_topic == bus_topic
    assert record.mode == "core"
    assert record.ack_policy == "none"
    assert record.retain_last_per_subject is False
    assert record.max_msgs_per_subject == 1
    assert record.max_age_ms == 50
    assert record.message_type == "percept.packet"
    assert b'"type":"percept.packet"' in record.payload


def test_nats_bridge_codec_encodes_safety_case_as_jetstream_record() -> None:
    codec = NatsBridgeCodec()
    bus_topic = profile_safety_case_topic("physical-ai")

    record = codec.encode_publish(bus_topic, _load_fixture("profile_safety_case.json"))

    assert record.nats_subject == "omnisense.safety.profiles.physical-ai.safe_states"
    assert record.mode == "jetstream"
    assert record.ack_policy == "explicit"
    assert record.retain_last_per_subject is True
    assert record.max_msgs_per_subject == 8
    assert record.max_age_ms is None
    assert record.message_type == "profile.safety_case"


def test_nats_bridge_codec_decodes_inbound_message_to_bus_record() -> None:
    codec = NatsBridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )

    inbound = codec.decode_message(outbound.nats_subject, outbound.payload)

    assert inbound.bus_topic == outbound.bus_topic
    assert inbound.message_type == "percept.packet"
    assert isinstance(inbound.payload, PerceptPacket)


def test_nats_bridge_codec_rejects_topic_message_mismatch() -> None:
    codec = NatsBridgeCodec()

    with pytest.raises(ValueError, match="expects 'percept.packet'"):
        codec.encode_publish(
            percept_topic("audio", "audio.event_classifier_v1"),
            _load_fixture("profile_safety_case.json"),
        )


def test_nats_bridge_codec_rejects_unknown_bus_topic() -> None:
    codec = NatsBridgeCodec()

    with pytest.raises(ValueError, match="no OSIP channel id"):
        codec.encode_publish("omnisense.unknown.topic", _load_fixture("percept_packet.json"))


def test_nats_bridge_codec_decodes_prefixed_subjects() -> None:
    codec = NatsBridgeCodec(NatsSubjectMapper(subject_prefix="site_a.osip"))
    outbound = codec.encode_publish(
        profile_safety_case_topic("physical-ai"),
        _load_fixture("profile_safety_case.json"),
    )

    inbound = codec.decode_message(outbound.nats_subject, outbound.payload)

    assert outbound.nats_subject == "site_a.osip.safety.profiles.physical-ai.safe_states"
    assert inbound.bus_topic == profile_safety_case_topic("physical-ai")
    assert isinstance(inbound.payload, ProfileSafetyCase)


def test_nats_channel_mapping_still_handles_model_capabilities() -> None:
    codec = NatsBridgeCodec()

    record = codec.encode_publish(
        model_capabilities_topic(),
        _load_fixture("model_capability.json"),
    )

    assert record.nats_subject == "omnisense.models.capabilities"
    assert record.mode == "jetstream"
    assert record.ack_policy == "explicit"


@pytest.mark.asyncio
async def test_nats_outbound_bridge_publishes_through_transport() -> None:
    transport = RecordingNatsTransport()
    bridge = NatsOutboundBridge(transport, profile_id="rooms")
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    result = await bridge.publish_message(bus_topic, _load_fixture("percept_packet.json"))

    assert bridge.metadata.adapter_id == "nats.outbound_bridge"
    assert bridge.metadata.role == "sink"
    assert bridge.metadata.requires_hardware is False
    assert result.published_count == 1
    assert result.topics == (bus_topic,)
    assert result.target_topics == ("omnisense.percepts.audio.audio.event_classifier_v1",)
    assert result.message_types == ("percept.packet",)
    assert len(transport.records) == 1
    assert transport.records[0].mode == "core"


@pytest.mark.asyncio
async def test_nats_outbound_bridge_rejects_unsupported_message_type() -> None:
    transport = RecordingNatsTransport()
    bridge = NatsOutboundBridge(transport, supported_message_types=("profile.safety_case",))

    with pytest.raises(ValueError, match="not supported"):
        await bridge.publish_message(
            percept_topic("audio", "audio.event_classifier_v1"),
            _load_fixture("percept_packet.json"),
        )

    assert transport.records == []


def test_nats_outbound_bridge_requires_supported_message_types() -> None:
    with pytest.raises(ValueError, match="supported_message_types"):
        NatsOutboundBridge(RecordingNatsTransport(), supported_message_types=())


@pytest.mark.asyncio
async def test_nats_inbound_bridge_decodes_and_publishes_to_bus() -> None:
    codec = NatsBridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    source = QueuedNatsSource(
        [
            NatsInboundMessage(
                nats_subject=outbound.nats_subject,
                payload=outbound.payload,
            )
        ]
    )
    bridge = NatsInboundBridge(source, profile_id="rooms", codec=codec)
    bus = InMemoryBus()

    async with bus.subscribe("omnisense.>") as subscription:
        result = await bridge.publish_to(bus)
        message = await subscription.receive()

    assert bridge.metadata.adapter_id == "nats.inbound_bridge"
    assert bridge.metadata.role == "source"
    assert result.published_count == 1
    assert result.topics == (percept_topic("audio", "audio.event_classifier_v1"),)
    assert result.target_topics == ("omnisense.percepts.audio.audio.event_classifier_v1",)
    assert result.message_types == ("percept.packet",)
    assert isinstance(message.payload, PerceptPacket)


@pytest.mark.asyncio
async def test_nats_inbound_bridge_honors_max_messages() -> None:
    codec = NatsBridgeCodec()
    percept = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    safety = codec.encode_publish(
        profile_safety_case_topic("physical-ai"),
        _load_fixture("profile_safety_case.json"),
    )
    source = QueuedNatsSource(
        [
            NatsInboundMessage(nats_subject=percept.nats_subject, payload=percept.payload),
            NatsInboundMessage(nats_subject=safety.nats_subject, payload=safety.payload),
        ]
    )
    bridge = NatsInboundBridge(source, codec=codec)

    result = await bridge.publish_to(InMemoryBus(), max_messages=1)

    assert result.published_count == 1
    assert result.message_types == ("percept.packet",)
    assert len(source.messages) == 1


@pytest.mark.asyncio
async def test_nats_inbound_bridge_rejects_unsupported_message_type() -> None:
    codec = NatsBridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    source = QueuedNatsSource(
        [NatsInboundMessage(nats_subject=outbound.nats_subject, payload=outbound.payload)]
    )
    bridge = NatsInboundBridge(
        source,
        codec=codec,
        supported_message_types=("profile.safety_case",),
    )
    bus = InMemoryBus()

    async with bus.subscribe("omnisense.>") as subscription:
        with pytest.raises(ValueError, match="not supported"):
            await bridge.publish_to(bus)
        assert subscription.pending_count == 0


@pytest.mark.asyncio
async def test_nats_inbound_bridge_rejects_invalid_max_messages() -> None:
    bridge = NatsInboundBridge(QueuedNatsSource([]))

    with pytest.raises(ValueError, match="max_messages"):
        await bridge.publish_to(InMemoryBus(), max_messages=-1)


def test_nats_inbound_bridge_requires_supported_message_types() -> None:
    with pytest.raises(ValueError, match="supported_message_types"):
        NatsInboundBridge(QueuedNatsSource([]), supported_message_types=())
