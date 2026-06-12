from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from omnisense_osip import (
    ActionCommand,
    ActionContract,
    ActionProposal,
    ActionResult,
    AdapterHeartbeat,
    ContextUpdate,
    CovarianceMatrix,
    EventDetected,
    EvidenceRef,
    ModelCapabilityDescriptor,
    PerceptPacket,
    ProfileSafetyCase,
    Uncertainty,
    from_json,
    to_json,
    validate_osip_message,
)
from pydantic import BaseModel, ValidationError

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "osip"


def load_fixture(filename: str) -> dict[str, Any]:
    data = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.mark.parametrize(
    ("filename", "model_cls"),
    [
        ("model_capability.json", ModelCapabilityDescriptor),
        ("percept_packet.json", PerceptPacket),
        ("context_update.json", ContextUpdate),
        ("event_detected.json", EventDetected),
        ("action_contract.json", ActionContract),
        ("action_proposal.json", ActionProposal),
        ("action_command.json", ActionCommand),
        ("action_result.json", ActionResult),
        ("profile_safety_case.json", ProfileSafetyCase),
        ("adapter_heartbeat.json", AdapterHeartbeat),
    ],
)
def test_valid_fixtures_round_trip(filename: str, model_cls: type[BaseModel]) -> None:
    message = validate_osip_message(load_fixture(filename))

    assert isinstance(message, model_cls)
    assert from_json(to_json(message)) == message


def test_percept_requires_at_least_one_claim() -> None:
    data = load_fixture("percept_packet.json")
    data["claims"] = []

    with pytest.raises(ValidationError, match="claims"):
        PerceptPacket.model_validate(data)


def test_percept_rejects_unknown_schema_version() -> None:
    data = load_fixture("percept_packet.json")
    data["schema_version"] = "osip/9.9"

    with pytest.raises(ValidationError, match="schema_version"):
        PerceptPacket.model_validate(data)


def test_percept_rejects_naive_timestamp() -> None:
    data = load_fixture("percept_packet.json")
    data["timestamp"] = "2026-06-12T14:31:09.210"

    with pytest.raises(ValidationError, match="timezone"):
        PerceptPacket.model_validate(data)


def test_latency_profile_must_be_ordered() -> None:
    data = load_fixture("model_capability.json")
    data["latency_profile"] = {
        "p50_ms": 100,
        "p95_ms": 50,
        "max_budget_ms": 120,
    }

    with pytest.raises(ValidationError, match="p50_ms <= p95_ms"):
        ModelCapabilityDescriptor.model_validate(data)


def test_context_events_require_evidence() -> None:
    data = load_fixture("context_update.json")
    data["events"][0]["evidence"] = []

    with pytest.raises(ValidationError, match="evidence"):
        ContextUpdate.model_validate(data)


def test_context_event_accepts_structured_evidence_refs() -> None:
    data = load_fixture("context_update.json")
    data["trace_id"] = "trace_kitchen_001"
    data["correlation_id"] = "corr_kitchen_001"
    data["events"][0]["evidence_refs"] = [
        {
            "source_type": "percept.packet",
            "source_id": "percept_smoke_001",
            "claim_label": "chemical.air.smoke_like_pattern",
            "confidence": 0.91,
            "source_model": "air_quality_model_v1",
            "modality": "chemical",
            "timestamp": data["timestamp"],
        }
    ]

    update = ContextUpdate.model_validate(data)

    assert update.trace_id == "trace_kitchen_001"
    assert update.correlation_id == "corr_kitchen_001"
    assert update.events[0].evidence_refs[0].source_id == "percept_smoke_001"
    assert update.events[0].evidence_refs[0].claim_label == "chemical.air.smoke_like_pattern"


def test_percept_claim_accepts_structured_uncertainty() -> None:
    data = load_fixture("percept_packet.json")
    data["claims"][0]["uncertainty"] = {
        "confidence": 0.82,
        "covariance": {
            "variables": ["x", "y", "z"],
            "values": [
                [0.04, 0.0, 0.0],
                [0.0, 0.04, 0.0],
                [0.0, 0.0, 0.09],
            ],
            "unit": "m^2",
        },
    }

    packet = PerceptPacket.model_validate(data)

    assert packet.claims[0].uncertainty is not None
    assert packet.claims[0].uncertainty.covariance is not None
    assert packet.claims[0].uncertainty.covariance.variables == ["x", "y", "z"]


def test_uncertainty_requires_representation() -> None:
    with pytest.raises(ValidationError, match="confidence, covariance, or distribution"):
        Uncertainty.model_validate({})


def test_covariance_matrix_must_match_variables() -> None:
    with pytest.raises(ValidationError, match="square matrix"):
        CovarianceMatrix.model_validate(
            {
                "variables": ["x", "y"],
                "values": [[0.1, 0.0, 0.0], [0.0, 0.1, 0.0]],
            }
        )


def test_evidence_ref_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        EvidenceRef.model_validate(
            {
                "source_type": "percept.packet",
                "source_id": "percept_smoke_001",
                "timestamp": "2026-06-12T12:00:00",
            }
        )


def test_adapter_heartbeat_rejects_naive_timestamp() -> None:
    data = load_fixture("adapter_heartbeat.json")
    data["timestamp"] = "2026-06-12T12:00:00"

    with pytest.raises(ValidationError, match="timezone"):
        AdapterHeartbeat.model_validate(data)


def test_profile_safety_case_requires_safe_state() -> None:
    data = load_fixture("profile_safety_case.json")
    data["default_safe_states"] = []

    with pytest.raises(ValidationError, match="default_safe_states"):
        ProfileSafetyCase.model_validate(data)


def test_high_risk_contract_requires_rollback_or_safe_state() -> None:
    data = load_fixture("action_contract.json")
    data["risk_class"] = "critical"
    data.pop("rollback")

    with pytest.raises(ValidationError, match="rollback or safe_state"):
        ActionContract.model_validate(data)


def test_unknown_message_type_is_rejected() -> None:
    data = load_fixture("percept_packet.json")
    data["type"] = "percept.unknown"

    with pytest.raises(ValueError, match="Unsupported OSIP message type"):
        validate_osip_message(data)
