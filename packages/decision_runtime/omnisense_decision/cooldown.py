"""Cooldown state for bounded action proposals."""

from __future__ import annotations

from datetime import datetime

from omnisense_osip import ActionContract


class CooldownTracker:
    """Tracks the last proposal time per action id."""

    def __init__(self) -> None:
        self._last_seen: dict[str, datetime] = {}

    def is_blocked(self, contract: ActionContract, at: datetime) -> bool:
        return self.remaining_ms(contract, at) > 0

    def remaining_ms(self, contract: ActionContract, at: datetime) -> int:
        if contract.cooldown_ms == 0:
            return 0
        last_seen = self._last_seen.get(contract.action_id)
        if last_seen is None:
            return 0
        elapsed_ms = int((at - last_seen).total_seconds() * 1000)
        return max(contract.cooldown_ms - elapsed_ms, 0)

    def mark(self, contract: ActionContract, at: datetime) -> None:
        self._last_seen[contract.action_id] = at
