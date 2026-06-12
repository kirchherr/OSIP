from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema.validators import Draft202012Validator
from omnisense_osip.schema_export import SCHEMA_MODELS, export_json_schemas

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "protocols" / "schemas"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "osip"

SCHEMA_BY_FIXTURE = {
    "model_capability.json": "model_capability.schema.json",
    "percept_packet.json": "percept_packet.schema.json",
    "context_update.json": "context_update.schema.json",
    "event_detected.json": "event_detected.schema.json",
    "action_contract.json": "action_contract.schema.json",
    "action_proposal.json": "action_proposal.schema.json",
    "action_command.json": "action_command.schema.json",
    "action_result.json": "action_result.schema.json",
    "profile_safety_case.json": "profile_safety_case.schema.json",
    "adapter_heartbeat.json": "adapter_heartbeat.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_exported_schema_files_exist() -> None:
    assert sorted(SCHEMA_BY_FIXTURE.values()) == sorted(SCHEMA_MODELS)
    for schema_file in SCHEMA_BY_FIXTURE.values():
        assert (SCHEMA_DIR / schema_file).is_file()


def test_fixtures_validate_against_exported_json_schemas() -> None:
    for fixture_file, schema_file in SCHEMA_BY_FIXTURE.items():
        schema = load_json(SCHEMA_DIR / schema_file)
        fixture = load_json(FIXTURE_DIR / fixture_file)

        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(fixture)


def test_schema_export_is_reproducible(tmp_path: Path) -> None:
    export_json_schemas(tmp_path)

    for schema_file in SCHEMA_BY_FIXTURE.values():
        committed = load_json(SCHEMA_DIR / schema_file)
        generated = load_json(tmp_path / schema_file)
        assert generated == committed
