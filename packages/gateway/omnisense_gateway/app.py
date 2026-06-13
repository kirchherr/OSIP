"""FastAPI app factory for OSIP Gateway API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from omnisense_model_plugins import ModelPluginManifest
from omnisense_osip import ActionProposal, ContextUpdate, ModelCapabilityDescriptor, PerceptPacket
from pydantic import BaseModel, ConfigDict

from omnisense_gateway.capability_gate import CapabilityGateError
from omnisense_gateway.state import GatewayState


class ModelRegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    registered: bool


class ModelPluginRegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plugin_id: str
    model_id: str
    status: str
    registered: bool


class PerceptIngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    percept_id: str
    context: ContextUpdate
    action_proposals: list[ActionProposal]


def create_app(state: GatewayState | None = None) -> FastAPI:
    gateway_state = state or GatewayState()
    app = FastAPI(
        title="OmniSense Runtime Gateway",
        version="0.1.0",
        description="HTTP and WebSocket gateway for OSIP v0.1 messages.",
    )
    app.state.gateway = gateway_state

    @app.post("/v1/models/register", response_model=ModelRegistrationResponse)
    async def register_model(
        capability: ModelCapabilityDescriptor,
    ) -> ModelRegistrationResponse:
        registered = await gateway_state.register_model(capability)
        return ModelRegistrationResponse(model_id=registered.model_id, registered=True)

    @app.post("/v1/model-plugins/register", response_model=ModelPluginRegistrationResponse)
    async def register_model_plugin(
        manifest: ModelPluginManifest,
    ) -> ModelPluginRegistrationResponse:
        registration = await gateway_state.register_model_plugin(manifest)
        return ModelPluginRegistrationResponse(
            plugin_id=registration.manifest.plugin_id,
            model_id=registration.manifest.capability.model_id,
            status=registration.status,
            registered=True,
        )

    @app.post("/v1/percepts", response_model=PerceptIngestResponse)
    async def ingest_percept(percept: PerceptPacket) -> PerceptIngestResponse:
        try:
            context, proposals = await gateway_state.ingest_percept(percept)
        except CapabilityGateError as exc:
            raise HTTPException(status_code=403, detail=list(exc.violations)) from exc
        return PerceptIngestResponse(
            percept_id=percept.id,
            context=context,
            action_proposals=list(proposals),
        )

    @app.get("/v1/context/current", response_model=ContextUpdate)
    async def current_context(
        room: Annotated[str | None, Query(min_length=1)] = None,
    ) -> ContextUpdate:
        context = gateway_state.current_context(room)
        if context is None:
            detail = f"no current context for room '{room}'" if room else "no current context"
            raise HTTPException(status_code=404, detail=detail)
        return context

    @app.websocket("/ws/events")
    async def event_stream(websocket: WebSocket) -> None:
        await gateway_state.events.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            gateway_state.events.disconnect(websocket)

    return app
