"""Scenario benchmark runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from omnisense_bus import InMemoryBus
from omnisense_context import ContextEngine
from omnisense_decision import DecisionRuntime
from omnisense_osip import ContextUpdate
from omnisense_sim import ReplayRunner, ScenarioDefinition, ScenarioLoader

from omnisense_benchmarks.metrics import PercentileSummary, percentile_summary

DEFAULT_BENCHMARK_FACTS = {
    "hvac.available": True,
    "notification.available": True,
    "speaker.available": True,
}


@dataclass(frozen=True, slots=True)
class ScenarioBenchmarkResult:
    scenario_id: str
    scenario_name: str
    application_profile: str
    room: str
    percept_count: int
    expected_contexts: tuple[str, ...]
    detected_contexts: tuple[str, ...]
    missing_contexts: tuple[str, ...]
    unexpected_contexts: tuple[str, ...]
    expected_actions: tuple[str, ...]
    proposed_actions: tuple[str, ...]
    missing_actions: tuple[str, ...]
    unexpected_actions: tuple[str, ...]
    first_context_latency_ms: int | None
    first_action_proposal_latency_ms: int | None
    context_latency_budget_ms: int | None
    action_latency_budget_ms: int | None
    context_latency_budget_passed: bool | None
    action_latency_budget_passed: bool | None
    action_contract_blocks: int

    @property
    def passed(self) -> bool:
        return (
            not self.missing_contexts
            and not self.unexpected_contexts
            and not self.missing_actions
            and not self.unexpected_actions
            and self.context_latency_budget_passed is not False
            and self.action_latency_budget_passed is not False
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "application_profile": self.application_profile,
            "room": self.room,
            "percept_count": self.percept_count,
            "expected_contexts": list(self.expected_contexts),
            "detected_contexts": list(self.detected_contexts),
            "missing_contexts": list(self.missing_contexts),
            "unexpected_contexts": list(self.unexpected_contexts),
            "expected_actions": list(self.expected_actions),
            "proposed_actions": list(self.proposed_actions),
            "missing_actions": list(self.missing_actions),
            "unexpected_actions": list(self.unexpected_actions),
            "first_context_latency_ms": self.first_context_latency_ms,
            "first_action_proposal_latency_ms": self.first_action_proposal_latency_ms,
            "context_latency_budget_ms": self.context_latency_budget_ms,
            "action_latency_budget_ms": self.action_latency_budget_ms,
            "context_latency_budget_passed": self.context_latency_budget_passed,
            "action_latency_budget_passed": self.action_latency_budget_passed,
            "action_contract_blocks": self.action_contract_blocks,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSummary:
    scenario_count: int
    passed_scenarios: int
    failed_scenarios: int
    context_latency: PercentileSummary
    action_proposal_latency: PercentileSummary
    false_positive_contexts: int
    false_negative_contexts: int
    false_positive_actions: int
    false_negative_actions: int
    action_contract_blocks: int

    def as_dict(self) -> dict[str, object]:
        return {
            "scenario_count": self.scenario_count,
            "passed_scenarios": self.passed_scenarios,
            "failed_scenarios": self.failed_scenarios,
            "context_latency": self.context_latency.as_dict(),
            "action_proposal_latency": self.action_proposal_latency.as_dict(),
            "false_positive_contexts": self.false_positive_contexts,
            "false_negative_contexts": self.false_negative_contexts,
            "false_positive_actions": self.false_positive_actions,
            "false_negative_actions": self.false_negative_actions,
            "action_contract_blocks": self.action_contract_blocks,
        }


@dataclass(frozen=True, slots=True)
class SuiteBenchmarkResult:
    summary: BenchmarkSummary
    scenarios: tuple[ScenarioBenchmarkResult, ...]

    @property
    def passed(self) -> bool:
        return self.summary.failed_scenarios == 0

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "summary": self.summary.as_dict(),
            "scenarios": [scenario.as_dict() for scenario in self.scenarios],
        }


class ScenarioBenchmarkRunner:
    """Runs deterministic OSIP scenarios through context and decision stages."""

    def __init__(self, scenario_dir: Path) -> None:
        self._scenario_dir = scenario_dir
        self._loader = ScenarioLoader()

    async def run_suite(self, scenario_names: list[str] | None = None) -> SuiteBenchmarkResult:
        names = scenario_names or sorted(path.name for path in self._scenario_dir.glob("*.yaml"))
        scenarios = [await self.run_scenario(self._scenario_dir / name) for name in names]
        return SuiteBenchmarkResult(
            summary=self._summarize(scenarios),
            scenarios=tuple(scenarios),
        )

    async def run_scenario(self, scenario_path: Path) -> ScenarioBenchmarkResult:
        scenario = self._loader.load(scenario_path)
        bus = InMemoryBus()
        context_engine = ContextEngine(bus)
        decision_runtime = DecisionRuntime(bus, facts=DEFAULT_BENCHMARK_FACTS)
        replay = await ReplayRunner(bus).run(scenario)

        detected_contexts: list[str] = []
        proposed_actions: list[str] = []
        first_context_latency_ms: int | None = None
        first_action_proposal_latency_ms: int | None = None
        action_contract_blocks = 0

        for published in replay.published_percepts:
            context = await context_engine.ingest(published.message.payload)
            detected_contexts.extend(_event_labels(context))
            if first_context_latency_ms is None and _has_expected_context(context, scenario):
                first_context_latency_ms = published.at_ms

            decision = await decision_runtime.evaluate(context)
            action_contract_blocks += len(decision.blocks)
            for proposal in decision.proposals:
                proposed_actions.append(proposal.action_id)
            if first_action_proposal_latency_ms is None and decision.proposals:
                first_action_proposal_latency_ms = published.at_ms

        expected_contexts = tuple(scenario.expected_contexts)
        expected_actions = tuple(scenario.expected_actions)
        unique_contexts = tuple(dict.fromkeys(detected_contexts))
        unique_actions = tuple(dict.fromkeys(proposed_actions))

        context_budget = scenario.latency_budget_ms.first_context_update
        action_budget = scenario.latency_budget_ms.first_action_proposal

        return ScenarioBenchmarkResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            application_profile=scenario.application_profile,
            room=scenario.room,
            percept_count=len(replay.published_percepts),
            expected_contexts=expected_contexts,
            detected_contexts=unique_contexts,
            missing_contexts=_missing(expected_contexts, unique_contexts),
            unexpected_contexts=_unexpected(unique_contexts, expected_contexts),
            expected_actions=expected_actions,
            proposed_actions=unique_actions,
            missing_actions=_missing(expected_actions, unique_actions),
            unexpected_actions=_unexpected(unique_actions, expected_actions),
            first_context_latency_ms=first_context_latency_ms,
            first_action_proposal_latency_ms=first_action_proposal_latency_ms,
            context_latency_budget_ms=context_budget,
            action_latency_budget_ms=action_budget,
            context_latency_budget_passed=_budget_passed(
                first_context_latency_ms,
                context_budget,
                expected_contexts,
            ),
            action_latency_budget_passed=_budget_passed(
                first_action_proposal_latency_ms,
                action_budget,
                expected_actions,
            ),
            action_contract_blocks=action_contract_blocks,
        )

    @staticmethod
    def _summarize(scenarios: list[ScenarioBenchmarkResult]) -> BenchmarkSummary:
        context_latencies = [
            scenario.first_context_latency_ms
            for scenario in scenarios
            if scenario.first_context_latency_ms is not None
        ]
        action_latencies = [
            scenario.first_action_proposal_latency_ms
            for scenario in scenarios
            if scenario.first_action_proposal_latency_ms is not None
        ]
        return BenchmarkSummary(
            scenario_count=len(scenarios),
            passed_scenarios=sum(1 for scenario in scenarios if scenario.passed),
            failed_scenarios=sum(1 for scenario in scenarios if not scenario.passed),
            context_latency=percentile_summary(context_latencies),
            action_proposal_latency=percentile_summary(action_latencies),
            false_positive_contexts=sum(
                len(scenario.unexpected_contexts) for scenario in scenarios
            ),
            false_negative_contexts=sum(len(scenario.missing_contexts) for scenario in scenarios),
            false_positive_actions=sum(len(scenario.unexpected_actions) for scenario in scenarios),
            false_negative_actions=sum(len(scenario.missing_actions) for scenario in scenarios),
            action_contract_blocks=sum(scenario.action_contract_blocks for scenario in scenarios),
        )


def _event_labels(context: ContextUpdate) -> list[str]:
    return [event.label for event in context.events]


def _has_expected_context(context: ContextUpdate, scenario: ScenarioDefinition) -> bool:
    labels = set(_event_labels(context))
    return any(label in labels for label in scenario.expected_contexts)


def _missing(expected: tuple[str, ...], actual: tuple[str, ...]) -> tuple[str, ...]:
    actual_set = set(actual)
    return tuple(item for item in expected if item not in actual_set)


def _unexpected(actual: tuple[str, ...], expected: tuple[str, ...]) -> tuple[str, ...]:
    expected_set = set(expected)
    return tuple(item for item in actual if item not in expected_set)


def _budget_passed(
    observed_latency_ms: int | None,
    budget_ms: int | None,
    expected_items: tuple[str, ...],
) -> bool | None:
    if not expected_items or budget_ms is None:
        return None
    if observed_latency_ms is None:
        return False
    return observed_latency_ms <= budget_ms
