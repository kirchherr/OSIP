"""Replay validated scenarios onto a message bus."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from omnisense_bus import AsyncMessageBus, BusMessage
from omnisense_osip import PerceptPacket

from omnisense_sim.clocks import SimulatedClock
from omnisense_sim.percept_generators import build_percept_packet, scenario_topic
from omnisense_sim.scenario_loader import ScenarioLoader
from omnisense_sim.schemas import ScenarioDefinition


@dataclass(frozen=True, slots=True)
class PublishedPercept:
    at_ms: int
    message: BusMessage[PerceptPacket]


@dataclass(frozen=True, slots=True)
class ReplayResult:
    scenario: ScenarioDefinition
    published_percepts: list[PublishedPercept]
    final_time_ms: int

    @property
    def topics(self) -> list[str]:
        return [item.message.topic for item in self.published_percepts]


class ReplayRunner:
    """Deterministically publish scenario percepts without real sleeps."""

    def __init__(
        self,
        bus: AsyncMessageBus,
        *,
        clock: SimulatedClock | None = None,
        loader: ScenarioLoader | None = None,
    ) -> None:
        self._bus = bus
        self._clock = clock or SimulatedClock()
        self._loader = loader or ScenarioLoader()

    @property
    def clock(self) -> SimulatedClock:
        return self._clock

    async def run(self, scenario: ScenarioDefinition | Path | str) -> ReplayResult:
        definition = self._coerce_scenario(scenario)
        published: list[PublishedPercept] = []

        ordered_percepts = sorted(definition.percepts, key=lambda item: item.at_ms)
        for index, event in enumerate(ordered_percepts, start=1):
            self._clock.advance_to(event.at_ms)
            packet = build_percept_packet(
                definition,
                event,
                index=index,
                clock=self._clock,
            )
            message = await self._bus.publish(scenario_topic(event), packet)
            published.append(PublishedPercept(at_ms=event.at_ms, message=message))

        self._clock.advance_to(definition.duration_ms)
        return ReplayResult(
            scenario=definition,
            published_percepts=published,
            final_time_ms=self._clock.current_ms,
        )

    def _coerce_scenario(self, scenario: ScenarioDefinition | Path | str) -> ScenarioDefinition:
        if isinstance(scenario, ScenarioDefinition):
            return scenario
        return self._loader.load(scenario)
