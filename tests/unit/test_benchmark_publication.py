from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from omnisense_benchmarks import (
    BenchmarkArtifact,
    BenchmarkPublicationManifest,
    BenchmarkRuntimeEnvironment,
    ScenarioBenchmarkRunner,
    build_publication_manifest,
)
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


async def test_publication_manifest_captures_reproducible_benchmark_evidence() -> None:
    result = await ScenarioBenchmarkRunner(SCENARIO_DIR).run_suite(["fall_candidate.yaml"])

    manifest = build_publication_manifest(
        result,
        generated_at=datetime(2026, 6, 26, 12, 0, tzinfo=UTC),
        git_commit="abc123",
        git_dirty=False,
        project_version="0.1.0",
        artifacts=(
            BenchmarkArtifact(
                kind="json_report",
                path="docs/results/latest.json",
                media_type="application/json",
            ),
            BenchmarkArtifact(
                kind="markdown_report",
                path="docs/results/latest.md",
                media_type="text/markdown",
            ),
            BenchmarkArtifact(
                kind="publication_manifest",
                path="docs/results/latest.manifest.json",
                media_type="application/json",
            ),
        ),
        runtime_environment=BenchmarkRuntimeEnvironment(
            python="3.12.0",
            platform="test-platform",
            container="test-container",
        ),
        runtime_config={"deterministic_clock": True, "scenario_dir": "scenarios"},
        scenario_dir=SCENARIO_DIR,
        scenario_names=("fall_candidate.yaml",),
    )

    assert manifest.manifest_version == "benchmark-publication/0.1"
    assert manifest.osip_schema_version == "osip/0.1"
    assert manifest.benchmark_passed is True
    assert manifest.scenario_count == 1
    assert manifest.scenario_ids == ("fall_candidate",)
    assert manifest.application_profiles == ("rooms",)
    assert manifest.runtime_environment.container == "test-container"
    assert manifest.scenario_evidence[0].expected_contexts == ("context.possible_fall",)
    assert manifest.scenario_evidence[0].proposed_actions == (
        "action.room.speaker.ask_help_needed",
    )


def test_publication_manifest_rejects_inconsistent_scenario_ids() -> None:
    payload = {
        "generated_at": "2026-06-26T12:00:00+00:00",
        "project_version": "0.1.0",
        "git_commit": "abc123",
        "git_dirty": False,
        "benchmark_passed": True,
        "scenario_count": 1,
        "scenario_ids": ["other_scenario"],
        "application_profiles": ["rooms"],
        "runtime_environment": {
            "python": "3.12.0",
            "platform": "test-platform",
        },
        "artifacts": [
            {
                "kind": "json_report",
                "path": "docs/results/latest.json",
                "media_type": "application/json",
            }
        ],
        "scenario_evidence": [
            {
                "scenario_id": "fall_candidate",
                "scenario_name": "Fall candidate scenario",
                "application_profile": "rooms",
                "passed": True,
            }
        ],
    }

    with pytest.raises(ValidationError, match="scenario_ids"):
        BenchmarkPublicationManifest.model_validate(payload)
