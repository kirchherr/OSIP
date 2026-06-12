"""Rooms Application Profile bundle."""

from __future__ import annotations

from dataclasses import dataclass, field

from omnisense_context.interfaces import ContextFusion
from omnisense_decision.profiles import DecisionProfile

from omnisense_profiles.interfaces import ApplicationProfileMetadata
from omnisense_profiles.rooms.context_fusion import RoomsFusion
from omnisense_profiles.rooms.decision import rooms_decision_profile

ROOMS_PROFILE_METADATA = ApplicationProfileMetadata(
    profile_id="rooms",
    display_name="Rooms",
    version="0.1",
    domain="Smart rooms and ambient sensing",
    description=(
        "Reference Application Profile for intelligent rooms, smart buildings, "
        "ambient sensing, comfort, safety, and maintenance workflows."
    ),
    standards=(
        "W3C WoT",
        "W3C/OGC SOSA/SSN",
        "Brick Schema",
        "OpenAPI",
        "AsyncAPI",
    ),
    requires_hardware=False,
)


@dataclass(frozen=True, slots=True)
class RoomsApplicationProfile:
    """Bundled runtime extension for the rooms reference profile."""

    profile_id: str = "rooms"
    metadata: ApplicationProfileMetadata = ROOMS_PROFILE_METADATA
    context_fusion: ContextFusion = field(default_factory=RoomsFusion)
    decision_profile: DecisionProfile = field(default_factory=rooms_decision_profile)
