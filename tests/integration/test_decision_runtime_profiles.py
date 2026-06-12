from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from omnisense_bus import InMemoryBus, action_proposals_topic
from omnisense_decision import (
    ActionContractRegistry,
    ContractMatch,
    DecisionProfile,
    DecisionProfileRegistry,
    DecisionRuntime,
    UnknownDecisionProfileError,
)
from omnisense_osip import ActionContract, ActionProposal
from omnisense_osip.schemas import ActionPriority, ContextEvent, ContextUpdate, GlobalRisk


class ProfileTestDecisionPolicy:
    profile_id = "xxx"

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
        return "normal"

    def requires_confirmation(self, contract: ActionContract) -> bool:
        return False

    def reason(self, event: ContextEvent, contract: ActionContract) -> str:
        return f"{event.label} accepted by profile {self.profile_id}."


def profile_test_contract() -> ActionContract:
    return ActionContract(
        action_id="action.profile.test",
        target="profile.test_target",
        operation="profile.test_operation",
        risk_class="low",
        allowed_contexts=["context.profile_test"],
        preconditions=["profile.available == true"],
        min_confidence=0.8,
        max_decision_latency_ms=100,
        cooldown_ms=0,
        safe_state="profile.safe_state",
        idempotent=True,
    )


def profile_test_context() -> ContextUpdate:
    return ContextUpdate(
        context_id="ctx_profile_test",
        timestamp=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        time_window_ms=100,
        room="lab",
        events=[
            ContextEvent(
                label="context.profile_test",
                confidence=0.9,
                urgency=0.4,
                evidence=["profile.input"],
                contradictions=[],
            )
        ],
        global_risk=GlobalRisk(safety=0.0, comfort=0.0, maintenance=0.0),
    )


async def test_decision_runtime_uses_registered_application_profile() -> None:
    bus = InMemoryBus()
    runtime = DecisionRuntime(
        bus,
        application_profile="xxx",
        profile_registry=DecisionProfileRegistry(
            [
                DecisionProfile(
                    profile_id="xxx",
                    policy=ProfileTestDecisionPolicy(),
                    contracts=(profile_test_contract(),),
                )
            ]
        ),
        facts={"profile.available": True},
    )

    async with bus.subscribe(action_proposals_topic()) as subscription:
        outcome = await runtime.evaluate(profile_test_context())
        delivered = await asyncio.wait_for(subscription.receive(), timeout=1)

    assert runtime.application_profile == "xxx"
    assert [proposal.action_id for proposal in outcome.proposals] == ["action.profile.test"]
    assert isinstance(delivered.payload, ActionProposal)
    assert delivered.payload == outcome.proposals[0]
    assert delivered.payload.reason == "context.profile_test accepted by profile xxx."


def test_decision_runtime_rejects_unregistered_application_profile() -> None:
    with pytest.raises(UnknownDecisionProfileError) as error:
        DecisionRuntime(
            InMemoryBus(),
            application_profile="physical-ai",
            profile_registry=DecisionProfileRegistry(),
        )

    assert error.value.profile_id == "physical-ai"
