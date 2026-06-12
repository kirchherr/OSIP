"""Load and validate YAML scenarios."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from omnisense_sim.schemas import ScenarioDefinition


class ScenarioLoader:
    """Loads deterministic scenario definitions from YAML files."""

    def load(self, path: Path | str) -> ScenarioDefinition:
        scenario_path = Path(path)
        loaded = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            msg = f"{scenario_path} must contain a YAML object"
            raise ValueError(msg)
        return ScenarioDefinition.model_validate(loaded)

    def load_many(self, paths: list[Path | str]) -> list[ScenarioDefinition]:
        return [self.load(path) for path in paths]


def load_scenario_data(path: Path | str) -> dict[str, Any]:
    scenario_path = Path(path)
    loaded = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        msg = f"{scenario_path} must contain a YAML object"
        raise ValueError(msg)
    return loaded
