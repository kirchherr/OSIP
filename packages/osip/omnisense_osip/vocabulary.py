"""Initial OSIP v0.1 vocabulary anchors.

These names are intentionally lightweight. Richer WoT, SOSA/SSN, Brick, or
domain-specific mappings can live in adapter layers without changing OSIP core
payloads.
"""

from __future__ import annotations

from typing import Final

CORE_MESSAGE_TYPES: Final[frozenset[str]] = frozenset(
    {
        "model.capability",
        "percept.packet",
        "context.update",
        "event.detected",
        "action.contract",
        "action.proposal",
        "action.command",
        "action.result",
    }
)

CLAIM_LABEL_EXAMPLES: Final[frozenset[str]] = frozenset(
    {
        "audio.impact_sound",
        "audio.human_shout",
        "person.presence",
        "person.pose",
        "event.fall_candidate",
        "event.possible_burning_food",
        "environment.air.co2_high",
        "radar.motion_drop",
        "tactile.floor_pressure_spike",
    }
)

CONTEXT_LABEL_EXAMPLES: Final[frozenset[str]] = frozenset(
    {
        "context.bad_air",
        "context.high_occupancy_stale_air",
        "context.possible_burning_food",
        "context.possible_fall",
        "context.possible_smoke_low_risk",
    }
)

ACTION_LABEL_EXAMPLES: Final[frozenset[str]] = frozenset(
    {
        "hvac.ventilation_boost",
        "hvac.ventilation_normal",
        "room.speaker.ask_help_needed",
        "room.speaker.speak",
        "notification.caregiver.alert",
    }
)
