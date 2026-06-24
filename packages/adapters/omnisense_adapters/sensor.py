"""Generic sensor reading adapter boundary for OSIP PerceptPacket publishing."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, Protocol

from omnisense_bus import AsyncMessageBus, percept_topic
from omnisense_osip import (
    Claim,
    EmbeddingRef,
    Location,
    ModelCapabilityDescriptor,
    PerceptPacket,
    SensorQuality,
)
from omnisense_osip.schemas import (
    Identifier,
    OSIPModel,
    require_optional_timezone,
    require_timezone,
)
from pydantic import Field, field_validator

from omnisense_adapters.interfaces import AdapterMetadata, AdapterRunResult


class SensorReading(OSIPModel):
    """Hardware-neutral reading that can be converted into one OSIP percept."""

    reading_id: str = Field(min_length=1)
    modality: Identifier
    timestamp: datetime
    received_at: datetime | None = None
    valid_for_ms: int = Field(gt=0)
    latency_ms: int = Field(ge=0)
    location: Location | None = None
    claims: tuple[Claim, ...] = Field(min_length=1)
    quality: SensorQuality
    embedding: EmbeddingRef | None = None
    trace_id: str | None = Field(default=None, min_length=1)
    correlation_id: str | None = Field(default=None, min_length=1)
    raw: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)

    @field_validator("received_at")
    @classmethod
    def received_at_has_timezone(cls, value: datetime | None) -> datetime | None:
        return require_optional_timezone(value)


class SensorReadingSource(Protocol):
    """Minimal wrapper around a real or simulated sensor source."""

    async def receive(self) -> SensorReading | None: ...


class SensorToPerceptAdapter:
    """Convert bounded sensor readings into validated OSIP percept packets."""

    def __init__(
        self,
        source: SensorReadingSource,
        capability: ModelCapabilityDescriptor,
        *,
        adapter_id: str = "sensor.percept_source",
        profile_id: str | None = None,
        requires_hardware: bool = False,
        supported_message_types: Iterable[str] = ("percept.packet",),
    ) -> None:
        supported = tuple(dict.fromkeys(supported_message_types))
        if not supported:
            msg = "supported_message_types must not be empty"
            raise ValueError(msg)
        if "percept.packet" not in supported:
            msg = "SensorToPerceptAdapter must support 'percept.packet'"
            raise ValueError(msg)
        self._source = source
        self._capability = capability
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="source",
            supported_message_types=supported,
            profile_id=profile_id,
            requires_hardware=requires_hardware,
            description="Generic sensor reading source adapter for OSIP percept publishing.",
        )

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    @property
    def capability(self) -> ModelCapabilityDescriptor:
        return self._capability

    def build_percept(self, reading: SensorReading) -> PerceptPacket:
        """Convert one source reading into a validated OSIP PerceptPacket."""

        self._validate_reading(reading)
        return PerceptPacket(
            id=reading.reading_id,
            source_model=self._capability.model_id,
            modality=reading.modality,
            timestamp=reading.timestamp,
            received_at=reading.received_at,
            valid_for_ms=reading.valid_for_ms,
            latency_ms=reading.latency_ms,
            location=reading.location,
            claims=list(reading.claims),
            embedding=reading.embedding,
            quality=reading.quality,
            trace_id=reading.trace_id or reading.reading_id,
            correlation_id=reading.correlation_id or reading.trace_id or reading.reading_id,
        )

    async def publish_to(
        self,
        bus: AsyncMessageBus,
        *,
        max_readings: int | None = None,
    ) -> AdapterRunResult:
        if max_readings is not None and max_readings < 0:
            msg = "max_readings must be greater than or equal to zero"
            raise ValueError(msg)

        topics: list[str] = []
        while max_readings is None or len(topics) < max_readings:
            reading = await self._source.receive()
            if reading is None:
                break
            percept = self.build_percept(reading)
            topic = percept_topic(percept.modality, percept.source_model)
            await bus.publish(topic, percept)
            topics.append(topic)

        return AdapterRunResult(
            adapter_id=self._metadata.adapter_id,
            published_count=len(topics),
            topics=tuple(topics),
            message_types=tuple("percept.packet" for _ in topics),
        )

    def _validate_reading(self, reading: SensorReading) -> None:
        if reading.modality not in self._capability.modalities:
            msg = (
                f"modality '{reading.modality}' is not declared by model "
                f"'{self._capability.model_id}'"
            )
            raise ValueError(msg)
        allowed_outputs = set(self._capability.outputs)
        unsupported = sorted(
            {claim.label for claim in reading.claims if claim.label not in allowed_outputs}
        )
        if unsupported:
            labels = ", ".join(unsupported)
            msg = f"claims are not declared by model '{self._capability.model_id}': {labels}"
            raise ValueError(msg)
