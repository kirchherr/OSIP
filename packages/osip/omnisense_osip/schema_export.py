"""Export OSIP Pydantic models as JSON Schema Draft 2020-12 artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from omnisense_osip.schemas import (
    ActionCommand,
    ActionContract,
    ActionProposal,
    ActionResult,
    AdapterHeartbeat,
    ContextUpdate,
    EventDetected,
    ModelCapabilityDescriptor,
    PerceptPacket,
    ProfileSafetyCase,
)

SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "model_capability.schema.json": ModelCapabilityDescriptor,
    "percept_packet.schema.json": PerceptPacket,
    "context_update.schema.json": ContextUpdate,
    "event_detected.schema.json": EventDetected,
    "action_contract.schema.json": ActionContract,
    "action_proposal.schema.json": ActionProposal,
    "action_command.schema.json": ActionCommand,
    "action_result.schema.json": ActionResult,
    "profile_safety_case.schema.json": ProfileSafetyCase,
    "adapter_heartbeat.schema.json": AdapterHeartbeat,
}


def export_json_schemas(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []

    for filename, model in SCHEMA_MODELS.items():
        schema = model.model_json_schema(mode="validation")
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"https://schemas.omnisense.dev/osip/0.1/{filename}"
        path = output_dir / filename
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        exported.append(path)

    return exported
