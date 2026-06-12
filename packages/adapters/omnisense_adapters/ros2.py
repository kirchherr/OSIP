"""ROS 2 / DDS bridge codec and topic mapping for OSIP messages."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any, Final, Literal, Protocol

from omnisense_bus import AsyncMessageBus, ensure_valid_topic, map_to_ros2_dds, qos_for_channel
from omnisense_osip import OSIPMessage, from_json, validate_osip_message
from pydantic import BaseModel, ConfigDict, Field, field_validator

from omnisense_adapters.channels import (
    BUS_TOPIC_PREFIX,
    CHANNEL_MESSAGE_TYPES,
    channel_id_for_bus_topic,
    ensure_channel_message_type,
)
from omnisense_adapters.interfaces import AdapterMetadata, AdapterRunResult

ROS2_JSON_MESSAGE_TYPE: Final = "std_msgs/msg/String"

type Ros2Reliability = Literal["best_effort", "reliable"]
type Ros2Durability = Literal["volatile", "transient_local"]
type Ros2History = Literal["keep_last", "keep_all"]

_ROS2_TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")


class Ros2TopicMapper(BaseModel):
    """Reversible mapping between OSIP bus topics and ROS 2 topic names."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    namespace: str = Field(default="/omnisense", min_length=1)

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, value: str) -> str:
        return ensure_ros2_namespace(value)

    def ros_topic_for_bus_topic(self, bus_topic: str) -> str:
        suffix = _bus_suffix(bus_topic)
        tokens = tuple(_encode_bus_segment(segment) for segment in suffix)
        return ensure_ros2_topic_name("/".join(("", *self._namespace_tokens(), *tokens)))

    def bus_topic_for_ros_topic(self, ros_topic: str) -> str:
        ensure_ros2_topic_name(ros_topic)
        namespace = self._namespace_tokens()
        tokens = tuple(ros_topic.strip("/").split("/"))
        if tokens[: len(namespace)] != namespace:
            msg = f"ROS 2 topic '{ros_topic}' must start with namespace '{self.namespace}'"
            raise ValueError(msg)
        suffix = tokens[len(namespace) :]
        if not suffix:
            msg = f"ROS 2 topic '{ros_topic}' must include an OSIP topic suffix"
            raise ValueError(msg)
        return ensure_valid_topic(
            ".".join((BUS_TOPIC_PREFIX, *(_decode_ros2_segment(token) for token in suffix)))
        )

    def _namespace_tokens(self) -> tuple[str, ...]:
        if self.namespace == "/":
            return ()
        return tuple(self.namespace.strip("/").split("/"))


class Ros2PublishRecord(BaseModel):
    """Middleware-independent ROS 2 publish request derived from an OSIP message."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ros_topic: str
    bus_topic: str
    payload: bytes
    ros_message_type: Literal["std_msgs/msg/String"] = ROS2_JSON_MESSAGE_TYPE
    reliability: Ros2Reliability
    durability: Ros2Durability
    history: Ros2History
    depth: int = Field(gt=0)
    deadline_ms: int | None = Field(default=None, gt=0)
    lifespan_ms: int | None = Field(default=None, gt=0)
    priority: str
    message_type: str

    @field_validator("ros_topic")
    @classmethod
    def validate_ros_topic(cls, value: str) -> str:
        return ensure_ros2_topic_name(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class Ros2PublishTransport(Protocol):
    """Minimal ROS 2 publisher wrapper used by the outbound bridge."""

    async def publish(self, record: Ros2PublishRecord) -> None: ...


class Ros2InboundMessage(BaseModel):
    """Middleware-independent ROS 2 message received by an inbound bridge."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ros_topic: str
    payload: bytes
    ros_message_type: Literal["std_msgs/msg/String"] = ROS2_JSON_MESSAGE_TYPE

    @field_validator("ros_topic")
    @classmethod
    def validate_ros_topic(cls, value: str) -> str:
        return ensure_ros2_topic_name(value)


class Ros2MessageSource(Protocol):
    """Minimal ROS 2 subscriber wrapper used by the inbound bridge."""

    async def receive(self) -> Ros2InboundMessage | None: ...


