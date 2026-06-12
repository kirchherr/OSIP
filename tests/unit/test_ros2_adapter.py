from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters import (
    ROS2_JSON_MESSAGE_TYPE,
    Ros2BridgeCodec,
    Ros2InboundBridge,
    Ros2InboundMessage,
    Ros2OutboundBridge,
    Ros2PublishRecord,
    Ros2TopicMapper,
    ensure_ros2_namespace,
    ensure_ros2_topic_name,
)
from omnisense_bus import InMemoryBus, percept_topic, profile_safety_case_topic
from omnisense_osip import PerceptPacket, ProfileSafetyCase

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


class RecordingRos2Transport:
    def __init__(self) -> None:
        self.records: list[Ros2PublishRecord] = []

    async def publish(self, record: Ros2PublishRecord) -> None:
        self.records.append(record)


class QueuedRos2Source:
    def __init__(self, messages: list[Ros2InboundMessage]) -> None:
        self.messages = list(messages)

    async def receive(self) -> Ros2InboundMessage | None:
        if not self.messages:
            return None
        return self.messages.pop(0)


def _load_fixture(name: str) -> dict[str, object]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        msg = f"{name} must decode to a JSON object"
        raise TypeError(msg)
    return cast(dict[str, object], decoded)


def test_ros2_topic_mapper_roundtrips_publish_topics() -> None:
    mapper = Ros2TopicMapper()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    ros_topic = mapper.ros_topic_for_bus_topic(bus_topic)

    assert ros_topic == "/omnisense/tpercepts/taudio/taudio/tevent_uclassifier_uv1"
    assert mapper.bus_topic_for_ros_topic(ros_topic) == bus_topic


def test_ros2_topic_mapper_preserves_hyphenated_profile_ids() -> None:
    mapper = Ros2TopicMapper(namespace="/site_a/osip")
    bus_topic = profile_safety_case_topic("physical-ai")

    ros_topic = mapper.ros_topic_for_bus_topic(bus_topic)

    assert ros_topic == "/site_a/osip/tsafety/tprofiles/tphysical_dai/tsafe_ustates"
    assert mapper.bus_topic_for_ros_topic(ros_topic) == bus_topic


def test_ros2_topic_mapper_rejects_unmapped_namespace() -> None:
    mapper = Ros2TopicMapper(namespace="/site_a/osip")

    with pytest.raises(ValueError, match="must start with namespace"):
        mapper.bus_topic_for_ros_topic("/site_b/osip/tpercepts/taudio")


def test_ros2_topic_validation_rejects_relative_and_invalid_names() -> None:
    with pytest.raises(ValueError, match="absolute"):
        ensure_ros2_topic_name("omnisense/tpercepts")

    with pytest.raises(ValueError, match="invalid"):
        ensure_ros2_topic_name("/omnisense/physical-ai")


def test_ros2_namespace_validation_rejects_root_only_suffixless_mapping() -> None:
    assert ensure_ros2_namespace("/omnisense") == "/omnisense"
    mapper = Ros2TopicMapper(namespace="/")

    with pytest.raises(ValueError, match="at least one token"):
        mapper.bus_topic_for_ros_topic("/")


def test_ros2_bridge_codec_encodes_percept_with_dds_qos() -> None:
    codec = Ros2BridgeCodec()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    record = codec.encode_publish(bus_topic, _load_fixture("percept_packet.json"))

    assert record.ros_topic == "/omnisense/tpercepts/taudio/taudio/tevent_uclassifier_uv1"
    assert record.bus_topic == bus_topic
    assert record.ros_message_type == ROS2_JSON_MESSAGE_TYPE
    assert record.reliability == "best_effort"
    assert record.durability == "volatile"
    assert record.history == "keep_last"
    assert record.depth == 1
    assert record.lifespan_ms == 50
    assert record.message_type == "percept.packet"
    assert b'"type":"percept.packet"' in record.payload


def test_ros2_bridge_codec_encodes_safety_case_as_reliable_transient_local() -> None:
    codec = Ros2BridgeCodec()
    bus_topic = profile_safety_case_topic("physical-ai")

    record = codec.encode_publish(bus_topic, _load_fixture("profile_safety_case.json"))

    assert record.ros_topic == "/omnisense/tsafety/tprofiles/tphysical_dai/tsafe_ustates"
    assert record.reliability == "reliable"
    assert record.durability == "transient_local"
    assert record.history == "keep_last"
    assert record.depth == 8
    assert record.lifespan_ms is None
    assert record.message_type == "profile.safety_case"


def test_ros2_bridge_codec_decodes_inbound_message_to_bus_record() -> None:
    codec = Ros2BridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )

    inbound = codec.decode_message(outbound.ros_topic, outbound.payload)

    assert inbound.bus_topic == outbound.bus_topic
    assert inbound.message_type == "percept.packet"
    assert isinstance(inbound.payload, PerceptPacket)


def test_ros2_bridge_codec_rejects_topic_message_mismatch() -> None:
    codec = Ros2BridgeCodec()

    with pytest.raises(ValueError, match="expects 'percept.packet'"):
        codec.encode_publish(
            percept_topic("audio", "audio.event_classifier_v1"),
            _load_fixture("profile_safety_case.json"),
        )


