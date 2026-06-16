"""Gateway state and event broadcasting."""

from __future__ import annotations

from collections.abc import Mapping

from fastapi import WebSocket
from omnisense_bus import (
    InMemoryBus,
    model_capabilities_topic,
    percept_topic,
)
from omnisense_context import ContextEngine, ContextGraph
from omnisense_decision import DecisionRuntime, ScalarFact
from omnisense_model_plugins import (
    ModelPluginManifest,
    ModelPluginRegistration,
    ModelPluginRegistry,
)
from omnisense_osip import (
    ActionProposal,
    ContextUpdate,
    ModelCapabilityDescriptor,
    PerceptPacket,
)
from pydantic import BaseModel

from omnisense_gateway.capability_gate import CapabilityGate
from omnisense_gateway.dashboard import DashboardCounters, DashboardSnapshot, summarize_latency

DEFAULT_GATEWAY_FACTS: dict[str, ScalarFact] = {
    "hvac.available": True,
    "notification.available": True,
    "speaker.available": True,
}


class EventStream:
    """Small in-process WebSocket fan-out for gateway tests and demos."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, event_type: str, payload: object) -> None:
        event = {
            "type": event_type,
            "payload": _to_jsonable(payload),
        }
        disconnected: list[WebSocket] = []
        for websocket in tuple(self._clients):
            try:
                await websocket.send_json(event)
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)


class GatewayState:
    """Stateful composition of bus, context engine, and decision runtime."""

    def __init__(
        self,
        *,
        bus: InMemoryBus | None = None,
        facts: Mapping[str, ScalarFact] | None = None,
    ) -> None:
        self.bus = bus or InMemoryBus()
        self.context_engine = ContextEngine(self.bus)
        self.context_graph = ContextGraph(graph_id="gateway")
        self.decision_runtime = DecisionRuntime(
            self.bus,
            facts=dict(DEFAULT_GATEWAY_FACTS) | dict(facts or {}),
        )
        self.events = EventStream()
        self.models: dict[str, ModelCapabilityDescriptor] = {}
        self.model_plugins = ModelPluginRegistry()
        self.capability_gate = CapabilityGate(self.models)
        self.current_context_by_room: dict[str, ContextUpdate] = {}
        self.latest_context: ContextUpdate | None = None
        self._recent_percepts: list[PerceptPacket] = []
        self._recent_action_proposals: list[ActionProposal] = []
        self._percepts_ingested = 0
        self._contexts_emitted = 0
        self._action_proposals_emitted = 0

    async def register_model(
        self,
        capability: ModelCapabilityDescriptor,
    ) -> ModelCapabilityDescriptor:
        self.models[capability.model_id] = capability
        await self.bus.publish(model_capabilities_topic(), capability)
        await self.events.broadcast("model.capability_registered", capability)
        return capability

    async def register_model_plugin(
        self,
        manifest: ModelPluginManifest,
    ) -> ModelPluginRegistration:
        registration = self.model_plugins.register(manifest)
        await self.register_model(registration.manifest.capability)
        await self.events.broadcast("model.plugin_registered", registration)
        return registration

    async def ingest_percept(
        self,
        percept: PerceptPacket,
    ) -> tuple[ContextUpdate, tuple[ActionProposal, ...]]:
        self.capability_gate.validate(percept)
        await self.bus.publish(percept_topic(percept.modality, percept.source_model), percept)
        context = await self.context_engine.ingest(percept)
        self.context_graph.apply(context)
        self.current_context_by_room[context.room] = context
        self.latest_context = context
        decision = await self.decision_runtime.evaluate(context)
        self._percepts_ingested += 1
        self._contexts_emitted += 1
        self._action_proposals_emitted += len(decision.proposals)
        self._remember_percept(percept)
        self._remember_action_proposals(decision.proposals)

        await self.events.broadcast("percept.ingested", percept)
        await self.events.broadcast("context.update", context)
        for proposal in decision.proposals:
            await self.events.broadcast("action.proposal", proposal)

        return context, decision.proposals

    def current_context(self, room: str | None = None) -> ContextUpdate | None:
        if room is not None:
            return self.current_context_by_room.get(room)
        return self.latest_context

    def dashboard_snapshot(self, *, room: str | None = None) -> DashboardSnapshot:
        context = self.current_context(room)
        recent_percepts = tuple(
            percept
            for percept in self._recent_percepts
            if room is None or _percept_room(percept) == room
        )
        return DashboardSnapshot(
            generated_at=self.context_graph.snapshot().generated_at,
            counters=DashboardCounters(
                models_registered=len(self.models),
                model_plugins_registered=len(self.model_plugins.manifests()),
                percepts_ingested=self._percepts_ingested,
                contexts_emitted=self._contexts_emitted,
                action_proposals_emitted=self._action_proposals_emitted,
            ),
            registered_models=tuple(sorted(self.models)),
            registered_plugins=tuple(
                manifest.plugin_id for manifest in self.model_plugins.manifests()
            ),
            current_context=context,
            context_graph=self.context_graph.stats(),
            recent_percepts=recent_percepts,
            recent_action_proposals=tuple(self._recent_action_proposals),
            recent_percept_latency_ms=summarize_latency(recent_percepts),
        )

    def _remember_percept(self, percept: PerceptPacket) -> None:
        self._recent_percepts.append(percept)
        del self._recent_percepts[:-50]

    def _remember_action_proposals(self, proposals: tuple[ActionProposal, ...]) -> None:
        self._recent_action_proposals.extend(proposals)
        del self._recent_action_proposals[:-50]


def _to_jsonable(payload: object) -> object:
    if isinstance(payload, BaseModel):
        return payload.model_dump(mode="json", exclude_none=True)
    if isinstance(payload, tuple | list):
        return [_to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {str(key): _to_jsonable(value) for key, value in payload.items()}
    return payload


def _percept_room(percept: PerceptPacket) -> str | None:
    if percept.location is None:
        return None
    return percept.location.room
