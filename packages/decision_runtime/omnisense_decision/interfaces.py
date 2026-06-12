"""Decision policy interfaces owned by the OSIP decision runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from omnisense_osip import ActionContract
from omnisense_osip.schemas import ActionPriority, ContextEvent, ContextUpdate

from omnisense_decision.contracts import ActionContractRegistry


@dataclass(frozen=True, slots=True)
class ContractMatch:
    """One context event matched to one candidate contract."""

    event: ContextEvent
    contract: ActionContract


class DecisionPolicy(Protocol):
    """Application-profile policy for ranking bounded action proposals."""

    profile_id: str

    def matches(
        self,
        context: ContextUpdate,
        registry: ActionContractRegistry,
    ) -> list[ContractMatch]:
        """Return candidate contracts for the active context."""

    def priority(self, event: ContextEvent, contract: ActionContract) -> ActionPriority:
        """Assign an OSIP action priority to a candidate contract."""

    def requires_confirmation(self, contract: ActionContract) -> bool:
        """Return whether a candidate action needs human confirmation."""

    def reason(self, event: ContextEvent, contract: ActionContract) -> str:
        """Explain why a proposal was generated."""
