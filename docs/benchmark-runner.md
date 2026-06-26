# Benchmark Runner

The Benchmark Runner replays deterministic scenarios through the current OSIP
MVP pipeline:

```text
Scenario -> ReplayRunner -> ContextEngine -> DecisionRuntime -> Report
```

It produces machine-readable JSON, human-readable Markdown, and a publication
manifest under `docs/results/`.

## Metrics

- scenario pass/fail,
- detected versus expected contexts,
- proposed versus expected actions,
- simulated first-context latency,
- simulated first-action-proposal latency,
- p50/p95/p99 summaries,
- false-positive and false-negative context/action counts,
- action-contract block count,
- safe-state activation count,
- registered Application Profile metadata,
- optional Sim2Real metadata such as simulator, seed, robot/world descriptions,
  sensor noise model, latency jitter, and domain-randomization settings,
- per-scenario benchmark gate results, including optional `safety_watchdog`
  gates when a scenario declares safety expectations.

The first implementation uses deterministic scenario timestamps, not wall-clock
performance timing. That keeps CI stable and makes the report reproducible.
Later performance profiles can add wall-clock spans and OpenTelemetry exports.

## Publication Manifest

`docs/results/latest.manifest.json` is the reproducibility bundle for publishing
or reviewing a benchmark run. It records:

- OSIP schema version,
- project version,
- git commit and dirty-worktree flag supplied by CI or the caller,
- generated artifact paths,
- Python/platform/container runtime facts,
- selected scenario set and deterministic-clock runtime config,
- scenario IDs, Application Profiles, gate failures, latencies, contexts, actions,
  and optional Sim2Real seed/simulator metadata,
- acceptance criteria and known limitations.

The manifest is intentionally factual. It does not claim certification or real
hardware performance; it preserves enough metadata for another reviewer to rerun
or audit the deterministic benchmark.

## Publication Readiness Gate

`BenchmarkPublicationGate` evaluates whether a manifest is ready for public
artifact review. The default policy requires:

- benchmark pass,
- every scenario gate to pass,
- JSON, Markdown, and manifest artifacts to be declared,
- known git commit,
- clean git worktree flag,
- acceptance criteria and limitations.

Use the standalone checker for CI or release preparation:

```bash
uv run python scripts/check_benchmark_publication.py docs/results/latest.manifest.json
```

The GitHub Actions CI runs the deterministic benchmark with a CI-supplied git
commit, writes `/tmp/osip-benchmark.manifest.json`, and then runs the same
readiness checker. A pull request therefore fails when the scenario suite passes
but the publication manifest is not reviewable.

For local exploratory runs, reviewers can relax metadata-only checks without
weakening scenario gates:

```bash
uv run python scripts/check_benchmark_publication.py \
  docs/results/latest.manifest.json \
  --allow-dirty \
  --allow-unknown-git
```

## Run

```bash
docker compose run --rm dev make benchmark
```

Outputs:

- `docs/results/latest.json`
- `docs/results/latest.md`
- `docs/results/latest.manifest.json`

To run the benchmark plus the publication-readiness gate in one local review
step, use:

```bash
docker compose run --rm dev make benchmark-publication
```

For exploratory local review without touching `docs/results/`, override the
artifact paths:

```bash
docker compose run --rm dev make benchmark-publication \
  BENCHMARK_JSON=.pytest_cache/osip-benchmark.json \
  BENCHMARK_MD=.pytest_cache/osip-benchmark.md \
  BENCHMARK_MANIFEST=.pytest_cache/osip-benchmark.manifest.json \
  BENCHMARK_GIT_COMMIT=local
```

CI or release tooling can set reproducibility metadata explicitly:

```bash
uv run python scripts/run_benchmark.py \
  --git-commit "$GITHUB_SHA" \
  --no-git-dirty \
  --project-version "0.1.0"
```

## Gate

The command exits non-zero if any scenario misses expected contexts/actions,
emits unexpected contexts/actions, or violates a configured scenario latency
budget. If a scenario declares a `safety` section, the command also fails when
the observed watchdog result or safe-state activations differ from the expected
safe-state behavior.

The runner also fails closed when a scenario references an unregistered
Application Profile. Reports expose the failing gate instead of crashing, which
keeps CI output machine-readable.
