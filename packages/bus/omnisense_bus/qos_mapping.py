"""Adapter-specific mappings from OSIP QoS intent."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from omnisense_bus.qos import QoSProfile

type AdapterKind = Literal["ros2_dds", "mqtt5", "nats"]
type MqttQoSLevel = Literal[0, 1]


class QoSMapping(BaseModel):
    """Strict base model for generated adapter QoS mappings."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Ros2DDSQoSMapping(QoSMapping):
    """ROS 2 / DDS QoS policy mapping."""

    reliability: Literal["best_effort", "reliable"]
    durability: Literal["volatile", "transient_local"]
    history: Literal["keep_last", "keep_all"]
    depth: int = Field(gt=0)
    deadline_ms: int | None = Field(default=None, gt=0)
    lifespan_ms: int | None = Field(default=None, gt=0)
    priority: str
    notes: list[str] = Field(default_factory=list)


class Mqtt5QoSMapping(QoSMapping):
    """MQTT 5 publish/subscribe QoS mapping."""

    qos: MqttQoSLevel
    retain: bool
    message_expiry_interval_ms: int | None = Field(default=None, gt=0)
    priority: str
    notes: list[str] = Field(default_factory=list)


class NatsQoSMapping(QoSMapping):
    """NATS Core or JetStream mapping."""

    mode: Literal["core", "jetstream"]
    ack_policy: Literal["none", "explicit"]
    retain_last_per_subject: bool
    max_msgs_per_subject: int | None = Field(default=None, gt=0)
    max_age_ms: int | None = Field(default=None, gt=0)
    priority: str
    notes: list[str] = Field(default_factory=list)


type AdapterQoSMapping = Ros2DDSQoSMapping | Mqtt5QoSMapping | NatsQoSMapping


def map_qos_profile(profile: QoSProfile, adapter: AdapterKind) -> AdapterQoSMapping:
    """Map a transport-neutral OSIP QoS profile to one adapter family."""

    if adapter == "ros2_dds":
        return map_to_ros2_dds(profile)
    if adapter == "mqtt5":
        return map_to_mqtt5(profile)
    if adapter == "nats":
        return map_to_nats(profile)
    msg = f"unsupported adapter kind '{adapter}'"
    raise ValueError(msg)


def map_to_ros2_dds(profile: QoSProfile) -> Ros2DDSQoSMapping:
    notes = list(profile.adapter_notes)
    if profile.max_latency_ms is not None:
        notes.append("max_latency_ms is measured as benchmark or telemetry, not a DDS policy")
    return Ros2DDSQoSMapping(
        reliability=profile.delivery,
        durability=profile.durability,
        history=profile.history,
        depth=profile.depth,
        deadline_ms=profile.deadline_ms,
        lifespan_ms=profile.ttl_ms,
        priority=profile.priority,
        notes=notes,
    )


def map_to_mqtt5(profile: QoSProfile) -> Mqtt5QoSMapping:
    notes = list(profile.adapter_notes)
    if profile.deadline_ms is not None:
        notes.append("deadline_ms requires adapter watchdog or telemetry outside MQTT QoS")
    if profile.history == "keep_all":
        notes.append("keep_all history requires adapter-side buffering")
    return Mqtt5QoSMapping(
        qos=0 if profile.delivery == "best_effort" else 1,
        retain=profile.durability == "transient_local",
        message_expiry_interval_ms=profile.ttl_ms,
        priority=profile.priority,
        notes=notes,
    )


def map_to_nats(profile: QoSProfile) -> NatsQoSMapping:
    durable_or_reliable = profile.delivery == "reliable" or profile.durability == "transient_local"
    notes = list(profile.adapter_notes)
    if profile.deadline_ms is not None:
        notes.append("deadline_ms requires adapter watchdog or telemetry outside NATS delivery")
    if profile.max_latency_ms is not None:
        notes.append("max_latency_ms should be reported by benchmark or telemetry")
    return NatsQoSMapping(
        mode="jetstream" if durable_or_reliable else "core",
        ack_policy="explicit" if profile.delivery == "reliable" else "none",
        retain_last_per_subject=profile.durability == "transient_local",
        max_msgs_per_subject=profile.depth if profile.history == "keep_last" else None,
        max_age_ms=profile.ttl_ms,
        priority=profile.priority,
        notes=notes,
    )
