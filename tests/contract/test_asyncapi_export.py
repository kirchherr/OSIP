from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from omnisense_bus.asyncapi_export import build_asyncapi_spec, export_asyncapi

ROOT = Path(__file__).resolve().parents[2]
ASYNCAPI_PATH = ROOT / "protocols" / "asyncapi" / "asyncapi.json"

EXPECTED_CHANNELS = {
    "modelCapabilities": "omnisense.models.capabilities",
    "percepts": "omnisense.percepts.{modality}.{source_model}",
    "contextUpdates": "omnisense.context.updates.{room}",
    "eventsDetected": "omnisense.events.detected.{event_label}",
    "actionContracts": "omnisense.actions.contracts",
    "actionProposals": "omnisense.actions.proposals",
    "actionCommands": "omnisense.actions.commands.{target}",
    "actionResults": "omnisense.actions.results.{action_id}",
}

EXPECTED_SCHEMA_REFS = {
    "../schemas/model_capability.schema.json",
    "../schemas/percept_packet.schema.json",
    "../schemas/context_update.schema.json",
    "../schemas/event_detected.schema.json",
    "../schemas/action_contract.schema.json",
    "../schemas/action_proposal.schema.json",
    "../schemas/action_command.schema.json",
    "../schemas/action_result.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_asyncapi_artifact_exists_and_declares_channels() -> None:
    spec = load_json(ASYNCAPI_PATH)

    assert spec["asyncapi"] == "3.1.0"
    assert {
        channel_id: channel["address"]
        for channel_id, channel in spec["channels"].items()
    } == EXPECTED_CHANNELS


def test_asyncapi_references_public_osip_schemas() -> None:
    spec = build_asyncapi_spec()

    schema_refs = {
        message["payload"]["$ref"]
        for message in spec["components"]["messages"].values()
    }

    assert schema_refs == EXPECTED_SCHEMA_REFS


def test_asyncapi_export_is_reproducible(tmp_path: Path) -> None:
    generated_path = export_asyncapi(tmp_path / "asyncapi.json")

    assert load_json(generated_path) == load_json(ASYNCAPI_PATH)
