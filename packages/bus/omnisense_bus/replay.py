"""JSONL trace replay helpers for bus-level tests and simulations."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from omnisense_bus.interfaces import AsyncMessageBus
from omnisense_bus.messages import BusMessage
from omnisense_bus.topics import ensure_valid_topic


@dataclass(frozen=True, slots=True)
class ReplayRecord:
    topic: str
    payload: Any


def load_jsonl_trace(path: Path) -> list[ReplayRecord]:
    records: list[ReplayRecord] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        decoded = json.loads(stripped)
        if not isinstance(decoded, dict):
            msg = f"{path}:{line_number} must contain a JSON object"
            raise ValueError(msg)
        topic = decoded.get("topic")
        if not isinstance(topic, str):
            msg = f"{path}:{line_number} requires a string topic"
            raise ValueError(msg)
        if "payload" not in decoded:
            msg = f"{path}:{line_number} requires a payload"
            raise ValueError(msg)
        ensure_valid_topic(topic)
        records.append(ReplayRecord(topic=topic, payload=decoded["payload"]))
    return records


async def replay_jsonl(
    bus: AsyncMessageBus,
    path: Path,
    *,
    payload_parser: Callable[[Mapping[str, Any]], Any] | None = None,
) -> list[BusMessage[Any]]:
    published: list[BusMessage[Any]] = []
    for record in load_jsonl_trace(path):
        payload = record.payload
        if payload_parser is not None:
            if not isinstance(payload, Mapping):
                msg = f"payload for topic '{record.topic}' must be an object when parser is used"
                raise ValueError(msg)
            payload = payload_parser(payload)
        published.append(await bus.publish(record.topic, payload))
    return published
