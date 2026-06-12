"""Action contract registry."""

from __future__ import annotations

from collections.abc import Iterable

from omnisense_osip import ActionContract


class DuplicateActionContractError(ValueError):
    """Raised when the same action_id is registered twice."""


class UnknownActionContractError(KeyError):
    """Raised when a contract lookup cannot be satisfied."""


class ActionContractRegistry:
    """In-memory action contract registry for deterministic decision tests."""

    def __init__(self, contracts: Iterable[ActionContract] = ()) -> None:
        self._contracts: dict[str, ActionContract] = {}
        for contract in contracts:
            self.register(contract)

    def register(self, contract: ActionContract) -> None:
        if contract.action_id in self._contracts:
            msg = f"action contract '{contract.action_id}' is already registered"
            raise DuplicateActionContractError(msg)
        self._contracts[contract.action_id] = contract

    def get(self, action_id: str) -> ActionContract:
        try:
            return self._contracts[action_id]
        except KeyError as exc:
            msg = f"action contract '{action_id}' is not registered"
            raise UnknownActionContractError(msg) from exc

    def matching_context(self, context_label: str) -> list[ActionContract]:
        return [
            contract
            for contract in self._contracts.values()
            if context_label in contract.allowed_contexts
        ]

    def all(self) -> list[ActionContract]:
        return sorted(self._contracts.values(), key=lambda contract: contract.action_id)
