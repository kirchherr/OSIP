"""Index OSIP claims across active percept packets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from omnisense_osip import PerceptPacket
from omnisense_osip.schemas import Claim


@dataclass(frozen=True, slots=True)
class ClaimObservation:
    label: str
    confidence: float
    value: Any
    percept_id: str
    source_model: str
    modality: str
    timestamp: datetime

    @classmethod
    def from_claim(cls, packet: PerceptPacket, claim: Claim) -> ClaimObservation:
        return cls(
            label=claim.label,
            confidence=claim.confidence,
            value=claim.value,
            percept_id=packet.id,
            source_model=packet.source_model,
            modality=packet.modality,
            timestamp=packet.timestamp,
        )


class ClaimIndex:
    """Lookup helper over active claims."""

    def __init__(self, observations: list[ClaimObservation]) -> None:
        self._observations = observations

    @classmethod
    def from_percepts(cls, percepts: list[PerceptPacket]) -> ClaimIndex:
        observations = [
            ClaimObservation.from_claim(packet, claim)
            for packet in percepts
            for claim in packet.claims
        ]
        return cls(observations)

    @property
    def observations(self) -> list[ClaimObservation]:
        return list(self._observations)

    def all_for(self, label: str) -> list[ClaimObservation]:
        return [observation for observation in self._observations if observation.label == label]

    def best(self, label: str) -> ClaimObservation | None:
        observations = self.all_for(label)
        if not observations:
            return None
        return max(observations, key=lambda item: item.confidence)

    def present_labels(self, labels: list[str], *, min_confidence: float = 0.0) -> list[str]:
        present: list[str] = []
        for label in labels:
            observation = self.best(label)
            if observation is not None and observation.confidence >= min_confidence:
                present.append(label)
        return present

    def numeric_at_least(self, label: str, threshold: float) -> ClaimObservation | None:
        for observation in sorted(
            self.all_for(label),
            key=lambda item: item.confidence,
            reverse=True,
        ):
            if isinstance(observation.value, int | float) and observation.value >= threshold:
                return observation
        return None
