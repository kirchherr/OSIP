from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_PYTHONPATH_ENTRIES = {
    "packages/adapters",
    "packages/benchmarks",
    "packages/embedding",
    "packages/model_plugins",
}


def test_ci_workflow_covers_all_runtime_package_paths() -> None:
    workflow = _load_workflow()
    pythonpath = workflow["jobs"]["test"]["env"]["PYTHONPATH"]
    entries = set(pythonpath.split(":"))

    assert REQUIRED_PYTHONPATH_ENTRIES <= entries


def test_ci_workflow_checks_benchmark_publication_readiness() -> None:
    workflow = _load_workflow()
    steps = workflow["jobs"]["test"]["steps"]
    commands = "\n".join(str(step.get("run", "")) for step in steps)

    assert "scripts/run_benchmark.py" in commands
    assert "--manifest-output /tmp/osip-benchmark.manifest.json" in commands
    assert '--git-commit "$GITHUB_SHA"' in commands
    assert "--no-git-dirty" in commands
    assert "scripts/check_benchmark_publication.py /tmp/osip-benchmark.manifest.json" in commands


def _load_workflow() -> dict[str, Any]:
    loaded = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded
