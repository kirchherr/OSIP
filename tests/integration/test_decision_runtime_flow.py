from __future__ import annotations

import asyncio
from pathlib import Path

from omnisense_bus import InMemoryBus, action_proposals_topic
from omnisense_context import ContextEngine
from omnisense_decision import DecisionRuntime
from omnisense_sim import ReplayRunner, ScenarioLoader

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"
DEFAULT_FACTS = {
    "hvac.available": True,
    "notification.available": True,
    "speaker.available": True,
}


async def proposals_for_scenario(scenario_name: str) -> list[str]:
    bus = InMemoryBus()
    context_engine = ContextEngine(bus)
    decision_runtime = DecisionRuntime(bus, facts=DEFAULT_FACTS)
    scenario = ScenarioLoader().load(SCENARIO_DIR / scenario_name)

    async with bus.subscribe(action_proposals_topic()) as proposals_subscription:
        replay = await ReplayRunner(bus).run(scenario)
        proposed_actions: list[str] = []
        for published in replay.published_percepts:
            context = await context_engine.ingest(published.message.payload)
            outcome = await decision_runtime.evaluate(context)
            for _proposal in outcome.proposals:
                message = await asyncio.wait_for(proposals_subscription.receive(), timeout=1)
                proposed_actions.append(message.payload.action_id)

    return proposed_actions


async def test_decision_runtime_emits_expected_actions_for_rooms_scenarios() -> None:
    expectations = {
        "kitchen_burning_food.yaml": [
            "action.notify.local",
            "action.hvac.ventilation_boost",
        ],
        "fall_candidate.yaml": ["action.room.speaker.ask_help_needed"],
        "stale_air_high_occupancy.yaml": ["action.hvac.ventilation_boost"],
    }

    for scenario_name, expected_actions in expectations.items():
        proposed_actions = await proposals_for_scenario(scenario_name)
        assert proposed_actions == expected_actions


async def test_decision_runtime_emits_no_actions_for_normal_cooking() -> None:
    assert await proposals_for_scenario("normal_cooking_no_alarm.yaml") == []
