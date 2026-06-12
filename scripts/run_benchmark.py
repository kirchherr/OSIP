from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from omnisense_benchmarks import ScenarioBenchmarkRunner, write_reports


async def _run(args: argparse.Namespace) -> int:
    scenario_dir = Path(args.scenario_dir)
    runner = ScenarioBenchmarkRunner(scenario_dir)
    result = await runner.run_suite(args.scenario)
    write_reports(
        result,
        json_path=Path(args.json_output),
        markdown_path=Path(args.markdown_output),
    )
    print(f"wrote_json={args.json_output}")
    print(f"wrote_markdown={args.markdown_output}")
    print(f"passed={str(result.passed).lower()}")
    return 0 if result.passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic OSIP scenario benchmarks.")
    parser.add_argument("--scenario-dir", default="scenarios")
    parser.add_argument("--json-output", default="docs/results/latest.json")
    parser.add_argument("--markdown-output", default="docs/results/latest.md")
    parser.add_argument("--scenario", action="append", help="Scenario YAML filename to include")
    return asyncio.run(_run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
