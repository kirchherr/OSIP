"""Quality-of-service intent contracts for transport adapters."""

from __future__ import annotations

from typing import Annotated, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

type PositiveInt = Annotated[int, Field(gt=0)]
type DeliveryGuarantee = Literal["best_effort", "reliable"]
type Priority = Literal["low", "normal", "high", "critical"]
type Durability = Literal["volatile", "transient_local"]
type HistoryPolicy = Literal["keep_last", "keep_all"]


class QoSProfile(BaseModel):
    """Transport-neutral QoS intent for adapter mapping."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    delivery: DeliveryGuarantee
    priority: Priority
    history: HistoryPolicy = "keep_last"
    depth: PositiveInt = 1
    durability: Durability = "volatile"
    max_latency_ms: PositiveInt | None = None
    deadline_ms: PositiveInt | None = None
    ttl_ms: PositiveInt | None = None
    adapter_notes: list[str] = Field(default_factory=list)

    def as_asyncapi_extension(self) -> dict[str, object]:
        return self.model_dump(exclude_none=True, mode="json")


QOS_BY_CHANNEL: Final[dict[str, QoSProfile]] = {
    "modelCapabilities": QoSProfile(
        delivery="reliable",
        priority="normal",
        depth=16,
        durability="transient_local",
        adapter_notes=["Adapters may retain the latest capability set for late joiners."],
    ),
    "percepts": QoSProfile(
        delivery="best_effort",
        priority="high",
        max_latency_ms=10,
        deadline_ms=10,
        ttl_ms=50,
        adapter_notes=["Physical-AI adapters should map this to low-latency sensor-data QoS."],
    ),
    "contextUpdates": QoSProfile(
        delivery="best_effort",
        priority="high",
        max_latency_ms=25,
        deadline_ms=50,
        ttl_ms=100,
    ),
    "eventsDetected": QoSProfile(
        delivery="best_effort",
        priority="critical",
        max_latency_ms=10,
        deadline_ms=20,
        ttl_ms=100,
    ),
    "actionContracts": QoSProfile(
        delivery="reliable",
        priority="high",
        depth=32,
        durability="transient_local",
    ),
    "actionProposals": QoSProfile(
        delivery="reliable",
        priority="high",
        max_latency_ms=50,
        deadline_ms=100,
        depth=16,
    ),
    "actionCommands": QoSProfile(
        delivery="reliable",
        priority="critical",
        max_latency_ms=10,
        deadline_ms=20,
        depth=16,
    ),
    "actionResults": QoSProfile(
        delivery="reliable",
        priority="high",
        max_latency_ms=50,
        deadline_ms=100,
        depth=32,
    ),
    "profileSafetyCases": QoSProfile(
        delivery="reliable",
        priority="critical",
        depth=8,
        durability="transient_local",
        adapter_notes=["Adapters should load safe states before accepting action commands."],
    ),
    "adapterHeartbeats": QoSProfile(
        delivery="best_effort",
        priority="critical",
        max_latency_ms=10,
        deadline_ms=20,
        ttl_ms=50,
    ),
}


def qos_for_channel(channel_id: str) -> QoSProfile:
    try:
        return QOS_BY_CHANNEL[channel_id]
    except KeyError as exc:
        msg = f"unknown OSIP channel '{channel_id}'"
        raise ValueError(msg) from exc
