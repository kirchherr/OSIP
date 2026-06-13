"""Safe model plug-in manifest registry.

The registry validates and tracks plug-in manifests. It does not import modules,
spawn processes, call network endpoints, or execute model code.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Any, Literal, Self

from omnisense_osip import ModelCapabilityDescriptor
from omnisense_osip.schemas import Identifier, OSIPModel, ProfileIdentifier, require_timezone
from pydantic import Field, field_validator, model_validator

type PluginRuntime = Literal[
    "simulation_stub",
    "python_callable",
    "external_process",
    "http_endpoint",
]
type PluginStatus = Literal["registered", "replaced"]


class ModelPluginManifest(OSIPModel):
    """Declarative contract for one model plug-in and its OSIP capability."""

    schema_version: Literal["model_plugin/0.1"] = "model_plugin/0.1"
    plugin_id: Identifier
    display_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    capability: ModelCapabilityDescriptor
    runtime: PluginRuntime = "simulation_stub"
    entrypoint: str | None = Field(default=None, min_length=1)
    application_profiles: tuple[ProfileIdentifier, ...] = Field(default_factory=tuple)
    requires_hardware: bool = False
    sandbox_required: bool = True
    license: str | None = Field(default=None, min_length=1)
    source_uri: str | None = Field(default=None, min_length=1)
    tags: tuple[str, ...] = Field(default_factory=tuple)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("entrypoint")
    @classmethod
    def validate_entrypoint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.strip() != value or any(char.isspace() for char in value):
            msg = "entrypoint must not contain whitespace"
            raise ValueError(msg)
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(dict.fromkeys(value))
        if any(not tag or tag.strip() != tag for tag in normalized):
            msg = "tags must be non-empty and must not contain surrounding whitespace"
            raise ValueError(msg)
        return normalized

    @model_validator(mode="after")
    def validate_manifest_contract(self) -> Self:
        if self.plugin_id != self.capability.model_id:
            msg = "plugin_id must match capability.model_id in model_plugin/0.1"
            raise ValueError(msg)
        if self.runtime != "simulation_stub" and self.entrypoint is None:
            msg = f"runtime '{self.runtime}' requires an entrypoint"
            raise ValueError(msg)
        if self.runtime == "simulation_stub" and self.requires_hardware:
            msg = "simulation_stub plug-ins must not require hardware"
            raise ValueError(msg)
        if self.requires_hardware and not self.sandbox_required:
            msg = "hardware-requiring plug-ins must keep sandbox_required=true"
            raise ValueError(msg)
        return self


class ModelPluginRegistration(OSIPModel):
    """Registry result for one manifest registration."""

    manifest: ModelPluginManifest
    registered_at: datetime
    status: PluginStatus

    @field_validator("registered_at")
    @classmethod
    def registered_at_has_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)


class ModelPluginRegistry:
    """In-memory registry for declarative model plug-in manifests."""

    def __init__(self, manifests: Iterable[ModelPluginManifest] = ()) -> None:
        self._manifests: dict[str, ModelPluginManifest] = {}
        self._registrations: dict[str, ModelPluginRegistration] = {}
        for manifest in manifests:
            self.register(manifest)

    def register(
        self,
        manifest: ModelPluginManifest | Mapping[str, Any],
        *,
        registered_at: datetime | None = None,
    ) -> ModelPluginRegistration:
        parsed = (
            ModelPluginManifest.model_validate(manifest)
            if isinstance(manifest, Mapping)
            else manifest
        )
        status: PluginStatus = "replaced" if parsed.plugin_id in self._manifests else "registered"
        timestamp = registered_at or datetime.now(UTC)
        require_timezone(timestamp)
        registration = ModelPluginRegistration(
            manifest=parsed,
            registered_at=timestamp,
            status=status,
        )
        self._manifests[parsed.plugin_id] = parsed
        self._registrations[parsed.plugin_id] = registration
        return registration

    def get(self, plugin_id: str) -> ModelPluginManifest | None:
        return self._manifests.get(plugin_id)

    def registration(self, plugin_id: str) -> ModelPluginRegistration | None:
        return self._registrations.get(plugin_id)

    def manifests(self, *, profile_id: str | None = None) -> tuple[ModelPluginManifest, ...]:
        manifests: tuple[ModelPluginManifest, ...] = tuple(self._manifests.values())
        if profile_id is not None:
            manifests = tuple(
                manifest
                for manifest in manifests
                if not manifest.application_profiles or profile_id in manifest.application_profiles
            )
        return tuple(sorted(manifests, key=lambda manifest: manifest.plugin_id))

    def capabilities(
        self,
        *,
        profile_id: str | None = None,
    ) -> tuple[ModelCapabilityDescriptor, ...]:
        return tuple(manifest.capability for manifest in self.manifests(profile_id=profile_id))

    def registrations(self) -> tuple[ModelPluginRegistration, ...]:
        return tuple(
            sorted(
                self._registrations.values(),
                key=lambda registration: registration.manifest.plugin_id,
            )
        )
