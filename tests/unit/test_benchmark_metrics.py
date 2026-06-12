from __future__ import annotations

import pytest
from omnisense_benchmarks import percentile_summary


def test_percentile_summary_uses_nearest_rank() -> None:
    summary = percentile_summary([250, 70, 450, 120])

    assert summary.count == 4
    assert summary.p50_ms == 120.0
    assert summary.p95_ms == 450.0
    assert summary.p99_ms == 450.0


def test_percentile_summary_handles_empty_values() -> None:
    summary = percentile_summary([])

    assert summary.count == 0
    assert summary.p50_ms is None
    assert summary.p95_ms is None
    assert summary.p99_ms is None


def test_percentile_summary_rejects_invalid_quantile_through_helper() -> None:
    # Public API coverage: malformed quantiles are guarded inside the helper,
    # while percentile_summary itself only calls supported values.
    from omnisense_benchmarks.metrics import _nearest_rank

    with pytest.raises(ValueError, match="quantile"):
        _nearest_rank([1], 0.0)
