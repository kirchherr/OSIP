"""Decision runtime orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from omnisense_bus import AsyncMessageBus, action_proposals_topic
from omnisense_osip import ActionProposal, ContextUpdate

from omnisense_decision.contracts import ActionContractRegistry
from omnisense_decision.cooldown import CooldownTracker
from omnisense_decision.interfaces import ContractMatch, DecisionPolicy
from omnisense_decision.preconditions import PreconditionsEvaluator, ScalarFact
from omnisense_decision.profiles import DecisionProfileRegistry


@dataclass(frozen=True, slots=True)
class DecisionBlock:
    """Explains why a candidate action did not become a proposal."""

    context_id: str
    action_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class DecisionOutcome:
    """Decision runtime result for one context update."""

    proposals: tuple[ActionProposal, ...]
    blocks: tuple[DecisionBlock, ...]


class DecisionRuntime:
    """Creates bounded action proposals from context updates."""

    def __init__(
        self,
        bus: AsyncMessageBus,
        *,
        application_profile: str = "rooms",
        registry: ActionContractRegistry | None = None,
        profile_registry: DecisionProfileRegistry | None = None,
        preconditions: PreconditionsEvaluator | None = None,
        cooldowns: CooldownTracker | None = None,
        policy: DecisionPolicy | None = None,
        facts: Mapping[str, ScalarFact] | None = None,
    ) -> None:
        self._bus = bus
        decision_profile = (
            (profile_registry or DecisionProfileRegistry.with_defaults()).get(application_profile)
            if registry is None or policy is None
            else None
        )
        if registry is None:
            if decision_profile is None:
                msg = "decision profile is required when no action contract registry is provided"
                raise ValueError(msg)
            self._registry = ActionContractRegistry(decision_profile.contracts)
        else:
            self._registry = registry
        if policy is None:
            if decision_profile is None:
                msg = "decision profile is required when no decision policy is provided"
                raise ValueError(msg)
            self._policy = decision_profile.policy
        else:
            self._policy = policy
        self._preconditions = preconditions or PreconditionsEvaluator()
        self._cooldowns = cooldowns or CooldownTracker()
        self._application_profile = self._policy.profile_id
        self._facts: dict[str, ScalarFact] = dict(facts or {})
        self._proposal_counter = 0

    @property
    def application_profile(self) -> str:
        return self._application_profile

    async def evaluate(
        self,
        context: ContextUpdate,
        *,
        facts: Mapping[str, ScalarFact] | None = None,
    ) -> DecisionOutcome:
        runtime_facts = self._merged_facts(facts)
        proposals: list[ActionProposal] = []
        blocks: list[DecisionBlock] = []

        for match in self._policy.matches(context, self._registry):
            contract = match.contract
            event = match.event

            if event.confidence < contract.min_confidence:
                blocks.append(
                    DecisionBlock(
                        context_id=context.context_id,
                        action_id=contract.action_id,
                        reason=(
                            f"confidence {event.confidence:.2f} below "
                            f"minimum {contract.min_confidence:.2f}"
                        ),
                    )
                )
                continue

            precondition_result = self._preconditions.evaluate(contract, runtime_facts)
            if not precondition_result.satisfied:
                detail = ", ".join(precondition_result.failed + precondition_result.unsupported)
                blocks.append(
                    DecisionBlock(
                        context_id=context.context_id,
                        action_id=contract.action_id,
                        reason=f"preconditions not satisfied: {detail}",
                    )
                )
                continue

            remaining_ms = self._cooldowns.remaining_ms(contract, context.timestamp)
            if remaining_ms > 0:
                blocks.append(
                    DecisionBlock(
                        context_id=context.context_id,
                        action_id=contract.action_id,
                        reason=f"cooldown active for {remaining_ms}ms",
                    )
                )
                continue

            proposal = self._proposal_for(context, event_confidence=event.confidence, match=match)
            await self._bus.publish(action_proposals_topic(), proposal)
            self._cooldowns.mark(contract, context.timestamp)
            proposals.append(proposal)

        return DecisionOutcome(proposals=tuple(proposals), blocks=tuple(blocks))

    def _merged_facts(
        self,
        facts: Mapping[str, ScalarFact] | None,
    ) -> dict[str, ScalarFact]:
        if facts is None:
            return dict(self._facts)
        merged = dict(self._facts)
        merged.update(facts)
        return merged

    def _proposal_for(
        self,
        context: ContextUpdate,
        *,
        event_confidence: float,
        match: ContractMatch,
    ) -> ActionProposal:
        contract = match.contract
        event = match.event
        self._proposal_counter += 1
        return ActionProposal(
            proposal_id=f"actprop_{self._proposal_counter:06d}",
            based_on_context=context.context_id,
            action_id=contract.action_id,
            priority=self._policy.priority(event, contract),
            confidence=round(event_confidence, 3),
            deadline_ms=contract.max_decision_latency_ms,
            reason=self._policy.reason(event, contract),
            requires_confirmation=self._policy.requires_confirmation(contract),
        )
