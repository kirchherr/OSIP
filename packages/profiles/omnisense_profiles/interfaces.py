"""Application Profile interfaces for OmniSense Runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from omnisense_context.interfaces import ContextFusion
from omnisense_decision.profiles import DecisionProfile


@dataclass(frozen=True, slots=True)
class ApplicationProfileMetadata:
    """Human- and machine-readable metadata for one OSIP Application Profile."""

    profile_id: str
    display_name: str
    version: str
    domain: str
    description: str
    standards: tuple[str, ...] = field(default_factory=tuple)
    requires_hardware: bool = False


class ApplicationProfile(Protocol):
    """Bundle of profile-owned runtime extensions and metadata."""

    @property
    def profile_id(self) -> str:
        """Stable Application Profile id such as ``rooms`` or ``physical-ai``."""

    @property
    def metadata(self) -> ApplicationProfileMetadata:
        """Profile metadata for docs, registries, and public inspection."""

    @property
    def context_fusion(self) -> ContextFusion:
        """Profile-specific Context Engine fusion implementation."""

    @property
    def decision_profile(self) -> DecisionProfile:
        """Profile-specific Decision Runtime policy and contract bundle."""
