"""Pydantic v2 models for OSIP v0.1 public messages."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

OSIP_SCHEMA_VERSION: Literal["osip/0.1"] = "osip/0.1"

LABEL_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$"
IDENTIFIER_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*(_v[0-9]+)?$"

type Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
type NonNegativeInt = Annotated[int, Field(ge=0)]
type PositiveInt = Annotated[int, Field(gt=0)]
type Label = Annotated[str, Field(min_length=1, pattern=LABEL_PATTERN)]
type Identifier = Annotated[str, Field(min_length=1, pattern=IDENTIFIER_PATTERN)]
type ProfileIdentifier = Annotated[
    str,
    Field(min_length=1, pattern=r"^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$"),
]
type TraceIdentifier = Annotated[str, Field(min_length=1)]

type QualityStatus = Literal["usable", "degraded", "unusable"]
type RiskClass = Literal["low", "medium", "high", "critical"]
type ActionPriority = Literal["low", "normal", "high", "critical"]
type EvidenceSourceType = Literal[
    "percept.packet",
    "context.update",
    "event.detected",
    "action.result",
    "external",
]
type ActionResultStatus = Literal[
    "accepted",
    "executed",
    "failed",
    "blocked",
    "timed_out",
    "rolled_back",
]
type SafeStateTrigger = Literal[
    "heartbeat_timeout",
    "context_stale",
    "bus_disconnect",
    "adapter_error",
    "manual_estop",
    "contract_violation",
    "sensor_dropout",
]
type HeartbeatStatus = Literal[
    "alive",
    "degraded",
    "safe_state_active",
    "stopping",
    "failed",
]


def require_timezone(value: datetime) -> datetime:
    """Reject naive datetimes so OSIP events remain replayable across machines."""
    if value.tzinfo is None or value.utcoffset() is None:
        msg = "timestamp fields must include timezone information"
        raise ValueError(msg)
    return value


def require_optional_timezone(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return require_timezone(value)


class OSIPModel(BaseModel):
    """Strict base model shared by all public OSIP payloads."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class LatencyProfile(OSIPModel):
    p50_ms: PositiveInt
    p95_ms: PositiveInt
    max_budget_ms: PositiveInt

    @model_validator(mode="after")
    def validate_latency_order(self) -> Self:
        if not self.p50_ms <= self.p95_ms <= self.max_budget_ms:
            msg = "latency profile must satisfy p50_ms <= p95_ms <= max_budget_ms"
            raise ValueError(msg)
        return self


class EmbeddingCapability(OSIPModel):
    available: bool
    dimension: PositiveInt | None = None
    space: Identifier | None = None

    @model_validator(mode="after")
    def validate_available_embedding_metadata(self) -> Self:
        if self.available and (self.dimension is None or self.space is None):
            msg = "available embeddings require dimension and space"
            raise ValueError(msg)
        return self


class ModelCapabilityDescriptor(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["model.capability"] = "model.capability"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    model_id: Identifier
    display_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    modalities: list[Identifier] = Field(min_length=1)
    outputs: list[Label] = Field(min_length=1)
    latency_profile: LatencyProfile
    spatial_reference: Identifier | None = None
    confidence_calibrated: bool
    embedding: EmbeddingCapability | None = None


class CovarianceMatrix(OSIPModel):
    variables: list[Identifier] = Field(min_length=1)
    values: list[list[float]] = Field(min_length=1)
    unit: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_square_matrix(self) -> Self:
        dimension = len(self.variables)
        if len(self.values) != dimension or any(len(row) != dimension for row in self.values):
            msg = "covariance values must be a square matrix matching variables"
            raise ValueError(msg)
        return self


class Uncertainty(OSIPModel):
    confidence: Confidence | None = None
    covariance: CovarianceMatrix | None = None
    distribution: Identifier | None = None

    @model_validator(mode="after")
    def validate_uncertainty_representation(self) -> Self:
        if self.confidence is None and self.covariance is None and self.distribution is None:
            msg = "uncertainty requires confidence, covariance, or distribution"
            raise ValueError(msg)
        return self


class Location(OSIPModel):
    room: Identifier | None = None
    zone: Identifier | None = None
    azimuth_deg: float | None = Field(default=None, ge=-180.0, le=180.0)
    coordinates: dict[str, float] | None = None
    uncertainty: Uncertainty | None = None


class Claim(OSIPModel):
    label: Label
    confidence: Confidence
    value: bool | int | float | str | dict[str, Any] | list[Any] | None = None
    uncertainty: Uncertainty | None = None


class EmbeddingRef(OSIPModel):
    ref: str = Field(min_length=1)
    dimension: PositiveInt
    space: Identifier


class SensorQuality(OSIPModel):
    status: QualityStatus
    signal_noise: Confidence | None = None
    drift_score: Confidence | None = None


class PerceptPacket(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["percept.packet"] = "percept.packet"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    id: str = Field(min_length=1)
    source_model: Identifier
    modality: Identifier
    timestamp: datetime
    received_at: datetime | None = None
    valid_for_ms: PositiveInt
    latency_ms: NonNegativeInt
    location: Location | None = None
    claims: list[Claim] = Field(min_length=1)
    embedding: EmbeddingRef | None = None
    quality: SensorQuality

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)

    @field_validator("received_at")
    @classmethod
    def received_at_has_timezone(cls, value: datetime | None) -> datetime | None:
        return require_optional_timezone(value)


class ContextEntity(OSIPModel):
    id: str = Field(min_length=1)
    type: Identifier
    zone: Identifier | None = None
    state: Identifier | None = None
    confidence: Confidence
    uncertainty: Uncertainty | None = None


class EvidenceRef(OSIPModel):
    """Structured reference to the source evidence behind a context event."""

    source_type: EvidenceSourceType
    source_id: str = Field(min_length=1)
    claim_label: Label | None = None
    confidence: Confidence | None = None
    source_model: Identifier | None = None
    modality: Identifier | None = None
    timestamp: datetime | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime | None) -> datetime | None:
        return require_optional_timezone(value)


