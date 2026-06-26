"""Publication manifest contracts for reproducible OSIP benchmarks."""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, Self

from omnisense_osip import OSIP_SCHEMA_VERSION
from omnisense_osip.schemas import OSIPModel
from omnisense_sim import ScenarioLoader
from omnisense_sim.schemas import Sim2RealMetadata
from pydantic import Field, model_validator

from omnisense_benchmarks.runner import ScenarioBenchmarkResult, SuiteBenchmarkResult

type BenchmarkArtifactKind = Literal["json_report", "markdown_report", "publication_manifest"]

DEFAULT_ACCEPTANCE_CRITERIA = (
    "all expected contexts are detected",
    "no unexpected contexts are emitted",
    "all expected actions are proposed",
    "no unexpected actions are proposed",
    "scenario latency budgets pass when declared",
    "safety watchdog expectations pass when declared",
)

DEFAULT_LIMITATIONS = (
    "MVP benchmarks use deterministic scenario time, not wall-clock performance timing.",
    "Rooms scenarios do not require real sensors, actuators, brokers, or hardware.",
    "Physical-AI Sim2Real metadata is optional until physical-ai benchmark scenarios are added.",
)


class BenchmarkArtifact(OSIPModel):
    """Reference to one generated benchmark publication artifact."""

    kind: BenchmarkArtifactKind
    path: str = Field(min_length=1)
    media_type: str = Field(min_length=1)


class BenchmarkRuntimeEnvironment(OSIPModel):
    """Runtime environment metadata needed to reproduce a benchmark run."""

    runner: str = Field(default="omnisense_benchmarks", min_length=1)
    python: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    container: str | None = Field(default=None, min_length=1)


class BenchmarkScenarioEvidence(OSIPModel):
    """Scenario-level evidence included in a publication manifest."""

    scenario_id: str = Field(min_length=1)
    scenario_name: str = Field(min_length=1)
    application_profile: str = Field(min_length=1)
    application_profile_version: str | None = Field(default=None, min_length=1)
    passed: bool
    gate_failures: tuple[str, ...] = Field(default_factory=tuple)
    expected_contexts: tuple[str, ...] = Field(default_factory=tuple)
    detected_contexts: tuple[str, ...] = Field(default_factory=tuple)
    expected_actions: tuple[str, ...] = Field(default_factory=tuple)
    proposed_actions: tuple[str, ...] = Field(default_factory=tuple)
    first_context_latency_ms: int | None = Field(default=None, ge=0)
    first_action_proposal_latency_ms: int | None = Field(default=None, ge=0)
    scenario_seed: int | None = Field(default=None, ge=0)
    simulator: str | None = Field(default=None, min_length=1)
    simulator_version: str | None = Field(default=None, min_length=1)
    robot_description_ref: str | None = Field(default=None, min_length=1)
    world_description_ref: str | None = Field(default=None, min_length=1)
    robot_world_hash: str | None = Field(default=None, min_length=1)
    sensor_noise_model: str | None = Field(default=None, min_length=1)
    latency_jitter_ms: int | None = Field(default=None, ge=0)
    domain_randomization_parameters: tuple[str, ...] = Field(default_factory=tuple)


