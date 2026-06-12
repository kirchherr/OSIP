from __future__ import annotations

import pytest
from omnisense_bus import (
    InvalidTopicError,
    action_command_filter,
    action_command_topic,
    adapter_heartbeat_filter,
    adapter_heartbeat_topic,
    context_update_filter,
    context_update_topic,
    ensure_valid_topic,
    event_detected_filter,
    event_detected_topic,
    percept_filter,
    percept_topic,
    profile_safety_case_filter,
    profile_safety_case_topic,
    qos_for_channel,
    topic_matches,
)


def test_topic_builders_create_stable_subjects() -> None:
    assert percept_topic("audio", "audio.event_classifier_v1") == (
        "omnisense.percepts.audio.audio.event_classifier_v1"
    )
    assert percept_filter("audio") == "omnisense.percepts.audio.>"
    assert context_update_topic("living_room") == "omnisense.context.updates.living_room"
    assert context_update_filter() == "omnisense.context.updates.>"
    assert event_detected_topic("event.fall_candidate") == (
        "omnisense.events.detected.event.fall_candidate"
    )
    assert event_detected_filter() == "omnisense.events.detected.>"
    assert action_command_topic("room.speaker") == "omnisense.actions.commands.room.speaker"
    assert action_command_filter() == "omnisense.actions.commands.>"
    assert profile_safety_case_topic("physical-ai") == (
        "omnisense.safety.profiles.physical-ai.safe_states"
    )
    assert profile_safety_case_filter() == "omnisense.safety.profiles.>"
    assert adapter_heartbeat_topic("robot_arm_bridge") == (
        "omnisense.safety.heartbeats.robot_arm_bridge"
    )
    assert adapter_heartbeat_filter() == "omnisense.safety.heartbeats.>"


def test_topic_matching_supports_single_and_tail_wildcards() -> None:
    assert topic_matches("omnisense.percepts.audio.>", percept_topic("audio", "model.v1"))
    assert topic_matches("omnisense.percepts.*.model.v1", percept_topic("audio", "model.v1"))
    assert not topic_matches("omnisense.percepts.rgb.>", percept_topic("audio", "model.v1"))


@pytest.mark.parametrize(
    "topic",
    [
        "",
        " omnisense.percepts",
        "omnisense..percepts",
        "omnisense.percepts.audio.*",
        "omnisense.percepts.audio.BadModel",
        "omnisense.percepts.audio.model/v1",
    ],
)
def test_invalid_publish_topics_are_rejected(topic: str) -> None:
    with pytest.raises(InvalidTopicError):
        ensure_valid_topic(topic)


def test_tail_wildcard_must_be_final() -> None:
    with pytest.raises(InvalidTopicError, match="final segment"):
        ensure_valid_topic("omnisense.>.percepts", allow_wildcards=True)


def test_qos_profiles_capture_adapter_delivery_intent() -> None:
    percept_qos = qos_for_channel("percepts")
    command_qos = qos_for_channel("actionCommands")
    heartbeat_qos = qos_for_channel("adapterHeartbeats")

    assert percept_qos.delivery == "best_effort"
    assert percept_qos.max_latency_ms == 10
    assert command_qos.delivery == "reliable"
    assert command_qos.priority == "critical"
    assert heartbeat_qos.deadline_ms == 20


def test_unknown_qos_channel_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown OSIP channel"):
        qos_for_channel("unknown")
