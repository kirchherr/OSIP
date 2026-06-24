"""Experimental learned-fusion governance contracts.

This module defines promotion gates for learned context-fusion candidates. It
does not train, load, or execute learned models in the runtime fast path.
"""

from __future__ import annotations

from typing import Literal

from omnisense_osip.schemas import Confidence, Identifier, Label, OSIPModel, ProfileIdentifier
from pydantic import Field, model_validator

type LearnedFusionState = Literal["draft", "shadow", "approved", "rejected"]
type LearnedFusionMode = Literal["shadow", "advisory", "replace_rule"]


class LearnedFusionCandidate(OSIPModel):
    """Declarative record for one learned fusion candidate."""

    candidate_id: Identifier
    profile_id: ProfileIdentifier
    version: str = Field(min_length=1)
    target_event_labels: tuple[Label, ...] = Field(min_length=1)
    allowed_modes: tuple[LearnedFusionMode, ...] = ("shadow",)
    approval_state: LearnedFusionState = "draft"
    dataset_manifest_ref: str | None = Field(default=None, min_length=1)
    model_card_ref: str | None = Field(default=None, min_length=1)
    benchmark_report_ref: str | None = Field(default=None, min_length=1)
    rollback_target: str | None = Field(default=None, min_length=1)
    notes: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_promotion_metadata(self) -> LearnedFusionCandidate:
        if not self.allowed_modes:
            msg = "allowed_modes must not be empty"
            raise ValueError(msg)
        if self.approval_state == "approved":
            missing = [
                name
                for name, value in (
                    ("dataset_manifest_ref", self.dataset_manifest_ref),
                    ("model_card_ref", self.model_card_ref),
                    ("benchmark_report_ref", self.benchmark_report_ref),
                    ("rollback_target", self.rollback_target),
                )
                if value is None
            ]
            if missing:
                msg = "approved learned fusion candidates require " + ", ".join(missing)
                raise ValueError(msg)
        if "replace_rule" in self.allowed_modes and self.approval_state != "approved":
            msg = "replace_rule mode is only allowed for approved learned fusion candidates"
            raise ValueError(msg)
        return self


class LearnedFusionEvaluation(OSIPModel):
    """Replay or benchmark evidence for one learned fusion candidate."""

    candidate_id: Identifier
    profile_id: ProfileIdentifier
    scenario_count: int = Field(gt=0)
    shadow_mode: bool
    teacher_agreement: Confidence
    schema_failures: int = Field(ge=0)
    benchmark_gate_failures: int = Field(ge=0)
    safety_regressions: int = Field(ge=0)
    false_positive_delta: int = 0
    false_negative_delta: int = 0
    p95_latency_delta_ms: int = 0
    benchmark_report_ref: str = Field(min_length=1)
    evidence_notes: tuple[str, ...] = Field(default_factory=tuple)


class LearnedFusionGatePolicy(OSIPModel):
    """Promotion policy for learned fusion candidates."""

    min_scenarios: int = Field(default=3, gt=0)
    min_teacher_agreement: Confidence = 0.95
    max_false_positive_delta: int = 0
    max_false_negative_delta: int = 0
    max_p95_latency_delta_ms: int = 25
    require_shadow_mode: bool = True


class LearnedFusionGateDecision(OSIPModel):
    """Machine-readable result of evaluating one learned fusion candidate."""

    candidate_id: Identifier
    approved: bool
    recommended_state: LearnedFusionState
    reasons: tuple[str, ...] = Field(default_factory=tuple)


class LearnedFusionPromotionGate:
    """Evaluate learned fusion candidates against conservative safety gates."""

    def __init__(self, policy: LearnedFusionGatePolicy | None = None) -> None:
        self._policy = policy or LearnedFusionGatePolicy()

    @property
    def policy(self) -> LearnedFusionGatePolicy:
        return self._policy

    def evaluate(
        self,
        candidate: LearnedFusionCandidate,
        evaluation: LearnedFusionEvaluation,
    ) -> LearnedFusionGateDecision:
        if candidate.candidate_id != evaluation.candidate_id:
            msg = "evaluation candidate_id must match candidate"
            raise ValueError(msg)
        if candidate.profile_id != evaluation.profile_id:
            msg = "evaluation profile_id must match candidate"
            raise ValueError(msg)

        reasons = tuple(_gate_failures(candidate, evaluation, self._policy))
        if reasons:
            return LearnedFusionGateDecision(
                candidate_id=candidate.candidate_id,
                approved=False,
                recommended_state="rejected",
                reasons=reasons,
            )

        recommended_state: LearnedFusionState = "approved"
        if candidate.approval_state == "draft":
            recommended_state = "shadow"
        elif candidate.approval_state == "rejected":
            recommended_state = "rejected"

        return LearnedFusionGateDecision(
            candidate_id=candidate.candidate_id,
            approved=recommended_state == "approved",
            recommended_state=recommended_state,
            reasons=(),
        )


def _gate_failures(
    candidate: LearnedFusionCandidate,
    evaluation: LearnedFusionEvaluation,
    policy: LearnedFusionGatePolicy,
) -> list[str]:
    failures: list[str] = []
    if candidate.approval_state == "rejected":
        failures.append("candidate is already rejected")
    if policy.require_shadow_mode and not evaluation.shadow_mode:
        failures.append("evaluation must run in shadow mode")
    if evaluation.scenario_count < policy.min_scenarios:
        failures.append(
            f"scenario_count {evaluation.scenario_count} is below minimum {policy.min_scenarios}"
        )
    if evaluation.teacher_agreement < policy.min_teacher_agreement:
        failures.append(
            f"teacher_agreement {evaluation.teacher_agreement:.3f} is below "
            f"{policy.min_teacher_agreement:.3f}"
        )
    if evaluation.schema_failures:
        failures.append(f"schema_failures must be zero, got {evaluation.schema_failures}")
    if evaluation.benchmark_gate_failures:
        failures.append(
            f"benchmark_gate_failures must be zero, got {evaluation.benchmark_gate_failures}"
        )
    if evaluation.safety_regressions:
        failures.append(f"safety_regressions must be zero, got {evaluation.safety_regressions}")
    if evaluation.false_positive_delta > policy.max_false_positive_delta:
        failures.append(
            f"false_positive_delta {evaluation.false_positive_delta} exceeds "
            f"{policy.max_false_positive_delta}"
        )
    if evaluation.false_negative_delta > policy.max_false_negative_delta:
        failures.append(
            f"false_negative_delta {evaluation.false_negative_delta} exceeds "
            f"{policy.max_false_negative_delta}"
        )
    if evaluation.p95_latency_delta_ms > policy.max_p95_latency_delta_ms:
        failures.append(
            f"p95_latency_delta_ms {evaluation.p95_latency_delta_ms} exceeds "
            f"{policy.max_p95_latency_delta_ms}"
        )
    return failures
