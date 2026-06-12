from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from omnisense_adapters import NatsBridgeCodec, NatsSubjectMapper, ensure_nats_subject
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
