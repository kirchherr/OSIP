"""Dashboard snapshot models for gateway state inspection."""

from __future__ import annotations

from datetime import datetime

from omnisense_context import ContextGraphStats
from omnisense_osip import ActionProposal, ContextUpdate, PerceptPacket
from omnisense_osip.schemas import OSIPModel, require_timezone
from pydantic import Field, field_validator


class LatencySummary(OSIPModel):
    """Latency summary for recent percept ingestion."""

    count: int = Field(ge=0)
    min_ms: int | None = Field(default=None, ge=0)
    max_ms: int | None = Field(default=None, ge=0)
    avg_ms: float | None = Field(default=None, ge=0.0)


class DashboardCounters(OSIPModel):
    """Runtime counters exposed to dashboards and demos."""

    models_registered: int = Field(ge=0)
    model_plugins_registered: int = Field(ge=0)
    percepts_ingested: int = Field(ge=0)
    contexts_emitted: int = Field(ge=0)
    action_proposals_emitted: int = Field(ge=0)


class DashboardSnapshot(OSIPModel):
    """Machine-readable dashboard state for local demos and tests."""

    generated_at: datetime
    counters: DashboardCounters
    registered_models: tuple[str, ...] = Field(default_factory=tuple)
    registered_plugins: tuple[str, ...] = Field(default_factory=tuple)
    current_context: ContextUpdate | None = None
    context_graph: ContextGraphStats
    recent_percepts: tuple[PerceptPacket, ...] = Field(default_factory=tuple)
    recent_action_proposals: tuple[ActionProposal, ...] = Field(default_factory=tuple)
    recent_percept_latency_ms: LatencySummary

    @field_validator("generated_at")
    @classmethod
    def generated_at_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


def summarize_latency(percepts: tuple[PerceptPacket, ...]) -> LatencySummary:
    """Summarize latency from a bounded recent-percept window."""

    if not percepts:
        return LatencySummary(count=0)
    latencies = tuple(percept.latency_ms for percept in percepts)
    return LatencySummary(
        count=len(latencies),
        min_ms=min(latencies),
        max_ms=max(latencies),
        avg_ms=sum(latencies) / len(latencies),
    )
