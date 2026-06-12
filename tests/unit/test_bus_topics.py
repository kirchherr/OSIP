from __future__ import annotations

import pytest
from omnisense_bus import (
    InvalidTopicError,
    action_command_filter,
    action_command_topic,
    context_update_filter,
    context_update_topic,
    ensure_valid_topic,
    event_detected_filter,
    event_detected_topic,
    percept_filter,
    percept_topic,
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
