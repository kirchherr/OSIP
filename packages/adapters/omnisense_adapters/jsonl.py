"""JSONL source adapter for hardware-free OSIP ingestion tests."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Final

from omnisense_bus import AsyncMessageBus, load_jsonl_trace
from omnisense_osip import OSIPMessage, validate_osip_message

from omnisense_adapters.interfaces import AdapterMetadata, AdapterRunResult

DEFAULT_ALLOWED_MESSAGE_TYPES: Final[tuple[str, ...]] = (
    "model.capability",
    "percept.packet",
    "adapter.heartbeat",
)


class JSONLOSIPSourceAdapter:
    """Read OSIP JSONL records from disk, validate them, and publish them to the bus."""

    def __init__(
        self,
        path: Path,
        *,
        adapter_id: str = "jsonl.osip_source",
        profile_id: str | None = None,
        allowed_message_types: Iterable[str] = DEFAULT_ALLOWED_MESSAGE_TYPES,
    ) -> None:
        allowed = tuple(dict.fromkeys(allowed_message_types))
        if not allowed:
            msg = "allowed_message_types must not be empty"
            raise ValueError(msg)
        self._path = path
        self._allowed_message_types = allowed
        self._metadata = AdapterMetadata(
            adapter_id=adapter_id,
            role="source",
            supported_message_types=allowed,
            profile_id=profile_id,
            requires_hardware=False,
            description="Validating JSONL OSIP source adapter for tests and demos.",
        )

    @property
    def path(self) -> Path:
        return self._path

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    async def publish_to(self, bus: AsyncMessageBus) -> AdapterRunResult:
        topics: list[str] = []
        message_types: list[str] = []

        for record in load_jsonl_trace(self._path):
            if not isinstance(record.payload, Mapping):
                msg = f"payload for topic '{record.topic}' must be an OSIP JSON object"
                raise ValueError(msg)
            payload = validate_osip_message(record.payload)
            message_type = _message_type(payload)
            if message_type not in self._allowed_message_types:
                msg = (
                    f"message type '{message_type}' is not allowed by adapter "
                    f"'{self._metadata.adapter_id}'"
                )
                raise ValueError(msg)

            await bus.publish(record.topic, payload)
            topics.append(record.topic)
            message_types.append(message_type)

        return AdapterRunResult(
            adapter_id=self._metadata.adapter_id,
            published_count=len(topics),
            topics=tuple(topics),
            message_types=tuple(message_types),
        )


def _message_type(payload: OSIPMessage) -> str:
    return payload.type
