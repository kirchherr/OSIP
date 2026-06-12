"""Benchmark metric helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PercentileSummary:
    count: int
    p50_ms: float | None
    p95_ms: float | None
    p99_ms: float | None

    def as_dict(self) -> dict[str, float | int | None]:
        return {
            "count": self.count,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
        }


def percentile_summary(values: list[int]) -> PercentileSummary:
    if not values:
        return PercentileSummary(count=0, p50_ms=None, p95_ms=None, p99_ms=None)
    sorted_values = sorted(values)
    return PercentileSummary(
        count=len(sorted_values),
        p50_ms=_nearest_rank(sorted_values, 0.50),
        p95_ms=_nearest_rank(sorted_values, 0.95),
        p99_ms=_nearest_rank(sorted_values, 0.99),
    )


def _nearest_rank(sorted_values: list[int], quantile: float) -> float:
    if not 0.0 < quantile <= 1.0:
        msg = "quantile must be in the range (0, 1]"
        raise ValueError(msg)
    index = max(1, int(_ceil(len(sorted_values) * quantile))) - 1
    return float(sorted_values[index])


def _ceil(value: float) -> int:
    as_int = int(value)
    if value == as_int:
        return as_int
    return as_int + 1
