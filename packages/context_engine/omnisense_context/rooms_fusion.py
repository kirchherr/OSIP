"""Transparent rooms-profile context fusion rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omnisense_osip import PerceptPacket
from omnisense_osip.schemas import ContextEvent, ContextUpdate, GlobalRisk

from omnisense_context.claim_index import ClaimIndex


@dataclass(frozen=True, slots=True)
class _Rule:
    label: str
    evidence_labels: list[str]
    contradiction_labels: list[str]
    minimum_evidence: int
    threshold: float
    urgency: float
    safety_risk: float
    comfort_risk: float
    maintenance_risk: float


class RoomsFusion:
    """Small deterministic fusion layer for the first rooms scenarios."""

    _rules = [
        _Rule(
            label="context.possible_burning_food",
            evidence_labels=[
                "object.stove.power_on",
                "thermal.stove.hotspot",
                "chemical.air.smoke_like_pattern",
                "vision.smoke.visible_near_stove",
            ],
            contradiction_labels=[
                "vision.no_smoke_visible",
                "object.stove.power_off",
                "chemical.air.steam_pattern",
            ],
            minimum_evidence=3,
            threshold=0.72,
            urgency=0.82,
            safety_risk=0.82,
            comfort_risk=0.25,
            maintenance_risk=0.35,
        ),
        _Rule(
            label="context.possible_fall",
            evidence_labels=[
                "tactile.floor_pressure_spike",
                "audio.impact_sound",
                "radar.motion_drop",
            ],
            contradiction_labels=[
                "person.standing",
                "object.falls_not_person",
            ],
            minimum_evidence=2,
            threshold=0.74,
            urgency=0.81,
            safety_risk=0.85,
            comfort_risk=0.2,
            maintenance_risk=0.05,
        ),
        _Rule(
            label="context.high_occupancy_stale_air",
            evidence_labels=[
                "occupancy.people_count",
                "environment.air.co2_high",
                "environment.air.voc_elevated",
            ],
            contradiction_labels=[
                "environment.air.ventilation_good",
                "occupancy.room_empty",
            ],
            minimum_evidence=2,
            threshold=0.7,
            urgency=0.55,
            safety_risk=0.2,
            comfort_risk=0.78,
            maintenance_risk=0.25,
        ),
    ]

    def fuse(
        self,
        percepts: list[PerceptPacket],
        *,
        context_id: str,
        timestamp: datetime,
        room: str,
        time_window_ms: int,
    ) -> ContextUpdate:
        index = ClaimIndex.from_percepts(percepts)
        events: list[ContextEvent] = []
        safety = 0.0
        comfort = 0.0
        maintenance = 0.0

        conflict_event = self._sensor_conflict(index)
        if conflict_event is not None:
            events.append(conflict_event)
            safety = max(safety, 0.35)
            maintenance = max(maintenance, 0.4)

        for rule in self._rules:
            event = self._evaluate_rule(rule, index)
            if event is None:
                continue
            events.append(event)
            safety = max(safety, rule.safety_risk)
            comfort = max(comfort, rule.comfort_risk)
            maintenance = max(maintenance, rule.maintenance_risk)

        return ContextUpdate(
            context_id=context_id,
            timestamp=timestamp,
            time_window_ms=time_window_ms,
            room=room,
            entities=[],
            events=events,
            global_risk=GlobalRisk(
                safety=safety,
                comfort=comfort,
                maintenance=maintenance,
            ),
        )

    def _evaluate_rule(self, rule: _Rule, index: ClaimIndex) -> ContextEvent | None:
        evidence = self._evidence(rule, index)
        contradictions = index.present_labels(rule.contradiction_labels, min_confidence=0.6)
        if len(evidence) < rule.minimum_evidence or contradictions:
            return None

        confidence = self._average_confidence(evidence, index)
        if confidence < rule.threshold:
            return None

        return ContextEvent(
            label=rule.label,
            confidence=round(confidence, 3),
            urgency=rule.urgency,
            evidence=evidence,
            contradictions=contradictions,
        )

    def _evidence(self, rule: _Rule, index: ClaimIndex) -> list[str]:
        evidence = index.present_labels(rule.evidence_labels, min_confidence=0.6)
        if (
            "occupancy.people_count" in rule.evidence_labels
            and index.numeric_at_least("occupancy.people_count", 3) is not None
            and "occupancy.people_count" not in evidence
        ):
            evidence.append("occupancy.people_count")
        return evidence

    @staticmethod
    def _average_confidence(labels: list[str], index: ClaimIndex) -> float:
        values: list[float] = []
        for label in labels:
            observation = index.best(label)
            if observation is not None:
                values.append(observation.confidence)
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def _sensor_conflict(index: ClaimIndex) -> ContextEvent | None:
        smoke_like = index.best("chemical.air.smoke_like_pattern")
        no_smoke = index.best("vision.no_smoke_visible")
        if smoke_like is None or no_smoke is None:
            return None
        if smoke_like.confidence < 0.65 or no_smoke.confidence < 0.65:
            return None
        confidence = min(smoke_like.confidence, no_smoke.confidence)
        return ContextEvent(
            label="context.sensor_conflict",
            confidence=round(confidence, 3),
            urgency=0.45,
            evidence=["chemical.air.smoke_like_pattern"],
            contradictions=["vision.no_smoke_visible"],
        )
