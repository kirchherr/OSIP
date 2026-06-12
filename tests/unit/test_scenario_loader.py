from __future__ import annotations

from pathlib import Path

import pytest
from omnisense_sim import ScenarioLoader
from omnisense_sim.scenario_loader import load_scenario_data
from omnisense_sim.schemas import ScenarioDefinition
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


def test_loader_validates_required_scenarios() -> None:
    loader = ScenarioLoader()

    scenarios = loader.load_many(
        [
            SCENARIO_DIR / "kitchen_burning_food.yaml",
            SCENARIO_DIR / "fall_candidate.yaml",
            SCENARIO_DIR / "stale_air_high_occupancy.yaml",
        ]
    )

    assert [scenario.id for scenario in scenarios] == [
        "kitchen_burning_food",
        "fall_candidate",
        "stale_air_high_occupancy",
    ]
    assert all(scenario.application_profile == "rooms" for scenario in scenarios)


def test_loader_rejects_percepts_beyond_duration() -> None:
    data = load_scenario_data(SCENARIO_DIR / "kitchen_burning_food.yaml")
    data["percepts"][0]["at_ms"] = data["duration_ms"] + 1

    with pytest.raises(ValidationError, match="duration_ms"):
        ScenarioDefinition.model_validate(data)


def test_loader_rejects_missing_claims() -> None:
    data = load_scenario_data(SCENARIO_DIR / "fall_candidate.yaml")
    data["percepts"][0]["claims"] = []

    with pytest.raises(ValidationError, match="claims"):
        ScenarioDefinition.model_validate(data)
