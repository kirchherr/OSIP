# OmniSense Runtime / OSIP

OmniSense Runtime is an open, modular, simulation-first Perception-to-Action runtime built around a domain-neutral OSIP Core, attachable Application Profiles, and a controlled Experience & Learning Layer.

OSIP, the OmniSense Interchange Protocol, is the stable interface between
sensory models, context/world fusion, bounded actions, and later learning from
traceable decisions, actions, results, and outcomes.

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
- Keep tests simulation-first; no real hardware or external broker should be required for core tests.
- Public interfaces need typed models, validation, fixtures, negative tests, and docs.