class BenchmarkPublicationManifest(OSIPModel):
    """Machine-readable reproducibility manifest for one benchmark publication."""

    manifest_version: Literal["benchmark-publication/0.1"] = "benchmark-publication/0.1"
    type: Literal["benchmark.publication_manifest"] = "benchmark.publication_manifest"
    osip_schema_version: Literal["osip/0.1"] = OSIP_SCHEMA_VERSION
    generated_at: datetime
    project_version: str = Field(min_length=1)
    git_commit: str = Field(min_length=1)
    git_dirty: bool
    benchmark_passed: bool
    scenario_count: int = Field(gt=0)
    scenario_ids: tuple[str, ...] = Field(min_length=1)
    application_profiles: tuple[str, ...] = Field(min_length=1)
    runtime_environment: BenchmarkRuntimeEnvironment
    runtime_config: dict[str, str | int | bool | None] = Field(default_factory=dict)
    artifacts: tuple[BenchmarkArtifact, ...] = Field(min_length=1)
    acceptance_criteria: tuple[str, ...] = Field(default=DEFAULT_ACCEPTANCE_CRITERIA)
    scenario_evidence: tuple[BenchmarkScenarioEvidence, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(default=DEFAULT_LIMITATIONS)

    @model_validator(mode="after")
    def validate_manifest_consistency(self) -> Self:
        evidence_ids = tuple(evidence.scenario_id for evidence in self.scenario_evidence)
        if self.scenario_count != len(self.scenario_evidence):
            msg = "scenario_count must match scenario_evidence length"
            raise ValueError(msg)
        if self.scenario_ids != evidence_ids:
            msg = "scenario_ids must match scenario_evidence order"
            raise ValueError(msg)
        if self.benchmark_passed != all(evidence.passed for evidence in self.scenario_evidence):
            msg = "benchmark_passed must match scenario evidence"
            raise ValueError(msg)
        return self


def default_runtime_environment(*, container: str | None = None) -> BenchmarkRuntimeEnvironment:
    """Collect local runtime facts without invoking external commands."""

    return BenchmarkRuntimeEnvironment(
        python=sys.version.split()[0],
        platform=platform.platform(),
        container=container,
    )


def build_publication_manifest(
    result: SuiteBenchmarkResult,
    *,
    generated_at: datetime,
    git_commit: str,
    git_dirty: bool,
    project_version: str,
    artifacts: tuple[BenchmarkArtifact, ...],
    runtime_environment: BenchmarkRuntimeEnvironment | None = None,
    runtime_config: dict[str, str | int | bool | None] | None = None,
    scenario_dir: Path | None = None,
    scenario_names: tuple[str, ...] | None = None,
    limitations: tuple[str, ...] = DEFAULT_LIMITATIONS,
) -> BenchmarkPublicationManifest:
    """Build a publication manifest from a completed benchmark suite result."""

    sim2real_by_scenario = _load_sim2real_metadata(scenario_dir, scenario_names)
    scenario_evidence = tuple(
        _scenario_evidence(scenario, sim2real_by_scenario.get(scenario.scenario_id))
        for scenario in result.scenarios
    )
    return BenchmarkPublicationManifest(
        generated_at=generated_at,
        project_version=project_version,
        git_commit=git_commit,
        git_dirty=git_dirty,
        benchmark_passed=result.passed,
        scenario_count=result.summary.scenario_count,
        scenario_ids=tuple(scenario.scenario_id for scenario in result.scenarios),
        application_profiles=result.summary.application_profiles,
        runtime_environment=runtime_environment or default_runtime_environment(),
        runtime_config=runtime_config or {},
        artifacts=artifacts,
        scenario_evidence=scenario_evidence,
        limitations=limitations,
    )


def write_publication_manifest(manifest: BenchmarkPublicationManifest, path: Path) -> None:
    """Write a publication manifest as stable, machine-readable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _scenario_evidence(
    scenario: ScenarioBenchmarkResult,
    sim2real: Sim2RealMetadata | None,
) -> BenchmarkScenarioEvidence:
    return BenchmarkScenarioEvidence(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.scenario_name,
        application_profile=scenario.application_profile,
        application_profile_version=scenario.application_profile_version,
        passed=scenario.passed,
        gate_failures=tuple(gate.name for gate in scenario.gates if not gate.passed),
        expected_contexts=scenario.expected_contexts,
        detected_contexts=scenario.detected_contexts,
        expected_actions=scenario.expected_actions,
        proposed_actions=scenario.proposed_actions,
        first_context_latency_ms=scenario.first_context_latency_ms,
        first_action_proposal_latency_ms=scenario.first_action_proposal_latency_ms,
        scenario_seed=sim2real.seed if sim2real is not None else None,
        simulator=sim2real.simulator if sim2real is not None else None,
        simulator_version=sim2real.simulator_version if sim2real is not None else None,
        robot_description_ref=sim2real.robot_description_ref if sim2real is not None else None,
        world_description_ref=sim2real.world_description_ref if sim2real is not None else None,
        robot_world_hash=sim2real.robot_world_hash if sim2real is not None else None,
        sensor_noise_model=sim2real.sensor_noise_model if sim2real is not None else None,
        latency_jitter_ms=sim2real.latency_jitter_ms if sim2real is not None else None,
        domain_randomization_parameters=(
            tuple(setting.parameter for setting in sim2real.domain_randomization)
            if sim2real is not None
            else ()
        ),
    )


def _load_sim2real_metadata(
    scenario_dir: Path | None,
    scenario_names: tuple[str, ...] | None,
) -> dict[str, Sim2RealMetadata]:
    if scenario_dir is None:
        return {}

    names = scenario_names or tuple(sorted(path.name for path in scenario_dir.glob("*.yaml")))
    loader = ScenarioLoader()
    metadata: dict[str, Sim2RealMetadata] = {}
    for name in names:
        scenario = loader.load(scenario_dir / name)
        if scenario.sim2real is not None:
            metadata[scenario.id] = scenario.sim2real
    return metadata
