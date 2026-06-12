"""Registry for OSIP Application Profiles."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self

from omnisense_context.interfaces import ContextFusion
from omnisense_decision.profiles import DecisionProfile

from omnisense_profiles.interfaces import ApplicationProfile


class UnknownApplicationProfileIdError(LookupError):
    """Raised when no Application Profile is registered for a profile id."""

    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        super().__init__(f"unknown application profile: {profile_id}")


class ApplicationProfileRegistry:
    """Maps application profile ids to bundled profile implementations."""

    def __init__(self, profiles: Iterable[ApplicationProfile] | None = None) -> None:
        self._profiles: dict[str, ApplicationProfile] = {}
        if profiles is None:
            return
        for profile in profiles:
            self.register(profile)

    @classmethod
    def with_defaults(cls) -> Self:
        """Build the default registry with the reference rooms profile."""

        from omnisense_profiles.rooms.profile import RoomsApplicationProfile

        return cls([RoomsApplicationProfile()])

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))

    def register(self, profile: ApplicationProfile) -> None:
        profile_id = profile.profile_id.strip()
        if not profile_id:
            raise ValueError("application profile_id must not be empty")
        if profile.metadata.profile_id != profile_id:
            msg = (
                "application profile metadata.profile_id must match "
                f"profile_id: {profile.metadata.profile_id} != {profile_id}"
            )
            raise ValueError(msg)
        if profile.context_fusion.profile_id != profile_id:
            msg = (
                "application profile context_fusion.profile_id must match "
                f"profile_id: {profile.context_fusion.profile_id} != {profile_id}"
            )
            raise ValueError(msg)
        if profile.decision_profile.profile_id != profile_id:
            msg = (
                "application profile decision_profile.profile_id must match "
                f"profile_id: {profile.decision_profile.profile_id} != {profile_id}"
            )
            raise ValueError(msg)
        if profile_id in self._profiles:
            raise ValueError(f"application profile already registered: {profile_id}")
        self._profiles[profile_id] = profile

    def get(self, profile_id: str) -> ApplicationProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise UnknownApplicationProfileIdError(profile_id) from exc

    def all(self) -> tuple[ApplicationProfile, ...]:
        return tuple(self._profiles[profile_id] for profile_id in self.profile_ids)

    def context_fusions(self) -> tuple[ContextFusion, ...]:
        return tuple(profile.context_fusion for profile in self.all())

    def decision_profiles(self) -> tuple[DecisionProfile, ...]:
        return tuple(profile.decision_profile for profile in self.all())
