"""MQTT bridge codec and topic mapping for OSIP messages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from omnisense_bus import (
    action_command_filter,
    action_contracts_topic,
    action_proposals_topic,
    action_result_filter,
    adapter_heartbeat_filter,
    context_update_filter,
    ensure_valid_topic,
    event_detected_filter,
    map_to_mqtt5,
    model_capabilities_topic,
    percept_filter,
    profile_safety_case_filter,
    qos_for_channel,
    topic_matches,
)
from omnisense_osip import OSIPMessage, from_json, validate_osip_message
from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class MqttTopicMapper(BaseModel):
    """Reversible mapping between OSIP bus topics and MQTT topics."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    topic_prefix: str = Field(default=BUS_TOPIC_PREFIX, min_length=1)

    @field_validator("topic_prefix")
    @classmethod
    def validate_topic_prefix(cls, value: str) -> str:
        return ensure_mqtt_topic(value)

    def mqtt_topic_for_bus_topic(self, bus_topic: str) -> str:
        suffix = _bus_suffix(bus_topic, allow_wildcards=False)
        return ensure_mqtt_topic("/".join((*self._prefix_levels(), *suffix)))

    def mqtt_filter_for_bus_filter(self, bus_filter: str) -> str:
        suffix = _bus_suffix(bus_filter, allow_wildcards=True)
        levels = tuple(_bus_wildcard_to_mqtt(part) for part in suffix)
        return ensure_mqtt_topic("/".join((*self._prefix_levels(), *levels)), allow_wildcards=True)

    def bus_topic_for_mqtt_topic(self, mqtt_topic: str) -> str:
        suffix = self._mqtt_suffix(mqtt_topic, allow_wildcards=False)
        return ensure_valid_topic(".".join((BUS_TOPIC_PREFIX, *suffix)))

    def bus_filter_for_mqtt_filter(self, mqtt_filter: str) -> str:
        suffix = self._mqtt_suffix(mqtt_filter, allow_wildcards=True)
        parts = tuple(_mqtt_wildcard_to_bus(part) for part in suffix)
        return ensure_valid_topic(".".join((BUS_TOPIC_PREFIX, *parts)), allow_wildcards=True)

    def _prefix_levels(self) -> tuple[str, ...]:
        return tuple(self.topic_prefix.split("/"))

    def _mqtt_suffix(self, mqtt_topic: str, *, allow_wildcards: bool) -> tuple[str, ...]:
        ensure_mqtt_topic(mqtt_topic, allow_wildcards=allow_wildcards)
        prefix = self._prefix_levels()
        levels = tuple(mqtt_topic.split("/"))
        if levels[: len(prefix)] != prefix:
            msg = f"MQTT topic '{mqtt_topic}' must start with '{self.topic_prefix}'"
            raise ValueError(msg)
        suffix = levels[len(prefix) :]
        if not suffix:
            msg = f"MQTT topic '{mqtt_topic}' must include an OSIP topic suffix"
            raise ValueError(msg)
        return suffix


