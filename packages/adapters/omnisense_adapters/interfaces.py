"""Public adapter contracts for OSIP edge integrations."""

from __future__ import annotations

from typing import Literal, Protocol

from omnisense_bus import AsyncMessageBus
from pydantic import BaseModel, ConfigDict, Field

type AdapterRole = Literal["source", "sink", "bridge"]


class AdapterMetadata(BaseModel):
    """Stable metadata every OSIP adapter should expose."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    adapter_id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_.-]*$")
    role: AdapterRole
    supported_message_types: tuple[str, ...] = Field(min_length=1)
    profile_id: str | None = Field(default=None, min_length=1)
    requires_hardware: bool = False
    description: str | None = Field(default=None, min_length=1)


class AdapterRunResult(BaseModel):
    """Machine-readable result for deterministic adapter runs."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    adapter_id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_.-]*$")
    published_count: int = Field(ge=0)
    topics: tuple[str, ...] = ()
    message_types: tuple[str, ...] = ()


class OSIPSourceAdapter(Protocol):
    """Source adapter that validates OSIP payloads and publishes them to a bus."""

    @property
    def metadata(self) -> AdapterMetadata: ...

    async def publish_to(self, bus: AsyncMessageBus) -> AdapterRunResult: ...
