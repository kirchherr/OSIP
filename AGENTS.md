# AGENTS.md - OmniSense Runtime / OSIP

## Project Goal

Build OmniSense Runtime: an open, modular, simulation-first Perception-to-Action runtime for intelligent rooms. Specialized sensory models publish OSIP Percept Packets; a context engine fuses them into operational room context; a bounded decision runtime triggers actions only through Action Contracts.

## Read First

- Read `Masterplan.md` before architectural or interface work.
- Read `docs/project-preparation.md` before changing public schemas, protocols, benchmarks, source governance, or standards alignment.
- Use the repo skill `osip-project` when working on OSIP schemas, bus, context fusion, decision runtime, simulation, benchmarks, or open-standard interface decisions.
- Check for a more specific `AGENTS.md` or `AGENTS.override.md` in subdirectories if the repository grows.

## Architecture Rules

- Interface first: define public schemas, message contracts, and examples before internal logic.
- Simulation first: tests and demos must not require real hardware.
- Modular by default: keep OSIP, bus, simulator, context engine, decision runtime, gateway, adapters, and SDK separate.
- Transport agnostic: OSIP semantics live in schemas and vocabulary, not in HTTP, NATS, MQTT, or ROS 2 code.
- Version every public schema and avoid breaking `schema_version` without migration notes.
- No LLM, database, cloud API, or blocking network call in Reflex Layer or other fast-path decision logic.
- No action without an `action.contract`; check preconditions, confidence, cooldown, idempotency, deadline, rollback or safe state where possible.
- Treat missing, late, duplicate, degraded, or conflicting sensor data as expected runtime conditions.
- Public interfaces need typed models, validation, examples, negative tests, and documentation.

## Standards Posture

- Prefer open standards and vendor-neutral protocols. If a needed interface does not exist, design a minimal open OSIP extension with versioning and JSON Schema.
- Align HTTP APIs with OpenAPI, event APIs with AsyncAPI, event envelopes optionally with CloudEvents, and schema exports with JSON Schema.
- Align sensor/actuator semantics with W3C SOSA/SSN and W3C WoT where practical.
- Align smart-building vocabulary with Brick where practical, while keeping OSIP labels stable and lightweight.
- Expose observability through OpenTelemetry concepts and Prometheus/OpenMetrics-compatible metrics.
- Keep open-source governance reviewable: clear license, SPDX/REUSE-compatible notices, dependency pinning, CI tests, and supply-chain provenance planning.

## Development Flow

1. Identify the affected Masterplan phase and module boundary.
2. Start from contracts: Pydantic model, JSON example, JSON Schema, OpenAPI/AsyncAPI entry, or topic contract.
3. Add or update positive and negative tests before or alongside implementation.
4. Keep changes small enough for review.
5. Run the narrowest relevant checks; once foundation exists, prefer `make test`, `make lint`, `make typecheck`, and `make benchmark`.
6. Document changed public interfaces in `docs/` or `protocols/`.

## Done Means

- Typed public data structures exist.
- Runtime validation exists.
- At least one positive and one negative test cover new public behavior.
- Relevant tests pass, or the reason they could not be run is documented.
- Fast paths avoid obvious blocking calls and shared-state races.
- Public schemas, examples, or docs are updated.
- Summary includes changed files, design decisions, tests run, and known limits.

## Do Not

- Do not build a monolithic `main.py`.
- Do not hard-code specific model implementations into the context engine.
- Do not make hardware, cloud services, or external model APIs required for tests.
- Do not mix simulation-only behavior with production code without explicit boundaries.
- Do not add proprietary lock-in where an open interface or adapter is feasible.