class ContextEvent(OSIPModel):
    label: Label
    confidence: Confidence
    urgency: Confidence
    evidence: list[Label] = Field(min_length=1)
    contradictions: list[Label] = Field(default_factory=list)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    contradiction_refs: list[EvidenceRef] = Field(default_factory=list)
    uncertainty: Uncertainty | None = None


class GlobalRisk(OSIPModel):
    safety: Confidence
    comfort: Confidence
    maintenance: Confidence


class ContextUpdate(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["context.update"] = "context.update"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    context_id: str = Field(min_length=1)
    timestamp: datetime
    time_window_ms: PositiveInt
    room: Identifier
    entities: list[ContextEntity] = Field(default_factory=list)
    events: list[ContextEvent] = Field(default_factory=list)
    global_risk: GlobalRisk

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


class EventDetected(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["event.detected"] = "event.detected"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    event_id: str = Field(min_length=1)
    timestamp: datetime
    label: Label
    confidence: Confidence
    urgency: Confidence
    room: Identifier | None = None
    zone: Identifier | None = None
    evidence: list[Label] = Field(min_length=1)
    contradictions: list[Label] = Field(default_factory=list)
    context_id: str | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


class ActionContract(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["action.contract"] = "action.contract"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    action_id: Label
    target: Label
    operation: Label
    risk_class: RiskClass
    allowed_contexts: list[Label] = Field(min_length=1)
    preconditions: list[str] = Field(min_length=1)
    min_confidence: Confidence
    max_decision_latency_ms: PositiveInt
    cooldown_ms: NonNegativeInt
    rollback: Label | None = None
    safe_state: Label | None = None
    idempotent: bool

    @model_validator(mode="after")
    def validate_high_risk_boundary(self) -> Self:
        if (
            self.risk_class in {"high", "critical"}
            and self.rollback is None
            and self.safe_state is None
        ):
            msg = "high and critical actions require rollback or safe_state"
            raise ValueError(msg)
        return self


class ActionProposal(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["action.proposal"] = "action.proposal"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    proposal_id: str = Field(min_length=1)
    based_on_context: str = Field(min_length=1)
    action_id: Label
    priority: ActionPriority
    confidence: Confidence
    deadline_ms: PositiveInt
    reason: str = Field(min_length=1)
    requires_confirmation: bool


class ActionCommand(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["action.command"] = "action.command"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    command_id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)
    action_id: Label
    target: Label
    operation: Label
    parameters: dict[str, Any] = Field(default_factory=dict)
    execute_before_ms: PositiveInt
    idempotency_key: str = Field(min_length=1)


class ActionResult(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["action.result"] = "action.result"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    result_id: str = Field(min_length=1)
    command_id: str = Field(min_length=1)
    action_id: Label
    status: ActionResultStatus
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: NonNegativeInt | None = None
    error: str | None = None
    output: dict[str, Any] = Field(default_factory=dict)
    rollback_performed: bool = False

    @field_validator("started_at")
    @classmethod
    def started_at_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)

    @field_validator("completed_at")
    @classmethod
    def completed_at_has_timezone(cls, value: datetime | None) -> datetime | None:
        return require_optional_timezone(value)

    @model_validator(mode="after")
    def validate_completion_order(self) -> Self:
        if self.completed_at is not None and self.completed_at < self.started_at:
            msg = "completed_at must be greater than or equal to started_at"
            raise ValueError(msg)
        return self


class DefaultSafeState(OSIPModel):
    target: Label
    safe_state: Label
    triggers: list[SafeStateTrigger] = Field(min_length=1)
    max_transition_ms: PositiveInt | None = None
    requires_hardware_interlock: bool = False


class ProfileSafetyCase(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["profile.safety_case"] = "profile.safety_case"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    safety_case_id: str = Field(min_length=1)
    profile_id: ProfileIdentifier
    heartbeat_timeout_ms: PositiveInt
    stale_context_ms: PositiveInt
    default_safe_states: list[DefaultSafeState] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)


class AdapterHeartbeat(OSIPModel):
    schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    type: Literal["adapter.heartbeat"] = "adapter.heartbeat"
    trace_id: TraceIdentifier | None = None
    correlation_id: TraceIdentifier | None = None
    heartbeat_id: str = Field(min_length=1)
    adapter_id: Identifier
    profile_id: ProfileIdentifier
    timestamp: datetime
    status: HeartbeatStatus
    ttl_ms: PositiveInt
    last_context_id: str | None = Field(default=None, min_length=1)
    current_safe_state: Label | None = None
    missed_count: NonNegativeInt = 0
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)
