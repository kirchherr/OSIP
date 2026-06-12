"""Registry for application-profile context fusion implementations."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self

from omnisense_context.interfaces import ContextFusion


class UnknownApplicationProfileError(LookupError):
    """Raised when no context fusion is registered for an application profile."""

    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        super().__init__(f"unknown application profile for context fusion: {profile_id}")


class ContextFusionRegistry:
    """Maps application profile ids to context fusion implementations."""

    def __init__(self, fusions: Iterable[ContextFusion] | None = None) -> None:
        self._fusions: dict[str, ContextFusion] = {}
        if fusions is None:
            return
        for fusion in fusions:
            self.register(fusion)

    @classmethod
    def with_defaults(cls) -> Self:
        """Build the default registry with the reference rooms profile."""

        from omnisense_profiles.rooms import RoomsFusion

        return cls([RoomsFusion()])

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._fusions))

    def register(self, fusion: ContextFusion) -> None:
        profile_id = fusion.profile_id.strip()
        if not profile_id:
            raise ValueError("context fusion profile_id must not be empty")
        if profile_id in self._fusions:
            raise ValueError(f"context fusion already registered for profile: {profile_id}")
        self._fusions[profile_id] = fusion

    def get(self, profile_id: str) -> ContextFusion:
        try:
            return self._fusions[profile_id]
        except KeyError as exc:
            raise UnknownApplicationProfileError(profile_id) from exc
