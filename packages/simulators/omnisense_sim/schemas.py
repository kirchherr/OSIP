"""Scenario schemas for deterministic OSIP replay."""

from __future__ import annotations

from typing import Any, Self

from omnisense_osip.schemas import Claim, Location, SensorQuality
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScenarioModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class LatencyBudget(ScenarioModel):
    first_context_update: int | None = Field(default=None, gt=0)
    first_action_proposal: int | None = Field(default=None, gt=0)


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
        return self