class Ros2DecodedRecord(BaseModel):
    """Decoded ROS 2 message ready to be published on an OSIP bus."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ros_topic: str
    bus_topic: str
    payload: OSIPMessage
    message_type: str

    @field_validator("ros_topic")
    @classmethod
    def validate_ros_topic(cls, value: str) -> str:
        return ensure_ros2_topic_name(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class Ros2BridgeCodec:
    """Encode and decode OSIP messages for ROS 2 / DDS without importing ROS."""

    def __init__(self, mapper: Ros2TopicMapper | None = None) -> None:
        self._mapper = mapper or Ros2TopicMapper()

    @property
    def mapper(self) -> Ros2TopicMapper:
        return self._mapper

    def encode_publish(
        self,
        bus_topic: str,
        payload: OSIPMessage | Mapping[str, Any],
    ) -> Ros2PublishRecord:
        message = _ensure_osip_message(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        ensure_channel_message_type(channel_id, message.type)
        qos = map_to_ros2_dds(qos_for_channel(channel_id))
        return Ros2PublishRecord(
            ros_topic=self._mapper.ros_topic_for_bus_topic(bus_topic),
            bus_topic=bus_topic,
            payload=message.model_dump_json(exclude_none=True).encode("utf-8"),
            reliability=qos.reliability,
            durability=qos.durability,
            history=qos.history,
            depth=qos.depth,
            deadline_ms=qos.deadline_ms,
            lifespan_ms=qos.lifespan_ms,
            priority=qos.priority,
            message_type=message.type,
        )

    def decode_message(
        self,
        ros_topic: str,
        payload: str | bytes | bytearray,
    ) -> Ros2DecodedRecord:
        bus_topic = self._mapper.bus_topic_for_ros_topic(ros_topic)
        message = from_json(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        ensure_channel_message_type(channel_id, message.type)
        return Ros2DecodedRecord(
            ros_topic=ros_topic,
            bus_topic=bus_topic,
            payload=message,
            message_type=message.type,
        )


class Ros2OutboundBridge:
    """Adapter-facing ROS 2 publisher built on a middleware-independent transport."""

    def __init__(
        self,
        transport: Ros2PublishTransport,
        *,
        adapter_id: str = "ros2.outbound_bridge",
        profile_id: str | None = None,
        codec: Ros2BridgeCodec | None = None,
        supported_message_types: Iterable[str] = CHANNEL_MESSAGE_TYPES.values(),
    ) -> None:
        supported = tuple(dict.fromkeys(supported_message_types))
        if not supported:
            msg = "supported_message_types must not be empty"
            raise ValueError(msg)
        self._transport = transport
        self._codec = codec or Ros2BridgeCodec()
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="sink",
            supported_message_types=supported,
            profile_id=profile_id,
            requires_hardware=False,
            description="ROS 2 outbound bridge using middleware-independent publish records.",
        )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    @property
    def codec(self) -> Ros2BridgeCodec:
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
            target_topics=(record.ros_topic,),
            message_types=(record.message_type,),
        )


class Ros2InboundBridge:
    """Adapter-facing ROS 2 subscriber that publishes decoded OSIP messages to a bus."""

    def __init__(
        self,
        source: Ros2MessageSource,
        *,
        adapter_id: str = "ros2.inbound_bridge",
        profile_id: str | None = None,
        codec: Ros2BridgeCodec | None = None,
        supported_message_types: Iterable[str] = CHANNEL_MESSAGE_TYPES.values(),
    ) -> None:
        supported = tuple(dict.fromkeys(supported_message_types))
        if not supported:
            msg = "supported_message_types must not be empty"
            raise ValueError(msg)
        self._source = source
        self._codec = codec or Ros2BridgeCodec()
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="source",
            supported_message_types=supported,
            profile_id=profile_id,
            requires_hardware=False,
            description="ROS 2 inbound bridge using middleware-independent received messages.",
        )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    @property
    def codec(self) -> Ros2BridgeCodec:
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
        ros_topics: list[str] = []
        message_types: list[str] = []

        while max_messages is None or len(bus_topics) < max_messages:
            message = await self._source.receive()
            if message is None:
                break
            decoded = self._codec.decode_message(message.ros_topic, message.payload)
            if decoded.message_type not in self._metadata.supported_message_types:
                msg = (
                    f"message type '{decoded.message_type}' is not supported by adapter "
                    f"'{self._metadata.adapter_id}'"
                )
                raise ValueError(msg)
            await bus.publish(decoded.bus_topic, decoded.payload)
            bus_topics.append(decoded.bus_topic)
            ros_topics.append(decoded.ros_topic)
            message_types.append(decoded.message_type)

        return AdapterRunResult(
            adapter_id=self._metadata.adapter_id,
            published_count=len(bus_topics),
            topics=tuple(bus_topics),
            target_topics=tuple(ros_topics),
            message_types=tuple(message_types),
        )


def ensure_ros2_topic_name(topic: str) -> str:
    """Validate the conservative ROS 2 topic subset used by OSIP adapters."""

    if not topic or topic.strip() != topic:
        msg = "ROS 2 topic must be non-empty and must not contain surrounding whitespace"
        raise ValueError(msg)
    if not topic.startswith("/"):
        msg = f"ROS 2 topic '{topic}' must be absolute"
        raise ValueError(msg)
    if topic != "/" and topic.endswith("/"):
        msg = f"ROS 2 topic '{topic}' must not end with '/'"
        raise ValueError(msg)
    tokens = tuple(token for token in topic.split("/") if token)
    if not tokens:
        msg = "ROS 2 topic must include at least one token"
        raise ValueError(msg)
    if "//" in topic:
        msg = f"ROS 2 topic '{topic}' must not contain empty tokens"
        raise ValueError(msg)
    invalid = next((token for token in tokens if _ROS2_TOKEN.fullmatch(token) is None), None)
    if invalid is not None:
        msg = f"ROS 2 topic token '{invalid}' in '{topic}' is invalid"
        raise ValueError(msg)
    return topic


def ensure_ros2_namespace(namespace: str) -> str:
    """Validate a namespace prefix for generated ROS 2 topics."""

    if namespace == "/":
        return namespace
    ensure_ros2_topic_name(namespace)
    if namespace != "/" and namespace.endswith("/"):
        msg = f"ROS 2 namespace '{namespace}' must not end with '/'"
        raise ValueError(msg)
    return namespace


def _bus_suffix(bus_topic: str) -> tuple[str, ...]:
    ensure_valid_topic(bus_topic)
    parts = tuple(bus_topic.split("."))
    if parts[0] != BUS_TOPIC_PREFIX:
        msg = f"OSIP bus topic '{bus_topic}' must start with '{BUS_TOPIC_PREFIX}'"
        raise ValueError(msg)
    suffix = parts[1:]
    if not suffix:
        msg = f"OSIP bus topic '{bus_topic}' must include a suffix"
        raise ValueError(msg)
    return suffix


def _encode_bus_segment(segment: str) -> str:
    encoded = segment.replace("_", "_u").replace("-", "_d")
    return f"t{encoded}"


def _decode_ros2_segment(token: str) -> str:
    if not token.startswith("t"):
        msg = f"ROS 2 OSIP token '{token}' must start with 't'"
        raise ValueError(msg)
    source = token[1:]
    decoded: list[str] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char != "_":
            decoded.append(char)
            index += 1
            continue
        if index + 1 >= len(source):
            msg = f"ROS 2 OSIP token '{token}' has an incomplete escape"
            raise ValueError(msg)
        escape = source[index + 1]
        if escape == "u":
            decoded.append("_")
        elif escape == "d":
            decoded.append("-")
        else:
            msg = f"ROS 2 OSIP token '{token}' has unknown escape '_{escape}'"
            raise ValueError(msg)
        index += 2

    if not decoded:
        msg = f"ROS 2 OSIP token '{token}' decodes to an empty bus segment"
        raise ValueError(msg)
    return "".join(decoded)


def _ensure_osip_message(payload: OSIPMessage | Mapping[str, Any]) -> OSIPMessage:
    if isinstance(payload, Mapping):
        return validate_osip_message(payload)
    return payload
