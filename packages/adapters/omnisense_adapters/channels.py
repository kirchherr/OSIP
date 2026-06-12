"""Shared OSIP channel mapping helpers for transport adapters."""

from __future__ import annotations

from typing import Final

from omnisense_bus import (
    action_command_filter,
    action_contracts_topic,
    action_proposals_topic,
    action_result_filter,
    adapter_heartbeat_filter,
    context_update_filter,
    ensure_valid_topic,
    event_detected_filter,
    model_capabilities_topic,
    percept_filter,
    profile_safety_case_filter,
    topic_matches,
)

BUS_TOPIC_PREFIX: Final = "omnisense"

CHANNEL_MESSAGE_TYPES: Final[dict[str, str]] = {
    "modelCapabilities": "model.capability",
    "percepts": "percept.packet",
    "contextUpdates": "context.update",
    "eventsDetected": "event.detected",
    "actionContracts": "action.contract",
    "actionProposals": "action.proposal",
    "actionCommands": "action.command",
    "actionResults": "action.result",
    "profileSafetyCases": "profile.safety_case",
    "adapterHeartbeats": "adapter.heartbeat",
}


def channel_id_for_bus_topic(bus_topic: str) -> str:
    """Map a concrete OSIP bus topic to its AsyncAPI channel id."""

    ensure_valid_topic(bus_topic)
    if bus_topic == model_capabilities_topic():
        return "modelCapabilities"
    if topic_matches(percept_filter(), bus_topic):
        return "percepts"
    if topic_matches(context_update_filter(), bus_topic):
        return "contextUpdates"
    if topic_matches(event_detected_filter(), bus_topic):
        return "eventsDetected"
    if bus_topic == action_contracts_topic():
        return "actionContracts"
    if bus_topic == action_proposals_topic():
        return "actionProposals"
    if topic_matches(action_command_filter(), bus_topic):
        return "actionCommands"
    if topic_matches(action_result_filter(), bus_topic):
        return "actionResults"
    if topic_matches(profile_safety_case_filter(), bus_topic):
        return "profileSafetyCases"
    if topic_matches(adapter_heartbeat_filter(), bus_topic):
        return "adapterHeartbeats"

    msg = f"no OSIP channel id is defined for bus topic '{bus_topic}'"
    raise ValueError(msg)


def ensure_channel_message_type(channel_id: str, message_type: str) -> None:
    expected = CHANNEL_MESSAGE_TYPES[channel_id]
    if message_type != expected:
        msg = f"channel '{channel_id}' expects '{expected}', got '{message_type}'"
        raise ValueError(msg)
