"""Deterministic in-memory embedding store for OSIP EmbeddingRef objects."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from omnisense_osip import EmbeddingRef, PerceptPacket
from omnisense_osip.schemas import OSIPModel
from pydantic import Field, model_validator


class EmbeddingRecord(OSIPModel):
    """Stored vector and provenance metadata for one OSIP embedding reference."""

    ref: EmbeddingRef
    vector: tuple[float, ...]
    source_message_id: str | None = Field(default=None, min_length=1)
    trace_id: str | None = Field(default=None, min_length=1)
    correlation_id: str | None = Field(default=None, min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_vector_shape(self) -> EmbeddingRecord:
        _validate_vector(self.vector, expected_dimension=self.ref.dimension)
        return self


class EmbeddingSearchHit(OSIPModel):
    """One similarity-search result."""

    record: EmbeddingRecord
    score: float = Field(ge=-1.0, le=1.0)


class EmbeddingStoreStats(OSIPModel):
    """Small machine-readable summary for tests, diagnostics, and dashboards."""

    total_records: int = Field(ge=0)
    spaces: dict[str, int] = Field(default_factory=dict)


class EmbeddingStore(Protocol):
    """Storage boundary for OSIP embedding vectors."""

    def upsert(
        self,
        ref: EmbeddingRef,
        vector: Sequence[float],
        *,
        source_message_id: str | None = None,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EmbeddingRecord: ...

    def upsert_percept(
        self,
        percept: PerceptPacket,
        vector: Sequence[float],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> EmbeddingRecord: ...

    def get(self, ref: str | EmbeddingRef) -> EmbeddingRecord | None: ...

    def delete(self, ref: str | EmbeddingRef) -> bool: ...

    def search(
        self,
        query: Sequence[float],
        *,
        space: str,
        limit: int = 10,
        min_score: float | None = None,
    ) -> tuple[EmbeddingSearchHit, ...]: ...

    def stats(self) -> EmbeddingStoreStats: ...


class InMemoryEmbeddingStore:
    """Hardware-free reference store for deterministic tests and local replay."""

    def __init__(self) -> None:
        self._records: dict[str, EmbeddingRecord] = {}

    def upsert(
        self,
        ref: EmbeddingRef,
        vector: Sequence[float],
        *,
        source_message_id: str | None = None,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EmbeddingRecord:
        normalized = _validate_vector(vector, expected_dimension=ref.dimension)
        existing = self._records.get(ref.ref)
        if existing is not None and (
            existing.ref.dimension != ref.dimension or existing.ref.space != ref.space
        ):
            msg = (
                f"embedding ref '{ref.ref}' already exists with dimension "
                f"{existing.ref.dimension} and space '{existing.ref.space}'"
            )
            raise ValueError(msg)

        record = EmbeddingRecord(
            ref=ref,
            vector=normalized,
            source_message_id=source_message_id,
            trace_id=trace_id,
            correlation_id=correlation_id,
            metadata=dict(metadata or {}),
        )
        self._records[ref.ref] = record
        return record

    def upsert_percept(
        self,
        percept: PerceptPacket,
        vector: Sequence[float],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> EmbeddingRecord:
        if percept.embedding is None:
            msg = f"percept '{percept.id}' does not contain an embedding reference"
            raise ValueError(msg)
        merged_metadata: dict[str, Any] = {
            "message_type": percept.type,
            "source_model": percept.source_model,
            "modality": percept.modality,
        }
        if metadata is not None:
            merged_metadata.update(metadata)
        return self.upsert(
            percept.embedding,
            vector,
            source_message_id=percept.id,
            trace_id=percept.trace_id,
            correlation_id=percept.correlation_id,
            metadata=merged_metadata,
        )

    def get(self, ref: str | EmbeddingRef) -> EmbeddingRecord | None:
        return self._records.get(_ref_key(ref))

    def delete(self, ref: str | EmbeddingRef) -> bool:
        key = _ref_key(ref)
        if key not in self._records:
            return False
        del self._records[key]
        return True

    def search(
        self,
        query: Sequence[float],
        *,
        space: str,
        limit: int = 10,
        min_score: float | None = None,
    ) -> tuple[EmbeddingSearchHit, ...]:
        if limit <= 0:
            msg = "limit must be greater than zero"
            raise ValueError(msg)
        if min_score is not None and not -1.0 <= min_score <= 1.0:
            msg = "min_score must be between -1.0 and 1.0"
            raise ValueError(msg)
        candidates = tuple(record for record in self._records.values() if record.ref.space == space)
        if not candidates:
            return ()
        dimensions = {record.ref.dimension for record in candidates}
        if len(dimensions) != 1:
            msg = f"embedding space '{space}' contains mixed dimensions"
            raise ValueError(msg)
        query_vector = _validate_vector(query, expected_dimension=dimensions.pop())
        hits = tuple(
            EmbeddingSearchHit(record=record, score=_cosine_similarity(query_vector, record.vector))
            for record in candidates
        )
        filtered = (
            hit for hit in hits if min_score is None or hit.score >= min_score
        )
        return tuple(
            sorted(filtered, key=lambda hit: (-hit.score, hit.record.ref.ref))[:limit]
        )

    def stats(self) -> EmbeddingStoreStats:
        spaces: dict[str, int] = {}
        for record in self._records.values():
            spaces[record.ref.space] = spaces.get(record.ref.space, 0) + 1
        return EmbeddingStoreStats(
            total_records=len(self._records),
            spaces=dict(sorted(spaces.items())),
        )


def _ref_key(ref: str | EmbeddingRef) -> str:
    if isinstance(ref, EmbeddingRef):
        return ref.ref
    if not ref:
        msg = "embedding ref must be non-empty"
        raise ValueError(msg)
    return ref


def _validate_vector(vector: Sequence[float], *, expected_dimension: int) -> tuple[float, ...]:
    if isinstance(vector, str | bytes | bytearray):
        msg = "embedding vector must be a numeric sequence"
        raise TypeError(msg)
    values = tuple(float(value) for value in vector)
    if len(values) != expected_dimension:
        msg = (
            f"embedding vector dimension {len(values)} does not match "
            f"expected {expected_dimension}"
        )
        raise ValueError(msg)
    if not values:
        msg = "embedding vector must not be empty"
        raise ValueError(msg)
    if any(not math.isfinite(value) for value in values):
        msg = "embedding vector must contain only finite values"
        raise ValueError(msg)
    if _norm(values) == 0.0:
        msg = "embedding vector norm must be greater than zero"
        raise ValueError(msg)
    return values


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True)) / (_norm(left) * _norm(right))


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))
