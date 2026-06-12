"""AsyncAPI export for OmniSense bus topics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from omnisense_bus.qos import qos_for_channel
from omnisense_bus.topics import (
    action_contracts_topic,
    action_proposals_topic,
    model_capabilities_topic,
)

SCHEMA_BASE = "../schemas"


def build_asyncapi_spec() -> dict[str, Any]:
    """Build the public AsyncAPI document for OSIP event channels."""

    channels = {
        "modelCapabilities": _channel(
            address=model_capabilities_topic(),
            message_ref="modelCapability",
            description="Registered sensory model capability descriptors.",
        ),
        "percepts": _channel(
            address="omnisense.percepts.{modality}.{source_model}",
            message_ref="perceptPacket",
            description=(
                "Percept packets emitted by sensory models. Source model identifiers "
                "that contain dots expand into multiple topic segments on concrete transports."
            ),
            parameters={
                "modality": "Percept modality such as audio, rgb, radar, or chemical.",
                "source_model": "Registered source model id.",
            },
        ),
        "contextUpdates": _channel(
            address="omnisense.context.updates.{room}",
            message_ref="contextUpdate",
            description="Fused context updates by room.",
            parameters={"room": "Room identifier."},
        ),
        "eventsDetected": _channel(
            address="omnisense.events.detected.{event_label}",
            message_ref="eventDetected",
            description="Detected event stream for low-latency subscribers.",
            parameters={"event_label": "Detected event label."},
        ),
        "actionContracts": _channel(
            address=action_contracts_topic(),
            message_ref="actionContract",
            description="Available bounded Action Contracts.",
        ),
        "actionProposals": _channel(
            address=action_proposals_topic(),
            message_ref="actionProposal",
            description="Bounded action proposals emitted by the Decision Runtime.",
        ),
        "actionCommands": _channel(
            address="omnisense.actions.commands.{target}",
            message_ref="actionCommand",
            description="Approved Action Commands for adapter-facing targets.",
            parameters={"target": "Action target such as hvac.room or speaker.room."},
        ),
        "actionResults": _channel(
            address="omnisense.actions.results.{action_id}",
            message_ref="actionResult",
            description="Action execution results by action id.",
            parameters={"action_id": "Action id from the originating contract."},
        ),
        "profileSafetyCases": _channel(
            address="omnisense.safety.profiles.{profile_id}.safe_states",
            message_ref="profileSafetyCase",
            description="Profile-level default safe-state and watchdog requirements.",
            parameters={"profile_id": "Application Profile id such as rooms or physical-ai."},
        ),
        "adapterHeartbeats": _channel(
            address="omnisense.safety.heartbeats.{adapter_id}",
            message_ref="adapterHeartbeat",
            description="Adapter heartbeat stream used by watchdogs and safe-state monitors.",
            parameters={"adapter_id": "Adapter id such as room_hvac_bridge or robot_arm_bridge."},
        ),
    }
    for channel_id, channel in channels.items():
        channel["x-osip-qos"] = qos_for_channel(channel_id).as_asyncapi_extension()

    return {
        "asyncapi": "3.1.0",
        "id": "https://schemas.omnisense.dev/asyncapi/osip-0.1.0",
        "info": {
            "title": "OmniSense Runtime OSIP Event API",
            "version": "0.1.0",
            "description": (
                "Transport-agnostic event channels for OSIP v0.1. Concrete adapters "
                "such as in-memory bus, NATS, MQTT, or ROS 2/DDS map these channels "
                "to their native topic or subject syntax."
            ),
        },
        "defaultContentType": "application/json",
        "channels": channels,
        "operations": _operations(channels),
        "components": {
            "messages": {
                "modelCapability": _message(
                    "model.capability",
                    "model_capability.schema.json",
                ),
                "perceptPacket": _message(
                    "percept.packet",
                    "percept_packet.schema.json",
                ),
                "contextUpdate": _message(
                    "context.update",
                    "context_update.schema.json",
                ),
                "eventDetected": _message(
                    "event.detected",
                    "event_detected.schema.json",
                ),
                "actionContract": _message(
                    "action.contract",
                    "action_contract.schema.json",
                ),
                "actionProposal": _message(
                    "action.proposal",
                    "action_proposal.schema.json",
                ),
                "actionCommand": _message(
                    "action.command",
                    "action_command.schema.json",
                ),
                "actionResult": _message(
                    "action.result",
                    "action_result.schema.json",
                ),
                "profileSafetyCase": _message(
                    "profile.safety_case",
                    "profile_safety_case.schema.json",
                ),
                "adapterHeartbeat": _message(
                    "adapter.heartbeat",
                    "adapter_heartbeat.schema.json",
                ),
            }
        },
        "tags": [
            {"name": "osip"},
            {"name": "simulation-first"},
            {"name": "application-profiles"},
        ],
    }


def export_asyncapi(path: Path) -> Path:
    """Write the AsyncAPI document to ``path``."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_asyncapi_spec(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _channel(
    *,
    address: str,
    message_ref: str,
    description: str,
    parameters: dict[str, str] | None = None,
) -> dict[str, Any]:
    channel: dict[str, Any] = {
        "address": address,
        "description": description,
        "messages": {
            message_ref: {"$ref": f"#/components/messages/{message_ref}"},
        },
    }
    if parameters:
        channel["parameters"] = {
            name: {"description": detail}
            for name, detail in sorted(parameters.items())
        }
    return channel


def _message(name: str, schema_file: str) -> dict[str, Any]:
    return {
        "name": name,
        "title": name,
        "contentType": "application/json",
        "payload": {
            "$ref": f"{SCHEMA_BASE}/{schema_file}",
        },
    }


def _operations(channels: dict[str, Any]) -> dict[str, Any]:
    operations: dict[str, Any] = {}
    for channel_id, channel in sorted(channels.items()):
        message_id = next(iter(channel["messages"]))
        operations[f"publish{channel_id[0].upper()}{channel_id[1:]}"] = {
            "action": "send",
            "channel": {"$ref": f"#/channels/{channel_id}"},
            "messages": [{"$ref": f"#/channels/{channel_id}/messages/{message_id}"}],
        }
        operations[f"subscribe{channel_id[0].upper()}{channel_id[1:]}"] = {
            "action": "receive",
            "channel": {"$ref": f"#/channels/{channel_id}"},
            "messages": [{"$ref": f"#/channels/{channel_id}/messages/{message_id}"}],
        }
    return operations
