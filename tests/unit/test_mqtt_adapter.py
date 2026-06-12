from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters import MqttBridgeCodec, MqttTopicMapper, channel_id_for_bus_topic
from omnisense_bus import (
    model_capabilities_topic,
    percept_filter,
    percept_topic,
    profile_safety_case_topic,
)
from omnisense_osip import PerceptPacket, ProfileSafetyCase

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


def _load_fixture(name: str) -> dict[str, object]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        msg = f"{name} must decode to a JSON object"
        raise TypeError(msg)
    return cast(dict[str, object], decoded)


def test_mqtt_topic_mapper_roundtrips_publish_topics() -> None:
    mapper = MqttTopicMapper()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    mqtt_topic = mapper.mqtt_topic_for_bus_topic(bus_topic)

    assert mqtt_topic == "omnisense/percepts/audio/audio/event_classifier_v1"
    assert mapper.bus_topic_for_mqtt_topic(mqtt_topic) == bus_topic


def test_mqtt_topic_mapper_maps_subscription_wildcards() -> None:
    mapper = MqttTopicMapper(topic_prefix="site_a/osip")

    assert mapper.mqtt_filter_for_bus_filter(percept_filter("audio")) == (
        "site_a/osip/percepts/audio/#"
    )
    assert mapper.bus_filter_for_mqtt_filter("site_a/osip/safety/heartbeats/+") == (
        "omnisense.safety.heartbeats.*"
    )


def test_mqtt_topic_mapper_rejects_invalid_filters() -> None:
    mapper = MqttTopicMapper()

    with pytest.raises(ValueError, match="must be final"):
        mapper.bus_filter_for_mqtt_filter("omnisense/percepts/#/bad")


def test_mqtt_bridge_codec_encodes_percept_with_mapped_qos() -> None:
    codec = MqttBridgeCodec()
    bus_topic = percept_topic("audio", "audio.event_classifier_v1")

    record = codec.encode_publish(bus_topic, _load_fixture("percept_packet.json"))

    assert record.mqtt_topic == "omnisense/percepts/audio/audio/event_classifier_v1"
    assert record.bus_topic == bus_topic
    assert record.qos == 0
    assert record.retain is False
    assert record.message_expiry_interval_ms == 50
    assert record.message_type == "percept.packet"
    assert b'"type":"percept.packet"' in record.payload


def test_mqtt_bridge_codec_encodes_safety_case_as_reliable_retained_message() -> None:
    codec = MqttBridgeCodec()
    bus_topic = profile_safety_case_topic("physical-ai")

    record = codec.encode_publish(bus_topic, _load_fixture("profile_safety_case.json"))

    assert record.mqtt_topic == "omnisense/safety/profiles/physical-ai/safe_states"
    assert record.qos == 1
    assert record.retain is True
    assert record.message_expiry_interval_ms is None
    assert record.message_type == "profile.safety_case"


def test_mqtt_bridge_codec_decodes_inbound_message_to_bus_record() -> None:
    codec = MqttBridgeCodec()
    outbound = codec.encode_publish(
        percept_topic("audio", "audio.event_classifier_v1"),
        _load_fixture("percept_packet.json"),
    )

    inbound = codec.decode_message(outbound.mqtt_topic, outbound.payload)

    assert inbound.bus_topic == outbound.bus_topic
    assert inbound.message_type == "percept.packet"
    assert isinstance(inbound.payload, PerceptPacket)


def test_mqtt_bridge_codec_rejects_topic_message_mismatch() -> None:
    codec = MqttBridgeCodec()

    with pytest.raises(ValueError, match="expects 'percept.packet'"):
        codec.encode_publish(
            percept_topic("audio", "audio.event_classifier_v1"),
            _load_fixture("profile_safety_case.json"),
        )


def test_channel_id_mapping_rejects_unknown_bus_topic() -> None:
    assert channel_id_for_bus_topic(model_capabilities_topic()) == "modelCapabilities"

    with pytest.raises(ValueError, match="no OSIP channel id"):
        channel_id_for_bus_topic("omnisense.unknown.topic")


def test_mqtt_decoded_record_validates_payload_shape() -> None:
    codec = MqttBridgeCodec()
    record = codec.decode_message(
        "omnisense/safety/profiles/physical-ai/safe_states",
        json.dumps(_load_fixture("profile_safety_case.json")),
    )

    assert isinstance(record.payload, ProfileSafetyCase)
