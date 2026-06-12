"""Compatibility imports for rooms-profile decision policy and contracts."""

from omnisense_profiles.rooms.decision import (
    RoomsDecisionPolicy,
    default_rooms_contracts,
    rooms_decision_profile,
)

from omnisense_decision.interfaces import ContractMatch

__all__ = [
    "ContractMatch",
    "RoomsDecisionPolicy",
    "default_rooms_contracts",
    "rooms_decision_profile",
]
