"""Safe evaluator for small ActionContract precondition expressions."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from omnisense_osip import ActionContract

type ScalarFact = bool | int | float | str

_PRECONDITION_PATTERN = re.compile(
    r"^\s*"
    r"(?P<key>[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)*)"
    r"\s*(?P<operator>==|!=|>=|<=|>|<)\s*"
    r"(?P<value>true|false|-?\d+(?:\.\d+)?|[a-z][a-z0-9_.-]*)"
    r"\s*$"
)


@dataclass(frozen=True, slots=True)
class PreconditionResult:
    """Result of evaluating contract preconditions against runtime facts."""

    satisfied: bool
    failed: tuple[str, ...]
    unsupported: tuple[str, ...]


class PreconditionsEvaluator:
    """Evaluates a deliberately tiny, non-executable precondition language."""

    def evaluate(
        self,
        contract: ActionContract,
        facts: Mapping[str, ScalarFact],
    ) -> PreconditionResult:
        failed: list[str] = []
        unsupported: list[str] = []
        for expression in contract.preconditions:
            match = _PRECONDITION_PATTERN.fullmatch(expression)
            if match is None:
                unsupported.append(expression)
                continue

            key = match.group("key")
            operator = match.group("operator")
            expected = self._parse_literal(match.group("value"))
            actual = facts.get(key)
            if actual is None or not self._compare(actual, operator, expected):
                failed.append(expression)

        return PreconditionResult(
            satisfied=not failed and not unsupported,
            failed=tuple(failed),
            unsupported=tuple(unsupported),
        )

    @staticmethod
    def _parse_literal(raw_value: str) -> ScalarFact:
        if raw_value == "true":
            return True
        if raw_value == "false":
            return False
        try:
            if "." in raw_value:
                return float(raw_value)
            return int(raw_value)
        except ValueError:
            return raw_value

    @classmethod
    def _compare(cls, actual: ScalarFact, operator: str, expected: ScalarFact) -> bool:
        if operator == "==":
            return actual == expected
        if operator == "!=":
            return actual != expected

        actual_number = cls._as_number(actual)
        expected_number = cls._as_number(expected)
        if actual_number is None or expected_number is None:
            return False

        if operator == ">=":
            return actual_number >= expected_number
        if operator == "<=":
            return actual_number <= expected_number
        if operator == ">":
            return actual_number > expected_number
        if operator == "<":
            return actual_number < expected_number
        return False

    @staticmethod
    def _as_number(value: ScalarFact) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int | float):
            return float(value)
        return None
