"""Scenario schemas for deterministic OSIP replay."""

from __future__ import annotations

from typing import Any, Literal, Self

from omnisense_osip.schemas import Claim, Location, ProfileSafetyCase, SensorQuality
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScenarioModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class LatencyBudget(ScenarioModel):
    first_context_update: int | None = Field(default=None, gt=0)
    first_action_proposal: int | None = Field(default=None, gt=0)


class ExpectedSafeStateActivation(ScenarioModel):
    target: str = Field(min_length=1)
    safe_state: str = Field(min_length=1)
    trigger: str = Field(min_length=1)

    def key(self) -> str:
        return f"{self.target}->{self.safe_state}:{self.trigger}"


class ScenarioAdapterHeartbeat(ScenarioModel):
    at_ms: int = Field(ge=0)
    adapter_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    status: Literal["alive", "degraded", "safe_state_active", "stopping", "failed"] = "alive"
    ttl_ms: int = Field(gt=0)
    heartbeat_id: str | None = Field(default=None, min_length=1)
    last_context_id: str | None = Field(default=None, min_length=1)
    current_safe_state: str | None = Field(default=None, min_length=1)
    missed_count: int = Field(default=0, ge=0)
    details: dict[str, Any] = Field(default_factory=dict)


class ScenarioSafetyEvaluation(ScenarioModel):
    safety_case: ProfileSafetyCase
    evaluate_at_ms: int | None = Field(default=None, ge=0)
    heartbeats: list[ScenarioAdapterHeartbeat] = Field(default_factory=list)
    bus_connected: bool = True
    manual_estop: bool = False
    contract_violation: bool = False
    sensor_dropout: bool = False
    expect_safe: bool = True
    expected_safe_states: list[ExpectedSafeStateActivation] = Field(default_factory=list)


class RandomizationRange(ScenarioModel):
    min: float
    max: float
    unit: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_ordered_range(self) -> Self:
        if self.min > self.max:
            msg = "randomization range min must be less than or equal to max"
            raise ValueError(msg)
        return self


class DomainRandomizationSetting(ScenarioModel):
    parameter: str = Field(min_length=1)
    distribution: Literal["uniform", "normal", "choice", "fixed"]
    range: RandomizationRange | None = None
    choices: list[bool | int | float | str] = Field(default_factory=list)
    seed: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_distribution_payload(self) -> Self:
        if self.distribution in {"uniform", "normal"} and self.range is None:
            msg = "uniform and normal randomization require range"
            raise ValueError(msg)
        if self.distribution == "choice" and not self.choices:
            msg = "choice randomization requires choices"
            raise ValueError(msg)
        if self.distribution == "fixed" and self.range is None and not self.choices:
            msg = "fixed randomization requires range or choices"
            raise ValueError(msg)
        return self


class Sim2RealMetadata(ScenarioModel):
    simulator: str = Field(min_length=1)
    simulator_version: str = Field(min_length=1)
    seed: int = Field(ge=0)
    robot_description_ref: str | None = Field(default=None, min_length=1)
    world_description_ref: str | None = Field(default=None, min_length=1)
    robot_world_hash: str | None = Field(default=None, min_length=1)
    sensor_noise_model: str | None = Field(default=None, min_length=1)
    latency_jitter_ms: int | None = Field(default=None, ge=0)
    domain_randomization: list[DomainRandomizationSetting] = Field(default_factory=list)


class ScenarioQuality(ScenarioModel):
    status: str = Field(default="usable")
    signal_noise: float | None = Field(default=None, ge=0.0, le=1.0)
    drift_score: float | None = Field(default=None, ge=0.0, le=1.0)

    def to_sensor_quality(self) -> SensorQuality:
        return SensorQuality.model_validate(self.model_dump())


class ScenarioPercept(ScenarioModel):
    at_ms: int = Field(ge=0)
    source_model: str = Field(min_length=1)
    modality: str = Field(min_length=1)
    claims: list[Claim] = Field(min_length=1)
    valid_for_ms: int = Field(default=1000, gt=0)
    latency_ms: int = Field(default=0, ge=0)
    location: Location | None = None
    quality: ScenarioQuality = Field(default_factory=ScenarioQuality)
    id: str | None = Field(default=None, min_length=1)
    embedding: dict[str, Any] | None = None


class ScenarioDefinition(ScenarioModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    application_profile: str = Field(default="rooms", min_length=1)
    duration_ms: int = Field(gt=0)
    room: str = Field(min_length=1)
    expected_contexts: list[str] = Field(default_factory=list)
    expected_actions: list[str] = Field(default_factory=list)
    latency_budget_ms: LatencyBudget = Field(default_factory=LatencyBudget)
    sim2real: Sim2RealMetadata | None = None
    safety: ScenarioSafetyEvaluation | None = None
    percepts: list[ScenarioPercept] = Field(min_length=1)

    @field_validator("id", "application_profile", "room")
    @classmethod
    def identifiers_use_topic_safe_characters(cls, value: str) -> str:
        if value.strip() != value or not value:
            msg = "scenario identifiers must be non-empty and trimmed"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_timeline(self) -> Self:
        for percept in self.percepts:
            if percept.at_ms > self.duration_ms:
                msg = "percept at_ms must not exceed scenario duration_ms"
                raise ValueError(msg)
        if self.safety is not None:
            if (
                self.safety.evaluate_at_ms is not None
                and self.safety.evaluate_at_ms > self.duration_ms
            ):
                msg = "safety evaluate_at_ms must not exceed scenario duration_ms"
                raise ValueError(msg)
            for heartbeat in self.safety.heartbeats:
                if heartbeat.at_ms > self.duration_ms:
                    msg = "heartbeat at_ms must not exceed scenario duration_ms"
                    raise ValueError(msg)
        return self
