"""Stable JSON serialization for OSIP messages."""

from __future__ import annotations

from omnisense_osip.validation import OSIPMessage, parse_osip_json


def to_json(message: OSIPMessage) -> str:
    return message.model_dump_json(exclude_none=True)


def from_json(payload: str | bytes | bytearray) -> OSIPMessage:
    return parse_osip_json(payload)