class MqttPublishRecord(BaseModel):
    """Broker-independent MQTT publish request derived from an OSIP bus message."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    mqtt_topic: str
    bus_topic: str
    payload: bytes
    qos: int = Field(ge=0, le=1)
    retain: bool
    message_expiry_interval_ms: int | None = Field(default=None, gt=0)
    message_type: str

    @field_validator("mqtt_topic")
    @classmethod
    def validate_mqtt_topic(cls, value: str) -> str:
        return ensure_mqtt_topic(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class MqttDecodedRecord(BaseModel):
    """Decoded MQTT message ready to be published on an OSIP bus."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    mqtt_topic: str
    bus_topic: str
    payload: OSIPMessage
    message_type: str

    @field_validator("mqtt_topic")
    @classmethod
    def validate_mqtt_topic(cls, value: str) -> str:
        return ensure_mqtt_topic(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class MqttBridgeCodec:
    """Encode and decode OSIP messages for an MQTT 5 bridge without opening a socket."""

    def __init__(self, mapper: MqttTopicMapper | None = None) -> None:
        self._mapper = mapper or MqttTopicMapper()

    @property
    def mapper(self) -> MqttTopicMapper:
        return self._mapper

    def encode_publish(
        self,
        bus_topic: str,
        payload: OSIPMessage | Mapping[str, Any],
    ) -> MqttPublishRecord:
        message = _ensure_osip_message(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        _ensure_channel_message_type(channel_id, message.type)
        qos = map_to_mqtt5(qos_for_channel(channel_id))
        return MqttPublishRecord(
            mqtt_topic=self._mapper.mqtt_topic_for_bus_topic(bus_topic),
            bus_topic=bus_topic,
            payload=message.model_dump_json(exclude_none=True).encode("utf-8"),
            qos=qos.qos,
            retain=qos.retain,
            message_expiry_interval_ms=qos.message_expiry_interval_ms,
            message_type=message.type,
        )

    def decode_message(
        self,
        mqtt_topic: str,
        payload: str | bytes | bytearray,
    ) -> MqttDecodedRecord:
        bus_topic = self._mapper.bus_topic_for_mqtt_topic(mqtt_topic)
        message = from_json(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        _ensure_channel_message_type(channel_id, message.type)
        return MqttDecodedRecord(
            mqtt_topic=mqtt_topic,
            bus_topic=bus_topic,
            payload=message,
            message_type=message.type,
        )


def ensure_mqtt_topic(topic: str, *, allow_wildcards: bool = False) -> str:
    """Validate the conservative MQTT topic subset used by OSIP adapters."""

    if not topic or topic.strip() != topic:
        msg = "MQTT topic must be non-empty and must not contain surrounding whitespace"
        raise ValueError(msg)
    if "\x00" in topic:
        msg = "MQTT topic must not contain null bytes"
        raise ValueError(msg)

    levels = topic.split("/")
    if any(level == "" for level in levels):
        msg = f"MQTT topic '{topic}' must not contain empty levels"
        raise ValueError(msg)

    for index, level in enumerate(levels):
        if level in {"+", "#"}:
            if not allow_wildcards:
                msg = f"MQTT publish topic '{topic}' must not contain wildcards"
                raise ValueError(msg)
            if level == "#" and index != len(levels) - 1:
                msg = f"MQTT multi-level wildcard '#' must be final in '{topic}'"
                raise ValueError(msg)
            continue
        if "+" in level or "#" in level:
            msg = f"MQTT wildcard must occupy a whole level in '{topic}'"
            raise ValueError(msg)

    return topic


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


def _bus_suffix(bus_topic: str, *, allow_wildcards: bool) -> tuple[str, ...]:
    ensure_valid_topic(bus_topic, allow_wildcards=allow_wildcards)
    parts = tuple(bus_topic.split("."))
    if parts[0] != BUS_TOPIC_PREFIX:
        msg = f"OSIP bus topic '{bus_topic}' must start with '{BUS_TOPIC_PREFIX}'"
        raise ValueError(msg)
    suffix = parts[1:]
    if not suffix:
        msg = f"OSIP bus topic '{bus_topic}' must include a suffix"
        raise ValueError(msg)
    return suffix


def _bus_wildcard_to_mqtt(part: str) -> str:
    if part == "*":
        return "+"
    if part == ">":
        return "#"
    return part


def _mqtt_wildcard_to_bus(part: str) -> str:
    if part == "+":
        return "*"
    if part == "#":
        return ">"
    return part


def _ensure_osip_message(payload: OSIPMessage | Mapping[str, Any]) -> OSIPMessage:
    if isinstance(payload, Mapping):
        return validate_osip_message(payload)
    return payload


def _ensure_channel_message_type(channel_id: str, message_type: str) -> None:
    expected = CHANNEL_MESSAGE_TYPES[channel_id]
    if message_type != expected:
        msg = f"channel '{channel_id}' expects '{expected}', got '{message_type}'"
        raise ValueError(msg)
