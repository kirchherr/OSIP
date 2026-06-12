"""MQTT bridge codec and topic mapping for OSIP messages."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol

from omnisense_bus import (
    AsyncMessageBus,
    ensure_valid_topic,
    map_to_mqtt5,
    qos_for_channel,
)
from omnisense_osip import OSIPMessage, from_json, validate_osip_message
from pydantic import BaseModel, ConfigDict, Field, field_validator

from omnisense_adapters.channels import (
    BUS_TOPIC_PREFIX,
    CHANNEL_MESSAGE_TYPES,
    channel_id_for_bus_topic,
    ensure_channel_message_type,
)
from omnisense_adapters.interfaces import AdapterMetadata, AdapterRunResult


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


class MqttPublishTransport(Protocol):
    """Minimal broker client wrapper used by the outbound MQTT bridge."""

    async def publish(self, record: MqttPublishRecord) -> None: ...


class MqttInboundMessage(BaseModel):
    """Broker-independent MQTT message received by an inbound bridge."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    mqtt_topic: str
    payload: bytes
    qos: int = Field(default=0, ge=0, le=2)
    retain: bool = False

    @field_validator("mqtt_topic")
    @classmethod
    def validate_mqtt_topic(cls, value: str) -> str:
        return ensure_mqtt_topic(value)


class MqttMessageSource(Protocol):
    """Minimal MQTT subscriber wrapper used by the inbound bridge."""

    async def receive(self) -> MqttInboundMessage | None: ...


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
        ensure_channel_message_type(channel_id, message.type)
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
        ensure_channel_message_type(channel_id, message.type)
        return MqttDecodedRecord(
            mqtt_topic=mqtt_topic,
            bus_topic=bus_topic,
            payload=message,
            message_type=message.type,
        )


class MqttOutboundBridge:
    """Adapter-facing MQTT publisher built on a broker-independent transport."""

    def __init__(
        self,
        transport: MqttPublishTransport,
        *,
        adapter_id: str = "mqtt.outbound_bridge",
        profile_id: str | None = None,
        codec: MqttBridgeCodec | None = None,
        supported_message_types: Iterable[str] = CHANNEL_MESSAGE_TYPES.values(),
    ) -> None:
        supported = tuple(dict.fromkeys(supported_message_types))
        if not supported:
            msg = "supported_message_types must not be empty"
            raise ValueError(msg)
        self._transport = transport
        self._codec = codec or MqttBridgeCodec()
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="sink",
            supported_message_types=supported,
            profile_id=profile_id,
            requires_hardware=False,
            description="MQTT outbound bridge using broker-independent publish records.",
        )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    @property
    def codec(self) -> MqttBridgeCodec:
        return self._codec

    async def publish_message(
        self,
        bus_topic: str,
        payload: OSIPMessage | Mapping[str, Any],
    ) -> AdapterRunResult:
        record = self._codec.encode_publish(bus_topic, payload)
        if record.message_type not in self._metadata.supported_message_types:
            msg = (
                f"message type '{record.message_type}' is not supported by adapter "
                f"'{self._metadata.adapter_id}'"
            )
            raise ValueError(msg)
        await self._transport.publish(record)
        return AdapterRunResult(
            adapter_id=self._metadata.adapter_id,
            published_count=1,
            topics=(record.bus_topic,),
            target_topics=(record.mqtt_topic,),
            message_types=(record.message_type,),
        )


class MqttInboundBridge:
    """Adapter-facing MQTT subscriber that publishes decoded OSIP messages to a bus."""

    def __init__(
        self,
        source: MqttMessageSource,
        *,
        adapter_id: str = "mqtt.inbound_bridge",
        profile_id: str | None = None,
        codec: MqttBridgeCodec | None = None,
        supported_message_types: Iterable[str] = CHANNEL_MESSAGE_TYPES.values(),
    ) -> None:
        supported = tuple(dict.fromkeys(supported_message_types))
        if not supported:
            msg = "supported_message_types must not be empty"
            raise ValueError(msg)
        self._source = source
        self._codec = codec or MqttBridgeCodec()
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="source",
            supported_message_types=supported,
            profile_id=profile_id,
            requires_hardware=False,
            description="MQTT inbound bridge using broker-independent received messages.",
        )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    @property
    def codec(self) -> MqttBridgeCodec:
        return self._codec

    async def publish_to(
        self,
        bus: AsyncMessageBus,
        *,
        max_messages: int | None = None,
    ) -> AdapterRunResult:
        if max_messages is not None and max_messages < 0:
            msg = "max_messages must be greater than or equal to zero"
            raise ValueError(msg)

        bus_topics: list[str] = []
        mqtt_topics: list[str] = []
        message_types: list[str] = []

        while max_messages is None or len(bus_topics) < max_messages:
            message = await self._source.receive()
            if message is None:
                break
            decoded = self._codec.decode_message(message.mqtt_topic, message.payload)
            if decoded.message_type not in self._metadata.supported_message_types:
                msg = (
                    f"message type '{decoded.message_type}' is not supported by adapter "
                    f"'{self._metadata.adapter_id}'"
                )
                raise ValueError(msg)
            await bus.publish(decoded.bus_topic, decoded.payload)
            bus_topics.append(decoded.bus_topic)
            mqtt_topics.append(decoded.mqtt_topic)
            message_types.append(decoded.message_type)

        return AdapterRunResult(
            adapter_id=self._metadata.adapter_id,
            published_count=len(bus_topics),
            topics=tuple(bus_topics),
            target_topics=tuple(mqtt_topics),
            message_types=tuple(message_types),
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
