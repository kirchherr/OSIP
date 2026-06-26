from __future__ import annotations

import argparse
import json
from pathlib import Path

from omnisense_benchmarks import (
    BenchmarkPublicationGate,
    BenchmarkPublicationGatePolicy,
    BenchmarkPublicationManifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether an OSIP benchmark publication manifest is release-ready."
    )
    parser.add_argument("manifest", nargs="?", default="docs/results/latest.manifest.json")
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--allow-unknown-git", action="store_true")
    parser.add_argument("--min-scenarios", type=int, default=1)
    args = parser.parse_args()

    manifest = BenchmarkPublicationManifest.model_validate_json(
        Path(args.manifest).read_text(encoding="utf-8")
    )
    decision = BenchmarkPublicationGate(
        BenchmarkPublicationGatePolicy(
            require_clean_git=not args.allow_dirty,
            require_known_git_commit=not args.allow_unknown_git,
            min_scenarios=args.min_scenarios,
        )
    ).evaluate(manifest)
    print(json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0 if decision.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
