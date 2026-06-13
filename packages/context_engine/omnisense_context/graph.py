"""Persistable context graph snapshots for OSIP ContextUpdate payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, Self

from omnisense_osip import ContextEntity, ContextEvent, ContextUpdate
from omnisense_osip.schemas import OSIPModel, require_timezone
from pydantic import Field, field_validator, model_validator


class ContextGraphEntityRecord(OSIPModel):
    """Entity observation with graph provenance."""

    context_id: str = Field(min_length=1)
    room: str = Field(min_length=1)
    timestamp: datetime
    entity: ContextEntity

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


class ContextGraphEventRecord(OSIPModel):
    """Event observation with graph provenance."""

    context_id: str = Field(min_length=1)
    room: str = Field(min_length=1)
    timestamp: datetime
    event: ContextEvent

    @field_validator("timestamp")
    @classmethod
    def timestamp_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


class ContextGraphSnapshot(OSIPModel):
    """Portable JSON snapshot of a context graph."""

    schema_version: Literal["context_graph/0.1"] = "context_graph/0.1"
    graph_id: str = Field(min_length=1)
    generated_at: datetime
    updates: tuple[ContextUpdate, ...] = Field(default_factory=tuple)
    latest_context_by_room: dict[str, str] = Field(default_factory=dict)

    @field_validator("generated_at")
    @classmethod
    def generated_at_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)

    @model_validator(mode="after")
    def validate_latest_contexts(self) -> Self:
        updates_by_id = {update.context_id: update for update in self.updates}
        for room, context_id in self.latest_context_by_room.items():
            update = updates_by_id.get(context_id)
            if update is None:
                msg = (
                    f"latest context '{context_id}' for room '{room}' "
                    "does not exist in snapshot updates"
                )
                raise ValueError(msg)
            if update.room != room:
                msg = (
                    f"latest context '{context_id}' belongs to room "
                    f"'{update.room}', not '{room}'"
                )
                raise ValueError(msg)
        return self


class ContextGraphStats(OSIPModel):
    """Small graph summary for diagnostics and benchmark reports."""

    total_updates: int = Field(ge=0)
    total_entities: int = Field(ge=0)
    total_events: int = Field(ge=0)
    rooms: tuple[str, ...] = Field(default_factory=tuple)


class ContextGraph:
    """Append-only in-memory world-state graph derived from ContextUpdate messages."""

    def __init__(
        self,
        *,
        graph_id: str = "default",
        updates: tuple[ContextUpdate, ...] = (),
    ) -> None:
        if not graph_id:
            msg = "graph_id must be non-empty"
            raise ValueError(msg)
        self._graph_id = graph_id
        self._updates: dict[str, ContextUpdate] = {}
        self._latest_context_by_room: dict[str, str] = {}
        for update in updates:
            self.apply(update)

    @property
    def graph_id(self) -> str:
        return self._graph_id

    def apply(self, update: ContextUpdate) -> None:
        """Add one context update and refresh latest-room indexes."""

        if update.context_id in self._updates:
            msg = f"context update '{update.context_id}' already exists in graph"
            raise ValueError(msg)
        self._updates[update.context_id] = update
        current = self.latest(room=update.room)
        if current is None or _context_sort_key(update) >= _context_sort_key(current):
            self._latest_context_by_room[update.room] = update.context_id

    def latest(self, *, room: str | None = None) -> ContextUpdate | None:
        """Return the newest update globally or for one room."""

        if room is not None:
            context_id = self._latest_context_by_room.get(room)
            if context_id is None:
                return None
            return self._updates[context_id]
        updates = self.updates()
        if not updates:
            return None
        return updates[-1]

    def updates(self, *, room: str | None = None) -> tuple[ContextUpdate, ...]:
        """Return updates in deterministic timestamp/context-id order."""

        updates: tuple[ContextUpdate, ...] = tuple(self._updates.values())
        if room is not None:
            updates = tuple(update for update in updates if update.room == room)
        return tuple(sorted(updates, key=_context_sort_key))

    def entity_records(
        self,
        *,
        room: str | None = None,
        entity_id: str | None = None,
    ) -> tuple[ContextGraphEntityRecord, ...]:
        """Return entity observations with context provenance."""

        records = (
            ContextGraphEntityRecord(
                context_id=update.context_id,
                room=update.room,
                timestamp=update.timestamp,
                entity=entity,
            )
            for update in self.updates(room=room)
            for entity in update.entities
            if entity_id is None or entity.id == entity_id
        )
        return tuple(
            sorted(records, key=lambda item: (item.timestamp, item.context_id, item.entity.id))
        )

    def event_records(
        self,
        *,
        room: str | None = None,
        label: str | None = None,
    ) -> tuple[ContextGraphEventRecord, ...]:
        """Return event observations with context provenance."""

        records = (
            ContextGraphEventRecord(
                context_id=update.context_id,
                room=update.room,
                timestamp=update.timestamp,
                event=event,
            )
            for update in self.updates(room=room)
            for event in update.events
            if label is None or event.label == label
        )
        return tuple(
            sorted(records, key=lambda item: (item.timestamp, item.context_id, item.event.label))
        )

    def snapshot(self, *, generated_at: datetime | None = None) -> ContextGraphSnapshot:
        """Create a portable snapshot that can be serialized as JSON."""

        return ContextGraphSnapshot(
            graph_id=self.graph_id,
            generated_at=generated_at or self._default_snapshot_time(),
            updates=self.updates(),
            latest_context_by_room=dict(sorted(self._latest_context_by_room.items())),
        )

    def to_json(self, *, generated_at: datetime | None = None) -> str:
        """Serialize the current graph snapshot to JSON."""

        return self.snapshot(generated_at=generated_at).model_dump_json(exclude_none=True)

    def stats(self) -> ContextGraphStats:
        """Return a compact graph summary."""

        updates = self.updates()
        return ContextGraphStats(
            total_updates=len(updates),
            total_entities=sum(len(update.entities) for update in updates),
            total_events=sum(len(update.events) for update in updates),
            rooms=tuple(sorted(self._latest_context_by_room)),
        )

    @classmethod
    def from_snapshot(cls, snapshot: ContextGraphSnapshot) -> ContextGraph:
        graph = cls(graph_id=snapshot.graph_id, updates=snapshot.updates)
        if graph.snapshot(generated_at=snapshot.generated_at) != snapshot:
            msg = "context graph snapshot does not match deterministic graph indexes"
            raise ValueError(msg)
        return graph

    @classmethod
    def from_json(cls, payload: str | bytes | bytearray) -> ContextGraph:
        return cls.from_snapshot(ContextGraphSnapshot.model_validate_json(payload))

    def _default_snapshot_time(self) -> datetime:
        latest = self.latest()
        if latest is not None:
            return latest.timestamp
        return datetime(1970, 1, 1, tzinfo=UTC)


def _context_sort_key(update: ContextUpdate) -> tuple[datetime, str]:
    return (update.timestamp, update.context_id)
