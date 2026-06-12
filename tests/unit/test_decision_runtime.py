from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from omnisense_bus import InMemoryBus, action_command_filter, action_proposals_topic
from omnisense_decision import (
    ActionCommandExecutorStub,
    ActionContractRegistry,
    DecisionRuntime,
    default_rooms_contracts,
)
from omnisense_osip import ActionProposal
from omnisense_osip.schemas import ContextEvent, ContextUpdate, GlobalRisk


def context_with_event(
    label: str,
    *,
    confidence: float = 0.84,
    timestamp: datetime | None = None,
    context_id: str = "ctx_test_001",
) -> ContextUpdate:
    return ContextUpdate(
        context_id=context_id,
        timestamp=timestamp or datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        time_window_ms=250,
        room="kitchen",
        events=[
            ContextEvent(
                label=label,
                confidence=confidence,
                urgency=0.82,
                evidence=["sensor.test_evidence"],
                contradictions=[],
            )
        ],
        global_risk=GlobalRisk(safety=0.8, comfort=0.3, maintenance=0.1),
    )


async def test_decision_runtime_publishes_burning_food_warning_and_ventilation() -> None:
    bus = InMemoryBus()
    runtime = DecisionRuntime(
        bus,
        facts={"notification.available": True, "hvac.available": True},
    )
    context = context_with_event("context.possible_burning_food", confidence=0.82)

    async with bus.subscribe(action_proposals_topic()) as subscription:
        outcome = await runtime.evaluate(context)
        delivered = [
            await asyncio.wait_for(subscription.receive(), timeout=1),
            await asyncio.wait_for(subscription.receive(), timeout=1),
        ]

    action_ids = [proposal.action_id for proposal in outcome.proposals]
    assert action_ids == ["action.notify.local", "action.hvac.ventilation_boost"]
    assert [message.payload for message in delivered] == list(outcome.proposals)
    assert all(isinstance(message.payload, ActionProposal) for message in delivered)


async def test_decision_runtime_blocks_missing_preconditions() -> None:
    bus = InMemoryBus()
    runtime = DecisionRuntime(bus, facts={"notification.available": True})
    context = context_with_event("context.possible_burning_food", confidence=0.82)

    outcome = await runtime.evaluate(context)

    assert [proposal.action_id for proposal in outcome.proposals] == ["action.notify.local"]
    assert [(block.action_id, block.reason) for block in outcome.blocks] == [
        (
            "action.hvac.ventilation_boost",
            "preconditions not satisfied: hvac.available == true",
        )
    ]


async def test_decision_runtime_blocks_low_confidence() -> None:
    bus = InMemoryBus()
    runtime = DecisionRuntime(bus, facts={"speaker.available": True})
    context = context_with_event("context.possible_fall", confidence=0.5)

    outcome = await runtime.evaluate(context)

    assert outcome.proposals == ()
    assert outcome.blocks[0].action_id == "action.room.speaker.ask_help_needed"
    assert "confidence 0.50 below minimum 0.74" in outcome.blocks[0].reason


async def test_decision_runtime_cooldown_prevents_repeated_proposals() -> None:
    bus = InMemoryBus()
    runtime = DecisionRuntime(bus, facts={"speaker.available": True})
    first = context_with_event("context.possible_fall", confidence=0.82)
    second = context_with_event(
        "context.possible_fall",
        confidence=0.82,
        timestamp=first.timestamp + timedelta(seconds=1),
        context_id="ctx_test_002",
    )

    first_outcome = await runtime.evaluate(first)
    second_outcome = await runtime.evaluate(second)

    assert [proposal.action_id for proposal in first_outcome.proposals] == [
        "action.room.speaker.ask_help_needed"
    ]
    assert second_outcome.proposals == ()
    assert "cooldown active" in second_outcome.blocks[0].reason


async def test_command_executor_stub_publishes_bounded_command() -> None:
    bus = InMemoryBus()
    registry = ActionContractRegistry(default_rooms_contracts())
    contract = registry.get("action.hvac.ventilation_boost")
    runtime = DecisionRuntime(bus, registry=registry, facts={"hvac.available": True})
    context = context_with_event("context.high_occupancy_stale_air", confidence=0.78)
    proposal = (await runtime.evaluate(context)).proposals[0]

    async with bus.subscribe(action_command_filter()) as subscription:
        command = await ActionCommandExecutorStub(bus).dispatch(
            proposal,
            contract,
            parameters={"room": context.room},
        )
        delivered = await asyncio.wait_for(subscription.receive(), timeout=1)

    assert delivered.payload == command
    assert command.target == contract.target
    assert command.operation == contract.operation
    assert command.parameters == {"room": "kitchen"}
    assert command.idempotency_key == f"{context.context_id}:{contract.action_id}"
