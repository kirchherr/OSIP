from __future__ import annotations

from omnisense_decision import PreconditionsEvaluator
from omnisense_osip import ActionContract


def contract_with(preconditions: list[str]) -> ActionContract:
    return ActionContract(
        action_id="action.test.example",
        target="test.target",
        operation="test.operate",
        risk_class="low",
        allowed_contexts=["context.test_event"],
        preconditions=preconditions,
        min_confidence=0.5,
        max_decision_latency_ms=100,
        cooldown_ms=0,
        safe_state="test.safe",
        idempotent=True,
    )


def test_preconditions_evaluator_accepts_boolean_and_numeric_facts() -> None:
    result = PreconditionsEvaluator().evaluate(
        contract_with(["hvac.available == true", "room.co2_ppm < 1200"]),
        {"hvac.available": True, "room.co2_ppm": 900},
    )

    assert result.satisfied
    assert result.failed == ()
    assert result.unsupported == ()


def test_preconditions_evaluator_blocks_missing_or_false_facts() -> None:
    result = PreconditionsEvaluator().evaluate(
        contract_with(["hvac.available == true", "room.co2_ppm < 1200"]),
        {"hvac.available": False},
    )

    assert not result.satisfied
    assert result.failed == ("hvac.available == true", "room.co2_ppm < 1200")


def test_preconditions_evaluator_rejects_unsupported_expressions() -> None:
    result = PreconditionsEvaluator().evaluate(
        contract_with(["__import__('os').system('echo nope')"]),
        {},
    )

    assert not result.satisfied
    assert result.unsupported == ("__import__('os').system('echo nope')",)
