"""Gateway state and event broadcasting."""

from __future__ import annotations

from collections.abc import Mapping

from fastapi import WebSocket
from omnisense_bus import (
    InMemoryBus,
    model_capabilities_topic,
    percept_topic,
)
from omnisense_context import ContextEngine
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
        self.current_context_by_room[context.room] = context
        self.latest_context = context
        decision = await self.decision_runtime.evaluate(context)

        await self.events.broadcast("percept.ingested", percept)
        await self.events.broadcast("context.update", context)
        for proposal in decision.proposals:
            await self.events.broadcast("action.proposal", proposal)

        return context, decision.proposals

    def current_context(self, room: str | None = None) -> ContextUpdate | None:
        if room is not None:
            return self.current_context_by_room.get(room)
        return self.latest_context


def _to_jsonable(payload: object) -> object:
    if isinstance(payload, BaseModel):
        return payload.model_dump(mode="json", exclude_none=True)
    if isinstance(payload, tuple | list):
        return [_to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {str(key): _to_jsonable(value) for key, value in payload.items()}
    return payload
