# OmniSense Runtime / OSIP

OmniSense Runtime is an open, modular, simulation-first Perception-to-Action runtime built around a domain-neutral OSIP Core, attachable Application Profiles, emergent goal hypotheses, and a controlled Experience & Learning Layer.

OSIP, the OmniSense Interchange Protocol, is the stable interface between
sensory models, context/world fusion, bounded actions, and later learning from
traceable decisions, actions, results, and outcomes.

Emergent autonomy is modeled as auditable `goal.packet` generation from
surprise, epistemic value, and digital homeostasis. Generated goals are never
direct action permissions; they must pass profile policy, simulation, benchmark,
and Action Contract gates.

Application Profiles attach domain-specific vocabulary, scenarios, adapters, and
safety rules:

- `rooms`: intelligent rooms and smart environments; this is the first MVP
  demonstrator.
- `physical-ai`: robotics, embodied agents, autonomous systems, Sim2Real, and
  physical safety bounds.
- `xxx`: template slot for future attachable domains.

The Experience & Learning Layer extracts versioned traces and datasets from the
runtime loop so future models can be trained, calibrated, evaluated, documented,
and promoted without bypassing Action Contracts or safety bounds.

## Quickstart

Build the development container:

```bash
docker compose build dev
```

Check the Python environment:

```bash
docker compose run --rm dev uv run python scripts/dev_env_check.py
```

Run tests:

```bash
docker compose run --rm dev uv run pytest
```

Regenerate OSIP JSON Schemas:

```bash
docker compose run --rm dev uv run python scripts/export_osip_schemas.py
```

Run the in-memory bus tests:

```bash
docker compose run --rm dev uv run pytest tests/integration/test_in_memory_bus.py
```

Run scenario replay tests:

```bash
docker compose run --rm dev uv run pytest tests/integration/test_scenario_replay.py
```

Run context engine tests:

```bash
docker compose run --rm dev uv run pytest tests/integration/test_context_engine.py
```

Run decision runtime tests:

```bash
docker compose run --rm dev uv run pytest tests/integration/test_decision_runtime_flow.py
```

Run gateway API tests:

```bash
docker compose run --rm dev uv run pytest tests/integration/test_gateway_api.py
```

Regenerate Gateway OpenAPI:

```bash
docker compose run --rm dev make openapi
```

Run deterministic scenario benchmarks:

```bash
docker compose run --rm dev make benchmark
```

CI runs the same core gates on GitHub Actions: environment check, tests, lint,
typecheck, schema export reproducibility, OpenAPI export reproducibility, and a
deterministic benchmark run.

Open a shell:

```bash
docker compose run --rm dev bash
```

Optional NATS broker for later event-bus demos:

```bash
docker compose --profile broker up -d nats
docker compose --profile broker down
```

## Development Rules

- Read `Masterplan.md` and `AGENTS.md` before architecture or interface changes.
- Keep OSIP schemas, bus, context engine, decision runtime, simulator, gateway, adapters, and SDK modular.
- Keep learning, training, model registry access, and model promotion out of the Reflex/Fast Path.
- Keep generated goals out of direct action paths; route them through policies, benchmarks, and Action Contracts.
- Keep tests simulation-first; no real hardware or external broker should be required for core tests.
- Public interfaces need typed models, validation, fixtures, negative tests, and docs.

## Open Source

- License: Apache-2.0, see `LICENSE`.
- Contribution guide: `CONTRIBUTING.md`.
- Vulnerability reporting: `SECURITY.md`.
