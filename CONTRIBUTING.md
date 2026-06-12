# Contributing

Thanks for helping build OmniSense Runtime and OSIP.

## Development Setup

Use the Docker development container for reproducible local checks:

```bash
docker compose build dev
docker compose run --rm dev uv run python scripts/dev_env_check.py
```

## Before Opening A Pull Request

Run:

```bash
docker compose run --rm dev uv run pytest
docker compose run --rm dev uv run ruff check .
docker compose run --rm dev uv run mypy
docker compose run --rm dev uv run python scripts/run_benchmark.py --json-output /tmp/osip-benchmark.json --markdown-output /tmp/osip-benchmark.md
```

If OSIP schemas or Gateway endpoints change, regenerate and commit the public
contracts:

```bash
docker compose run --rm dev uv run python scripts/export_osip_schemas.py
docker compose run --rm dev uv run python scripts/export_openapi.py
```

## Architecture Rules

- Keep OSIP Core domain-neutral.
- Add domain behavior through Application Profiles.
- Keep tests simulation-first and hardware-free.
- Do not let learned models, generated goals, or adapters bypass Action
  Contracts, bounds, preconditions, cooldowns, or safe states.
- Public interfaces need typed models, validation, fixtures, negative tests, and
  documentation.

## Commit And PR Guidance

- Keep changes reviewable and scoped.
- Include tests for new public behavior.
- Update docs for public contracts, profiles, APIs, benchmarks, or governance.
- Note any benchmark, schema, or safety impact in the PR description.
