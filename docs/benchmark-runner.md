# Benchmark Runner

The Benchmark Runner replays deterministic scenarios through the current OSIP
MVP pipeline:

```text
Scenario -> ReplayRunner -> ContextEngine -> DecisionRuntime -> Report
```

It produces machine-readable JSON and human-readable Markdown reports under
`docs/results/`.

## Metrics

- scenario pass/fail,
- detected versus expected contexts,
- proposed versus expected actions,
- simulated first-context latency,
- simulated first-action-proposal latency,
- p50/p95/p99 summaries,
- false-positive and false-negative context/action counts,
- action-contract block count.

The first implementation uses deterministic scenario timestamps, not wall-clock
performance timing. That keeps CI stable and makes the report reproducible.
Later performance profiles can add wall-clock spans and OpenTelemetry exports.

## Run

```bash
docker compose run --rm dev make benchmark
```

Outputs:

- `docs/results/latest.json`
- `docs/results/latest.md`

## Gate

The command exits non-zero if any scenario misses expected contexts/actions,
emits unexpected contexts/actions, or violates a configured scenario latency
budget.
