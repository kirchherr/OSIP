from __future__ import annotations

import pytest
from omnisense_context.learned_fusion import (
    LearnedFusionCandidate,
    LearnedFusionEvaluation,
    LearnedFusionGatePolicy,
    LearnedFusionPromotionGate,
)
from pydantic import ValidationError


def candidate(**updates: object) -> LearnedFusionCandidate:
    data: dict[str, object] = {
        "candidate_id": "learned_fusion.rooms_smoke_v1",
        "profile_id": "rooms",
        "version": "0.1.0",
        "target_event_labels": ("context.possible_burning_food",),
        "allowed_modes": ("shadow",),
        "approval_state": "draft",
    }
    data.update(updates)
    return LearnedFusionCandidate.model_validate(data)


def evaluation(**updates: object) -> LearnedFusionEvaluation:
    data: dict[str, object] = {
        "candidate_id": "learned_fusion.rooms_smoke_v1",
        "profile_id": "rooms",
        "scenario_count": 5,
        "shadow_mode": True,
        "teacher_agreement": 0.98,
        "schema_failures": 0,
        "benchmark_gate_failures": 0,
        "safety_regressions": 0,
        "false_positive_delta": 0,
        "false_negative_delta": 0,
        "p95_latency_delta_ms": 5,
        "benchmark_report_ref": "benchmarks/rooms_smoke_v1.json",
    }
    data.update(updates)
    return LearnedFusionEvaluation.model_validate(data)


def test_gate_moves_draft_candidate_to_shadow_when_evidence_passes() -> None:
    gate = LearnedFusionPromotionGate()

    decision = gate.evaluate(candidate(), evaluation())

    assert decision.approved is False
    assert decision.recommended_state == "shadow"
    assert decision.reasons == ()


def test_gate_approves_shadow_candidate_with_required_artifacts() -> None:
    gate = LearnedFusionPromotionGate()
    learned = candidate(
        approval_state="shadow",
        dataset_manifest_ref="datasets/rooms_smoke_v1.json",
        model_card_ref="model_cards/rooms_smoke_v1.md",
        benchmark_report_ref="benchmarks/rooms_smoke_v1.json",
        rollback_target="rooms.rules.v1",
    )

    decision = gate.evaluate(learned, evaluation())

    assert decision.approved is True
    assert decision.recommended_state == "approved"


def test_candidate_requires_artifacts_before_approved_state() -> None:
    with pytest.raises(ValidationError, match="approved learned fusion candidates"):
        candidate(approval_state="approved")


def test_candidate_allows_replace_rule_only_when_approved() -> None:
    with pytest.raises(ValidationError, match="replace_rule"):
        candidate(allowed_modes=("shadow", "replace_rule"))

    learned = candidate(
        approval_state="approved",
        allowed_modes=("shadow", "replace_rule"),
        dataset_manifest_ref="datasets/rooms_smoke_v1.json",
        model_card_ref="model_cards/rooms_smoke_v1.md",
        benchmark_report_ref="benchmarks/rooms_smoke_v1.json",
        rollback_target="rooms.rules.v1",
    )

    assert "replace_rule" in learned.allowed_modes


def test_gate_rejects_safety_regressions_and_schema_failures() -> None:
    gate = LearnedFusionPromotionGate()

    decision = gate.evaluate(
        candidate(),
        evaluation(schema_failures=1, safety_regressions=1),
    )

    assert decision.approved is False
    assert decision.recommended_state == "rejected"
    assert "schema_failures must be zero, got 1" in decision.reasons
    assert "safety_regressions must be zero, got 1" in decision.reasons


def test_gate_rejects_missing_shadow_mode_and_low_teacher_agreement() -> None:
    gate = LearnedFusionPromotionGate(
        LearnedFusionGatePolicy(min_scenarios=4, min_teacher_agreement=0.97)
    )

    decision = gate.evaluate(
        candidate(),
        evaluation(scenario_count=3, shadow_mode=False, teacher_agreement=0.9),
    )

    assert decision.recommended_state == "rejected"
    assert "evaluation must run in shadow mode" in decision.reasons
    assert any("scenario_count 3 is below minimum 4" == reason for reason in decision.reasons)
    assert any("teacher_agreement 0.900" in reason for reason in decision.reasons)


def test_gate_rejects_regressions_against_baseline_policy() -> None:
    gate = LearnedFusionPromotionGate(
        LearnedFusionGatePolicy(
            max_false_positive_delta=0,
            max_false_negative_delta=0,
            max_p95_latency_delta_ms=10,
        )
    )

    decision = gate.evaluate(
        candidate(),
        evaluation(false_positive_delta=1, false_negative_delta=1, p95_latency_delta_ms=11),
    )

    assert decision.recommended_state == "rejected"
    assert any("false_positive_delta 1 exceeds 0" == reason for reason in decision.reasons)
    assert any("false_negative_delta 1 exceeds 0" == reason for reason in decision.reasons)
    assert any("p95_latency_delta_ms 11 exceeds 10" == reason for reason in decision.reasons)


def test_gate_requires_evaluation_to_match_candidate() -> None:
    gate = LearnedFusionPromotionGate()

    with pytest.raises(ValueError, match="candidate_id"):
        gate.evaluate(candidate(), evaluation(candidate_id="learned_fusion.other_v1"))

    with pytest.raises(ValueError, match="profile_id"):
        gate.evaluate(candidate(), evaluation(profile_id="physical-ai"))