def test_ros2_bridge_codec_decodes_prefixed_topics() -> None:
    codec = Ros2BridgeCodec(Ros2TopicMapper(namespace="/site_a/osip"))
    outbound = codec.encode_publish(
        profile_safety_case_topic("physical-ai"),
        _load_fixture("profile_safety_case.json"),
    )

    inbound = codec.decode_message(outbound.ros_topic, outbound.payload)

    assert outbound.ros_topic == "/site_a/osip/tsafety/tprofiles/tphysical_dai/tsafe_ustates"
    assert inbound.bus_topic == profile_safety_case_topic("physical-ai")
    assert isinstance(inbound.payload, ProfileSafetyCase)


@pytest.mark.asyncio
async def test_ros2_outbound_bridge_publishes_through_transport() -> None:
    transport = RecordingRos2Transport()
    bridge = Ros2OutboundBridge(transport, profile_id="physical-ai")
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    result = await bridge.publish_message(bus_topic, _load_fixture("percept_packet.json"))

    assert bridge.metadata.adapter_id == "ros2.outbound_bridge"
    assert bridge.metadata.role == "sink"
    assert bridge.metadata.requires_hardware is False
    assert result.published_count == 1
    assert result.topics == (bus_topic,)
    assert result.target_topics == (
        "/omnisense/tpercepts/taudio/taudio/tevent_uclassifier_uv1",
    )
    assert result.message_types == ("percept.packet",)
    assert len(transport.records) == 1
    assert transport.records[0].reliability == "best_effort"


@pytest.mark.asyncio
async def test_ros2_outbound_bridge_rejects_unsupported_message_type() -> None:
    transport = RecordingRos2Transport()
    bridge = Ros2OutboundBridge(transport, supported_message_types=("profile.safety_case",))

    with pytest.raises(ValueError, match="not supported"):
        await bridge.publish_message(
            percept_topic("audio", "audio.event_classifier_v1"),
            _load_fixture("percept_packet.json"),
        )

    assert transport.records == []


def test_ros2_outbound_bridge_requires_supported_message_types() -> None:
    with pytest.raises(ValueError, match="supported_message_types"):
        Ros2OutboundBridge(RecordingRos2Transport(), supported_message_types=())


@pytest.mark.asyncio
async def test_ros2_inbound_bridge_decodes_and_publishes_to_bus() -> None:
    codec = Ros2BridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    source = QueuedRos2Source(
        [Ros2InboundMessage(ros_topic=outbound.ros_topic, payload=outbound.payload)]
    )
    bridge = Ros2InboundBridge(source, profile_id="physical-ai", codec=codec)
    bus = InMemoryBus()

    async with bus.subscribe("omnisense.>") as subscription:
        result = await bridge.publish_to(bus)
        message = await subscription.receive()

    assert bridge.metadata.adapter_id == "ros2.inbound_bridge"
    assert bridge.metadata.role == "source"
    assert result.published_count == 1
    assert result.topics == (percept_topic("audio", "audio.event_classifier_v1"),)
    assert result.target_topics == (
        "/omnisense/tpercepts/taudio/taudio/tevent_uclassifier_uv1",
    )
    assert result.message_types == ("percept.packet",)
    assert isinstance(message.payload, PerceptPacket)


@pytest.mark.asyncio
async def test_ros2_inbound_bridge_honors_max_messages() -> None:
    codec = Ros2BridgeCodec()
    percept = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    safety = codec.encode_publish(
        profile_safety_case_topic("physical-ai"),
        _load_fixture("profile_safety_case.json"),
    )
    source = QueuedRos2Source(
        [
            Ros2InboundMessage(ros_topic=percept.ros_topic, payload=percept.payload),
            Ros2InboundMessage(ros_topic=safety.ros_topic, payload=safety.payload),
        ]
    )
    bridge = Ros2InboundBridge(source, codec=codec)

    result = await bridge.publish_to(InMemoryBus(), max_messages=1)

    assert result.published_count == 1
    assert result.message_types == ("percept.packet",)
    assert len(source.messages) == 1


@pytest.mark.asyncio
async def test_ros2_inbound_bridge_rejects_unsupported_message_type() -> None:
    codec = Ros2BridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )
    source = QueuedRos2Source(
        [Ros2InboundMessage(ros_topic=outbound.ros_topic, payload=outbound.payload)]
    )
    bridge = Ros2InboundBridge(
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
async def test_ros2_inbound_bridge_rejects_invalid_max_messages() -> None:
    bridge = Ros2InboundBridge(QueuedRos2Source([]))

    with pytest.raises(ValueError, match="max_messages"):
        await bridge.publish_to(InMemoryBus(), max_messages=-1)


def test_ros2_inbound_bridge_requires_supported_message_types() -> None:
    with pytest.raises(ValueError, match="supported_message_types"):
        Ros2InboundBridge(QueuedRos2Source([]), supported_message_types=())
