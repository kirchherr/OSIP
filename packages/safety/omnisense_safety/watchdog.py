"""Deterministic watchdog evaluation for profile safe states."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from omnisense_osip import AdapterHeartbeat, ContextUpdate, DefaultSafeState, ProfileSafetyCase


@dataclass(frozen=True, slots=True)
class SafeStateActivation:
    """One safe-state activation requested by a watchdog trigger."""

    target: str
    safe_state: str
    trigger: str
    reason: str
    age_ms: int | None = None
    requires_hardware_interlock: bool = False


@dataclass(frozen=True, slots=True)
class SafetyEvaluation:
    """Watchdog result for one profile safety case."""

    profile_id: str
    safe: bool
    activations: tuple[SafeStateActivation, ...]


class SafetyWatchdog:
    """Evaluates context freshness and adapter liveness against a safety case."""

    def __init__(self, safety_case: ProfileSafetyCase) -> None:
        self._safety_case = safety_case

    def evaluate(
        self,
        *,
        now: datetime,
        context: ContextUpdate | None = None,
        heartbeats: Iterable[AdapterHeartbeat] = (),
        bus_connected: bool = True,
        manual_estop: bool = False,
        contract_violation: bool = False,
        sensor_dropout: bool = False,
    ) -> SafetyEvaluation:
        _require_timezone(now)
        heartbeats_by_adapter = tuple(heartbeats)

        activations: list[SafeStateActivation] = []
        if context is None:
            activations.extend(
                self._activate(
                    "context_stale",
                    reason="no current context update is available",
                    age_ms=None,
                )
            )
        else:
            _require_timezone(context.timestamp)
            context_age_ms = _age_ms(now, context.timestamp)
            if context_age_ms > self._safety_case.stale_context_ms:
                activations.extend(
                    self._activate(
                        "context_stale",
                        reason=(
                            f"context age {context_age_ms}ms exceeds "
                            f"{self._safety_case.stale_context_ms}ms"
                        ),
                        age_ms=context_age_ms,
                    )
                )

        if not heartbeats_by_adapter:
            activations.extend(
                self._activate(
                    "heartbeat_timeout",
                    reason="no adapter heartbeat is available",
                    age_ms=None,
                )
            )
        for heartbeat in heartbeats_by_adapter:
            _require_timezone(heartbeat.timestamp)
            heartbeat_age_ms = _age_ms(now, heartbeat.timestamp)
            heartbeat_timeout_ms = min(heartbeat.ttl_ms, self._safety_case.heartbeat_timeout_ms)
            if heartbeat_age_ms > heartbeat_timeout_ms:
                activations.extend(
                    self._activate(
                        "heartbeat_timeout",
                        reason=(
                            f"heartbeat {heartbeat.adapter_id} age {heartbeat_age_ms}ms "
                            f"exceeds {heartbeat_timeout_ms}ms"
                        ),
                        age_ms=heartbeat_age_ms,
                    )
                )
            if heartbeat.status in {"failed", "stopping"}:
                activations.extend(
                    self._activate(
                        "adapter_error",
                        reason=f"heartbeat {heartbeat.adapter_id} status is {heartbeat.status}",
                        age_ms=heartbeat_age_ms,
                    )
                )
            if heartbeat.status == "safe_state_active" and heartbeat.current_safe_state is not None:
                activations.extend(
                    self._activate(
                        "adapter_error",
                        reason=(
                            f"heartbeat {heartbeat.adapter_id} reports active safe state "
                            f"{heartbeat.current_safe_state}"
                        ),
                        age_ms=heartbeat_age_ms,
                    )
                )

        if not bus_connected:
            activations.extend(
                self._activate(
                    "bus_disconnect",
                    reason="bus connection is unavailable",
                    age_ms=None,
                )
            )
        if manual_estop:
            activations.extend(
                self._activate(
                    "manual_estop",
                    reason="manual emergency stop requested",
                    age_ms=None,
                )
            )
        if contract_violation:
            activations.extend(
                self._activate(
                    "contract_violation",
                    reason="action contract violation reported",
                    age_ms=None,
                )
            )
        if sensor_dropout:
            activations.extend(
                self._activate(
                    "sensor_dropout",
                    reason="sensor dropout reported",
                    age_ms=None,
                )
            )

        deduplicated = tuple(_deduplicate(activations))
        return SafetyEvaluation(
            profile_id=self._safety_case.profile_id,
            safe=not deduplicated,
            activations=deduplicated,
        )

    def _activate(
        self,
        trigger: str,
        *,
        reason: str,
        age_ms: int | None,
    ) -> list[SafeStateActivation]:
        return [
            _activation(default, trigger=trigger, reason=reason, age_ms=age_ms)
            for default in self._safety_case.default_safe_states
            if trigger in default.triggers
        ]


def evaluate_safety_case(
    safety_case: ProfileSafetyCase,
    *,
    now: datetime,
    context: ContextUpdate | None = None,
    heartbeats: Iterable[AdapterHeartbeat] = (),
    bus_connected: bool = True,
    manual_estop: bool = False,
    contract_violation: bool = False,
    sensor_dropout: bool = False,
) -> SafetyEvaluation:
    """Evaluate a profile safety case without explicitly creating a watchdog."""

    return SafetyWatchdog(safety_case).evaluate(
        now=now,
        context=context,
        heartbeats=heartbeats,
        bus_connected=bus_connected,
        manual_estop=manual_estop,
        contract_violation=contract_violation,
        sensor_dropout=sensor_dropout,
    )


def _activation(
    default: DefaultSafeState,
    *,
    trigger: str,
    reason: str,
    age_ms: int | None,
) -> SafeStateActivation:
    return SafeStateActivation(
        target=default.target,
        safe_state=default.safe_state,
        trigger=trigger,
        reason=reason,
        age_ms=age_ms,
        requires_hardware_interlock=default.requires_hardware_interlock,
    )


def _deduplicate(
    activations: Iterable[SafeStateActivation],
) -> list[SafeStateActivation]:
    seen: set[tuple[str, str, str]] = set()
    deduplicated: list[SafeStateActivation] = []
    for activation in activations:
        key = (activation.target, activation.safe_state, activation.trigger)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(activation)
    return deduplicated


def _age_ms(now: datetime, timestamp: datetime) -> int:
    age = now - timestamp
    return max(0, int(age.total_seconds() * 1000))


def _require_timezone(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        msg = "watchdog timestamps must include timezone information"
        raise ValueError(msg)
