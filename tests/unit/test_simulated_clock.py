from __future__ import annotations

from datetime import UTC, datetime

import pytest
from omnisense_sim import SimulatedClock


def test_simulated_clock_advances_without_sleeping() -> None:
    clock = SimulatedClock(start_time=datetime(2026, 6, 12, tzinfo=UTC))

    now = clock.advance_to(250)

    assert clock.current_ms == 250
    assert now.isoformat() == "2026-06-12T00:00:00.250000+00:00"


def test_simulated_clock_rejects_backwards_time() -> None:
    clock = SimulatedClock()
    clock.advance_to(100)

    with pytest.raises(ValueError, match="backwards"):
        clock.advance_to(99)


def test_simulated_clock_requires_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        SimulatedClock(start_time=datetime(2026, 6, 12))
