"""NATS bridge codec and subject mapping for OSIP messages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from omnisense_bus import ensure_valid_topic, map_to_nats, qos_for_channel
from omnisense_osip import OSIPMessage, from_json, validate_osip_message
from pydantic import BaseModel, ConfigDict, Field, field_validator

from omnisense_adapters.channels import (
    BUS_TOPIC_PREFIX,
    channel_id_for_bus_topic,
    ensure_channel_message_type,
)


class NatsSubjectMapper(BaseModel):
    """Reversible mapping between OSIP bus topics and NATS subjects."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    subject_prefix: str = Field(default=BUS_TOPIC_PREFIX, min_length=1)

    @field_validator("subject_prefix")
    @classmethod
    def validate_subject_prefix(cls, value: str) -> str:
        return ensure_nats_subject(value)

    def nats_subject_for_bus_topic(self, bus_topic: str) -> str:
        suffix = _bus_suffix(bus_topic, allow_wildcards=False)
        return ensure_nats_subject(".".join((*self._prefix_tokens(), *suffix)))

    def nats_filter_for_bus_filter(self, bus_filter: str) -> str:
        suffix = _bus_suffix(bus_filter, allow_wildcards=True)
        subject = ".".join((*self._prefix_tokens(), *suffix))
        return ensure_nats_subject(subject, allow_wildcards=True)

    def bus_topic_for_nats_subject(self, nats_subject: str) -> str:
        suffix = self._nats_suffix(nats_subject, allow_wildcards=False)
        return ensure_valid_topic(".".join((BUS_TOPIC_PREFIX, *suffix)))

    def bus_filter_for_nats_filter(self, nats_filter: str) -> str:
        suffix = self._nats_suffix(nats_filter, allow_wildcards=True)
        return ensure_valid_topic(".".join((BUS_TOPIC_PREFIX, *suffix)), allow_wildcards=True)

    def _prefix_tokens(self) -> tuple[str, ...]:
        return tuple(self.subject_prefix.split("."))

    def _nats_suffix(self, nats_subject: str, *, allow_wildcards: bool) -> tuple[str, ...]:
        ensure_nats_subject(nats_subject, allow_wildcards=allow_wildcards)
        prefix = self._prefix_tokens()
        tokens = tuple(nats_subject.split("."))
        if tokens[: len(prefix)] != prefix:
            msg = f"NATS subject '{nats_subject}' must start with '{self.subject_prefix}'"
            raise ValueError(msg)
        suffix = tokens[len(prefix) :]
        if not suffix:
            msg = f"NATS subject '{nats_subject}' must include an OSIP topic suffix"
            raise ValueError(msg)
        return suffix


class NatsPublishRecord(BaseModel):
    """Broker-independent NATS publish request derived from an OSIP bus message."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    nats_subject: str
    bus_topic: str
    payload: bytes
    mode: Literal["core", "jetstream"]
    ack_policy: Literal["none", "explicit"]
    retain_last_per_subject: bool
    max_msgs_per_subject: int | None = Field(default=None, gt=0)
    max_age_ms: int | None = Field(default=None, gt=0)
    message_type: str

    @field_validator("nats_subject")
    @classmethod
    def validate_nats_subject(cls, value: str) -> str:
        return ensure_nats_subject(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class NatsDecodedRecord(BaseModel):
    """Decoded NATS message ready to be published on an OSIP bus."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    nats_subject: str
    bus_topic: str
    payload: OSIPMessage
    message_type: str

    @field_validator("nats_subject")
    @classmethod
    def validate_nats_subject(cls, value: str) -> str:
        return ensure_nats_subject(value)

    @field_validator("bus_topic")
    @classmethod
    def validate_bus_topic(cls, value: str) -> str:
        return ensure_valid_topic(value)


class NatsBridgeCodec:
    """Encode and decode OSIP messages for a NATS bridge without opening a socket."""

    def __init__(self, mapper: NatsSubjectMapper | None = None) -> None:
        self._mapper = mapper or NatsSubjectMapper()

    @property
    def mapper(self) -> NatsSubjectMapper:
        return self._mapper

    def encode_publish(
        self,
        bus_topic: str,
        payload: OSIPMessage | Mapping[str, Any],
    ) -> NatsPublishRecord:
        message = _ensure_osip_message(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        ensure_channel_message_type(channel_id, message.type)
        qos = map_to_nats(qos_for_channel(channel_id))
        return NatsPublishRecord(
            nats_subject=self._mapper.nats_subject_for_bus_topic(bus_topic),
            bus_topic=bus_topic,
            payload=message.model_dump_json(exclude_none=True).encode("utf-8"),
            mode=qos.mode,
            ack_policy=qos.ack_policy,
            retain_last_per_subject=qos.retain_last_per_subject,
            max_msgs_per_subject=qos.max_msgs_per_subject,
            max_age_ms=qos.max_age_ms,
            message_type=message.type,
        )

    def decode_message(
        self,
        nats_subject: str,
        payload: str | bytes | bytearray,
    ) -> NatsDecodedRecord:
        bus_topic = self._mapper.bus_topic_for_nats_subject(nats_subject)
        message = from_json(payload)
        channel_id = channel_id_for_bus_topic(bus_topic)
        ensure_channel_message_type(channel_id, message.type)
        return NatsDecodedRecord(
            nats_subject=nats_subject,
            bus_topic=bus_topic,
            payload=message,
            message_type=message.type,
        )


def ensure_nats_subject(subject: str, *, allow_wildcards: bool = False) -> str:
    """Validate the conservative NATS subject subset used by OSIP adapters."""

    return ensure_valid_topic(subject, allow_wildcards=allow_wildcards)


def _bus_suffix(bus_topic: str, *, allow_wildcards: bool) -> tuple[str, ...]:
    ensure_valid_topic(bus_topic, allow_wildcards=allow_wildcards)
    tokens = tuple(bus_topic.split("."))
    if tokens[0] != BUS_TOPIC_PREFIX:
        msg = f"OSIP bus topic '{bus_topic}' must start with '{BUS_TOPIC_PREFIX}'"
        raise ValueError(msg)
    suffix = tokens[1:]
    if not suffix:
        msg = f"OSIP bus topic '{bus_topic}' must include a suffix"
        raise ValueError(msg)
    return suffix


def _ensure_osip_message(payload: OSIPMessage | Mapping[str, Any]) -> OSIPMessage:
    if isinstance(payload, Mapping):
        return validate_osip_message(payload)
    return payload
