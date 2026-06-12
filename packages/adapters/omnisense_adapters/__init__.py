"""Adapter contracts and hardware-free reference adapters for OSIP."""

from omnisense_adapters.interfaces import (
    AdapterMetadata,
    AdapterRole,
    AdapterRunResult,
    OSIPSourceAdapter,
)
from omnisense_adapters.jsonl import DEFAULT_ALLOWED_MESSAGE_TYPES, JSONLOSIPSourceAdapter

__all__ = [
    "DEFAULT_ALLOWED_MESSAGE_TYPES",
    "AdapterMetadata",
    "AdapterRole",
    "AdapterRunResult",
    "JSONLOSIPSourceAdapter",
    "OSIPSourceAdapter",
]
