"""Registry for application-profile decision policies and contracts."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Self

from omnisense_osip import ActionContract

from omnisense_decision.interfaces import DecisionPolicy


@dataclass(frozen=True, slots=True)
class DecisionProfile:
    """Decision policy plus default Action Contracts for one application profile."""

    profile_id: str
    policy: DecisionPolicy
    contracts: Sequence[ActionContract]


class UnknownDecisionProfileError(LookupError):
    """Raised when no decision profile is registered for an application profile."""

    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        super().__init__(f"unknown application profile for decision runtime: {profile_id}")


class DecisionProfileRegistry:
    """Maps application profile ids to decision policies and contract bundles."""

    def __init__(self, profiles: Iterable[DecisionProfile] | None = None) -> None:
        self._profiles: dict[str, DecisionProfile] = {}
        if profiles is None:
            return
        for profile in profiles:
            self.register(profile)

    @classmethod
    def with_defaults(cls) -> Self:
        """Build the default registry with the reference rooms decision profile."""

        from omnisense_profiles.rooms.decision import rooms_decision_profile

        return cls([rooms_decision_profile()])

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))

    def register(self, profile: DecisionProfile) -> None:
        profile_id = profile.profile_id.strip()
        if not profile_id:
            raise ValueError("decision profile_id must not be empty")
        if profile_id in self._profiles:
            raise ValueError(f"decision profile already registered: {profile_id}")
        self._profiles[profile_id] = profile

    def get(self, profile_id: str) -> DecisionProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise UnknownDecisionProfileError(profile_id) from exc
