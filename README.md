# OmniSense Runtime / OSIP

OmniSense Runtime is an open, modular, simulation-first Perception-to-Action runtime for intelligent rooms. OSIP, the OmniSense Interchange Protocol, is the stable interface between sensory models, context fusion, and bounded actions.

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
- Keep tests simulation-first; no real hardware or external broker should be required for core tests.
- Public interfaces need typed models, validation, fixtures, negative tests, and docs.
