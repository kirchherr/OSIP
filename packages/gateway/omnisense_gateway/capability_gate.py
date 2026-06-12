"""Capability gating for gateway percept ingestion."""

from __future__ import annotations

from collections.abc import Mapping

from omnisense_osip import ModelCapabilityDescriptor, PerceptPacket


class CapabilityGateError(ValueError):
    """Raised when a percept exceeds its registered model capability."""

    def __init__(self, percept: PerceptPacket, violations: list[str]) -> None:
        self.percept_id = percept.id
        self.source_model = percept.source_model
        self.violations = tuple(violations)
        super().__init__("; ".join(violations))


class CapabilityGate:
    """Validates percept packets against registered model capabilities."""

    def __init__(self, models: Mapping[str, ModelCapabilityDescriptor]) -> None:
        self._models = models

    def validate(self, percept: PerceptPacket) -> None:
        capability = self._models.get(percept.source_model)
        if capability is None:
            raise CapabilityGateError(
                percept,
                [f"source model '{percept.source_model}' is not registered"],
            )

        violations: list[str] = []
        if percept.modality not in capability.modalities:
            violations.append(
                f"modality '{percept.modality}' is not declared by model "
                f"'{capability.model_id}'"
            )

        allowed_outputs = set(capability.outputs)
        unsupported_claims = sorted(
            {claim.label for claim in percept.claims if claim.label not in allowed_outputs}
        )
        for claim_label in unsupported_claims:
            violations.append(
                f"claim '{claim_label}' is not declared by model '{capability.model_id}'"
            )

        if violations:
            raise CapabilityGateError(percept, violations)
