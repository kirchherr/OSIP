"""Topic conventions for OmniSense event transport."""

from __future__ import annotations

import re
from typing import Final

TOPIC_PREFIX: Final = "omnisense"

_TOPIC_SEGMENT = re.compile(r"^[a-z0-9_-]+$")


class InvalidTopicError(ValueError):
    """Raised when a topic or topic filter is not valid for OmniSense."""


def ensure_valid_topic(topic: str, *, allow_wildcards: bool = False) -> str:
    if not topic or topic.strip() != topic:
        msg = "topic must be non-empty and must not contain surrounding whitespace"
        raise InvalidTopicError(msg)

    segments = topic.split(".")
    if any(segment == "" for segment in segments):
        msg = f"topic '{topic}' must not contain empty segments"
        raise InvalidTopicError(msg)

    for index, segment in enumerate(segments):
        if segment in {"*", ">"}:
            if not allow_wildcards:
                msg = f"topic '{topic}' must not contain wildcards"
                raise InvalidTopicError(msg)
            if segment == ">" and index != len(segments) - 1:
                msg = f"tail wildcard '>' must be the final segment in '{topic}'"
                raise InvalidTopicError(msg)
            continue
        if _TOPIC_SEGMENT.fullmatch(segment) is None:
            msg = f"topic segment '{segment}' in '{topic}' is invalid"
            raise InvalidTopicError(msg)
    return topic


def build_topic(*parts: str, allow_wildcards: bool = False) -> str:
    return ensure_valid_topic(".".join(parts), allow_wildcards=allow_wildcards)


def topic_matches(topic_filter: str, topic: str) -> bool:
    ensure_valid_topic(topic_filter, allow_wildcards=True)
    ensure_valid_topic(topic)

    filter_parts = topic_filter.split(".")
    topic_parts = topic.split(".")

    for index, filter_part in enumerate(filter_parts):
        if filter_part == ">":
            return True
        if index >= len(topic_parts):
            return False
        if filter_part == "*":
            continue
        if filter_part != topic_parts[index]:
            return False
    return len(filter_parts) == len(topic_parts)


def model_capabilities_topic() -> str:
    return build_topic(TOPIC_PREFIX, "models", "capabilities")


def percept_topic(modality: str, source_model: str) -> str:
    return build_topic(TOPIC_PREFIX, "percepts", modality, source_model)


def percept_filter(modality: str | None = None, source_model: str | None = None) -> str:
    if modality is None:
        return build_topic(TOPIC_PREFIX, "percepts", ">", allow_wildcards=True)
    if source_model is None:
        return build_topic(TOPIC_PREFIX, "percepts", modality, ">", allow_wildcards=True)
    return percept_topic(modality, source_model)


def context_update_topic(room: str) -> str:
    return build_topic(TOPIC_PREFIX, "context", "updates", room)


def context_update_filter(room: str | None = None) -> str:
    if room is None:
        return build_topic(TOPIC_PREFIX, "context", "updates", ">", allow_wildcards=True)
    return context_update_topic(room)


def event_detected_topic(label: str) -> str:
    return build_topic(TOPIC_PREFIX, "events", "detected", label)


def event_detected_filter(label: str | None = None) -> str:
    if label is None:
        return build_topic(TOPIC_PREFIX, "events", "detected", ">", allow_wildcards=True)
    return event_detected_topic(label)


def action_contracts_topic() -> str:
    return build_topic(TOPIC_PREFIX, "actions", "contracts")


def action_proposals_topic() -> str:
    return build_topic(TOPIC_PREFIX, "actions", "proposals")


def action_command_topic(target: str) -> str:
    return build_topic(TOPIC_PREFIX, "actions", "commands", target)


def action_command_filter(target: str | None = None) -> str:
    if target is None:
        return build_topic(TOPIC_PREFIX, "actions", "commands", ">", allow_wildcards=True)
    return action_command_topic(target)


def action_result_topic(action_id: str) -> str:
    return build_topic(TOPIC_PREFIX, "actions", "results", action_id)


def action_result_filter(action_id: str | None = None) -> str:
    if action_id is None:
        return build_topic(TOPIC_PREFIX, "actions", "results", ">", allow_wildcards=True)
    return action_result_topic(action_id)


def profile_safety_case_topic(profile_id: str) -> str:
    return build_topic(TOPIC_PREFIX, "safety", "profiles", profile_id, "safe_states")


def profile_safety_case_filter(profile_id: str | None = None) -> str:
    if profile_id is None:
        return build_topic(TOPIC_PREFIX, "safety", "profiles", ">", allow_wildcards=True)
    return profile_safety_case_topic(profile_id)


def adapter_heartbeat_topic(adapter_id: str) -> str:
    return build_topic(TOPIC_PREFIX, "safety", "heartbeats", adapter_id)


def adapter_heartbeat_filter(adapter_id: str | None = None) -> str:
    if adapter_id is None:
        return build_topic(TOPIC_PREFIX, "safety", "heartbeats", ">", allow_wildcards=True)
    return adapter_heartbeat_topic(adapter_id)
