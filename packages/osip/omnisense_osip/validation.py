"""Runtime validation helpers for OSIP payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from pydantic import BaseModel

from omnisense_osip.schemas import (
    ActionCommand,
    ActionContract,
    ActionProposal,
    ActionResult,
    ContextUpdate,
    EventDetected,
    ModelCapabilityDescriptor,
    PerceptPacket,
)

type OSIPMessage = (
    ModelCapabilityDescriptor
    | PerceptPacket
    | ContextUpdate
    | EventDetected
    | ActionContract
    | ActionProposal
    | ActionCommand
    | ActionResult
)

MESSAGE_MODELS: dict[str, type[BaseModel]] = {
    "model.capability": ModelCapabilityDescriptor,
    "percept.packet": PerceptPacket,
    "context.update": ContextUpdate,
    "event.detected": EventDetected,
    "action.contract": ActionContract,
    "action.proposal": ActionProposal,
    "action.command": ActionCommand,
    "action.result": ActionResult,
}


def validate_osip_message(data: Mapping[str, Any]) -> OSIPMessage:
    message_type = data.get("type")
    if not isinstance(message_type, str):
        msg = "OSIP message requires a string 'type' field"
        raise ValueError(msg)

    model = MESSAGE_MODELS.get(message_type)
    if model is None:
        supported = ", ".join(sorted(MESSAGE_MODELS))
        msg = f"Unsupported OSIP message type '{message_type}'. Supported: {supported}"
        raise ValueError(msg)

    return cast(OSIPMessage, model.model_validate(data))


def parse_osip_json(payload: str | bytes | bytearray) -> OSIPMessage:
    data = json.loads(payload)
    if not isinstance(data, dict):
        msg = "OSIP JSON payload must decode to an object"
        raise ValueError(msg)
    return validate_osip_message(data)
