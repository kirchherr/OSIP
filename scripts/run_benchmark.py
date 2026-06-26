from __future__ import annotations

import argparse
import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

from omnisense_benchmarks import (
    BenchmarkArtifact,
    ScenarioBenchmarkRunner,
    build_publication_manifest,
    default_runtime_environment,
    write_publication_manifest,
    write_reports,
)


async def _run(args: argparse.Namespace) -> int:
    scenario_dir = Path(args.scenario_dir)
    json_path = Path(args.json_output)
    markdown_path = Path(args.markdown_output)
    manifest_path = Path(args.manifest_output)
    scenario_names = tuple(args.scenario) if args.scenario else None

    runner = ScenarioBenchmarkRunner(scenario_dir)
    result = await runner.run_suite(args.scenario)
    write_reports(
        result,
        json_path=json_path,
        markdown_path=markdown_path,
    )
    manifest = build_publication_manifest(
        result,
        generated_at=datetime.now(UTC),
        git_commit=args.git_commit,
        git_dirty=args.git_dirty,
        project_version=args.project_version,
        artifacts=(
            BenchmarkArtifact(
                kind="json_report",
                path=str(json_path),
                media_type="application/json",
            ),
            BenchmarkArtifact(
                kind="markdown_report",
                path=str(markdown_path),
                media_type="text/markdown",
            ),
            BenchmarkArtifact(
                kind="publication_manifest",
                path=str(manifest_path),
                media_type="application/json",
            ),
        ),
        runtime_environment=default_runtime_environment(container=args.container),
        runtime_config={
            "scenario_dir": str(scenario_dir),
            "selected_scenarios": ",".join(scenario_names) if scenario_names else None,
            "deterministic_clock": True,
        },
        scenario_dir=scenario_dir,
        scenario_names=scenario_names,
    )
    write_publication_manifest(manifest, manifest_path)
    print(f"wrote_json={args.json_output}")
    print(f"wrote_markdown={args.markdown_output}")
    print(f"wrote_manifest={args.manifest_output}")
    print(f"passed={str(result.passed).lower()}")
    return 0 if result.passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic OSIP scenario benchmarks.")
    parser.add_argument("--scenario-dir", default="scenarios")
    parser.add_argument("--json-output", default="docs/results/latest.json")
    parser.add_argument("--markdown-output", default="docs/results/latest.md")
    parser.add_argument("--manifest-output", default="docs/results/latest.manifest.json")
    parser.add_argument("--scenario", action="append", help="Scenario YAML filename to include")
    parser.add_argument(
        "--project-version", default=os.environ.get("OSIP_PROJECT_VERSION", "0.1.0")
    )
    parser.add_argument(
        "--git-commit",
        default=os.environ.get("OSIP_BENCHMARK_GIT_COMMIT")
        or os.environ.get("GITHUB_SHA")
        or "unknown",
    )
    parser.add_argument(
        "--git-dirty",
        action=argparse.BooleanOptionalAction,
        default=_env_bool("OSIP_BENCHMARK_GIT_DIRTY"),
    )
    parser.add_argument("--container", default=os.environ.get("OSIP_BENCHMARK_CONTAINER"))
    return asyncio.run(_run(parser.parse_args()))


def _env_bool(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "dirty"}


if __name__ == "__main__":
    raise SystemExit(main())
