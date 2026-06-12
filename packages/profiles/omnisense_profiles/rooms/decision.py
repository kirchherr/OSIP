"""Rooms-profile decision policy and default contracts."""

from __future__ import annotations

from omnisense_decision.contracts import ActionContractRegistry
from omnisense_decision.interfaces import ContractMatch
from omnisense_decision.profiles import DecisionProfile
from omnisense_osip import ActionContract
from omnisense_osip.schemas import ActionPriority, ContextEvent, ContextUpdate


class RoomsDecisionPolicy:
    """Deterministic profile policy for the first rooms scenarios."""

    profile_id = "rooms"

    def matches(
        self,
        context: ContextUpdate,
        registry: ActionContractRegistry,
    ) -> list[ContractMatch]:
        matches: list[ContractMatch] = []
        for event in context.events:
            for contract in registry.matching_context(event.label):
                matches.append(ContractMatch(event=event, contract=contract))
        return matches

    def priority(self, event: ContextEvent, contract: ActionContract) -> ActionPriority:
        if contract.risk_class == "critical" or event.urgency >= 0.95:
            return "critical"
        if contract.risk_class == "high" or event.urgency >= 0.75:
            return "high"
        if contract.risk_class == "medium" or event.urgency >= 0.5:
            return "normal"
        return "low"

    def requires_confirmation(self, contract: ActionContract) -> bool:
        return contract.risk_class in {"high", "critical"}

    def reason(self, event: ContextEvent, contract: ActionContract) -> str:
        return f"{event.label} matched {contract.action_id} with confidence {event.confidence:.2f}."


def default_rooms_contracts() -> list[ActionContract]:
    """Contracts needed by the rooms MVP scenarios."""

    return [
        ActionContract(
            action_id="action.notify.local",
            target="notification.local",
            operation="notify.warn",
            risk_class="low",
            allowed_contexts=["context.possible_burning_food"],
            preconditions=["notification.available == true"],
            min_confidence=0.72,
            max_decision_latency_ms=250,
            cooldown_ms=30_000,
            safe_state="notification.silent",
            idempotent=True,
        ),
        ActionContract(
            action_id="action.hvac.ventilation_boost",
            target="hvac.room",
            operation="ventilation.boost",
            risk_class="low",
            allowed_contexts=[
                "context.possible_burning_food",
                "context.high_occupancy_stale_air",
            ],
            preconditions=["hvac.available == true"],
            min_confidence=0.70,
            max_decision_latency_ms=250,
            cooldown_ms=30_000,
            rollback="hvac.ventilation_normal",
            idempotent=True,
        ),
        ActionContract(
            action_id="action.room.speaker.ask_help_needed",
            target="speaker.room",
            operation="speaker.ask_help",
            risk_class="low",
            allowed_contexts=["context.possible_fall"],
            preconditions=["speaker.available == true"],
            min_confidence=0.74,
            max_decision_latency_ms=250,
            cooldown_ms=10_000,
            safe_state="speaker.silent",
            idempotent=True,
        ),
    ]


def rooms_decision_profile() -> DecisionProfile:
    """Return the default decision profile for the rooms MVP."""

    return DecisionProfile(
        profile_id="rooms",
        policy=RoomsDecisionPolicy(),
        contracts=tuple(default_rooms_contracts()),
    )
