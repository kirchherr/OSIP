from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
from fastapi.testclient import TestClient
from omnisense_gateway import create_app
from omnisense_osip import LatencyProfile, ModelCapabilityDescriptor, PerceptPacket
from omnisense_sdk import OmniSensePublisher
from omnisense_sim import ScenarioLoader
from omnisense_sim.clocks import SimulatedClock
from omnisense_sim.percept_generators import build_percept_packet

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "osip"


def load_model_capability() -> ModelCapabilityDescriptor:
    data = json.loads((FIXTURE_DIR / "model_capability.json").read_text(encoding="utf-8"))
    return ModelCapabilityDescriptor.model_validate(data)


def kitchen_percept_payloads() -> list[dict[str, Any]]:
    scenario = ScenarioLoader().load(SCENARIO_DIR / "kitchen_burning_food.yaml")
    clock = SimulatedClock()
    payloads: list[dict[str, Any]] = []
    for index, scenario_percept in enumerate(scenario.percepts, start=1):
        percept = build_percept_packet(
            scenario,
            scenario_percept,
            index=index,
            clock=clock,
        )
        payloads.append(percept.model_dump(mode="json", exclude_none=True))
    return payloads


def capabilities_for_payloads(
    payloads: list[dict[str, Any]],
) -> list[ModelCapabilityDescriptor]:
    by_model: dict[str, dict[str, set[str]]] = {}
    for payload in payloads:
        source_model = str(payload["source_model"])
        entry = by_model.setdefault(source_model, {"modalities": set(), "outputs": set()})
        entry["modalities"].add(str(payload["modality"]))
        for claim in payload["claims"]:
            entry["outputs"].add(str(claim["label"]))

    return [
        ModelCapabilityDescriptor(
            model_id=model_id,
            display_name=f"{model_id} capability",
            version="0.1.0",
            modalities=sorted(values["modalities"]),
            outputs=sorted(values["outputs"]),
            latency_profile=LatencyProfile(p50_ms=10, p95_ms=50, max_budget_ms=100),
            confidence_calibrated=False,
        )
        for model_id, values in sorted(by_model.items())
    ]


def register_capabilities(
    client: TestClient,
    payloads: list[dict[str, Any]],
) -> None:
    for capability in capabilities_for_payloads(payloads):
        response = client.post(
            "/v1/models/register",
            json=capability.model_dump(mode="json", exclude_none=True),
        )
        assert response.status_code == 200


def test_gateway_registers_models_ingests_percepts_and_serves_context() -> None:
    client = TestClient(create_app())
    percept_payloads = kitchen_percept_payloads()
    register_capabilities(client, percept_payloads)

    proposed_actions: list[str] = []
    last_context_id = ""
    for payload in percept_payloads:
        response = client.post("/v1/percepts", json=payload)
        assert response.status_code == 200
        body = response.json()
        last_context_id = body["context"]["context_id"]
        proposed_actions.extend(
            proposal["action_id"] for proposal in body["action_proposals"]
        )

    assert proposed_actions == ["action.notify.local", "action.hvac.ventilation_boost"]

    context_response = client.get("/v1/context/current", params={"room": "kitchen"})
    assert context_response.status_code == 200
    assert context_response.json()["context_id"] == last_context_id


def test_gateway_rejects_percepts_from_unregistered_model() -> None:
    client = TestClient(create_app())
    payload = kitchen_percept_payloads()[0]

    response = client.post("/v1/percepts", json=payload)

    assert response.status_code == 403
    assert "is not registered" in response.json()["detail"][0]


def test_gateway_rejects_claims_not_declared_by_capability() -> None:
    client = TestClient(create_app())
    payload = kitchen_percept_payloads()[0]
    capability = ModelCapabilityDescriptor(
        model_id=payload["source_model"],
        display_name="Narrow test capability",
        version="0.1.0",
        modalities=[payload["modality"]],
        outputs=["test.unrelated_claim"],
        latency_profile=LatencyProfile(p50_ms=10, p95_ms=50, max_budget_ms=100),
        confidence_calibrated=False,
    )
    register_response = client.post(
        "/v1/models/register",
        json=capability.model_dump(mode="json", exclude_none=True),
    )
    assert register_response.status_code == 200

    response = client.post("/v1/percepts", json=payload)

    assert response.status_code == 403
    assert "is not declared" in response.json()["detail"][0]


def test_gateway_event_websocket_streams_registration_events() -> None:
    client = TestClient(create_app())

    with client.websocket_connect("/ws/events") as websocket:
        response = client.post(
            "/v1/models/register",
            json=load_model_capability().model_dump(mode="json", exclude_none=True),
        )
        assert response.status_code == 200
        event = websocket.receive_json()

    assert event["type"] == "model.capability_registered"
    assert event["payload"]["type"] == "model.capability"


async def test_sdk_publisher_can_register_publish_and_read_context() -> None:
    app = create_app()
    percept_payloads = kitchen_percept_payloads()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        publisher = OmniSensePublisher("http://testserver", client=client)
        for capability in capabilities_for_payloads(percept_payloads):
            model_id = await publisher.register_model(capability)
            assert model_id

        for payload in percept_payloads:
            response = await publisher.publish_percept(
                build_percept_from_payload(payload)
            )
            assert response["percept_id"] == payload["id"]

        context = await publisher.current_context(room="kitchen")
        assert context.room == "kitchen"
        assert any(event.label == "context.possible_burning_food" for event in context.events)


def build_percept_from_payload(payload: dict[str, Any]) -> PerceptPacket:
    return PerceptPacket.model_validate(payload)
