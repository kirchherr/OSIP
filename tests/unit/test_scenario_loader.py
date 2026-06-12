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


def test_scenario_accepts_sim2real_domain_randomization_metadata() -> None:
    data = load_scenario_data(SCENARIO_DIR / "kitchen_burning_food.yaml")
    data["application_profile"] = "physical-ai"
    data["sim2real"] = {
        "simulator": "gazebo",
        "simulator_version": "11.13",
        "seed": 42,
        "robot_description_ref": "robots/mobile_manipulator.urdf",
        "world_description_ref": "worlds/kitchen.sdf",
        "robot_world_hash": "sha256:example",
        "sensor_noise_model": "gaussian_pose_noise_v1",
        "latency_jitter_ms": 4,
        "domain_randomization": [
            {
                "parameter": "friction.table",
                "distribution": "uniform",
                "range": {"min": 0.4, "max": 0.9, "unit": "coefficient"},
                "seed": 43,
            },
            {
                "parameter": "camera.exposure",
                "distribution": "choice",
                "choices": ["low", "nominal", "high"],
            },
        ],
    }

    scenario = ScenarioDefinition.model_validate(data)

    assert scenario.sim2real is not None
    assert scenario.sim2real.seed == 42
    assert scenario.sim2real.domain_randomization[0].parameter == "friction.table"


def test_randomization_range_must_be_ordered() -> None:
    data = load_scenario_data(SCENARIO_DIR / "kitchen_burning_food.yaml")
    data["sim2real"] = {
        "simulator": "gazebo",
        "simulator_version": "11.13",
        "seed": 42,
        "domain_randomization": [
            {
                "parameter": "mass.payload",
                "distribution": "uniform",
                "range": {"min": 2.0, "max": 1.0, "unit": "kg"},
            }
        ],
    }

    with pytest.raises(ValidationError, match="min must be less than or equal to max"):
        ScenarioDefinition.model_validate(data)
