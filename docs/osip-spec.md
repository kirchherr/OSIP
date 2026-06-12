# OSIP v0.1 Specification

OSIP, the OmniSense Interchange Protocol, is the public contract between
specialized sensory models, the context layer, and bounded action execution.
The Python package in `packages/osip` is the reference implementation; the
exported JSON Schemas in `protocols/schemas` are the public wire contracts.

OSIP is domain-general. It is split into OSIP Core and Application Profiles.
Smart Rooms are the first profile, Physical AI is a later profile, and future
domains can attach as `xxx`-style profiles. The same Perception -> Context ->
Bounded Action contract should support each profile through additional
vocabulary, fixtures, scenarios, adapters, and safety-bounded action contracts.

## Versioning

- Current schema version: `osip/0.1`.
- Every top-level OSIP message includes `schema_version` and `type`.
- Unknown schema versions are rejected by the v0.1 reference models.
- Breaking changes require a new schema version and migration notes.

## Core Messages

- `model.capability`: describes what a sensory model can publish, including
  modalities, output claim labels, latency profile, calibration status, and
  optional embedding metadata.
- `percept.packet`: carries timestamped, quality-scored claims from one model.
  Every percept has at least one claim and claim-level confidence.
- `context.update`: carries fused room context, entities, events, global risk,
  evidence, and contradictions.
- `event.detected`: carries one detected event as a first-class message for
  event streams and low-latency subscriptions.
- `action.contract`: defines the bounded action surface. The runtime must not
  propose or execute actions outside a contract.
- `action.proposal`: recommends a contracted action for a context update.
- `action.command`: dispatches an approved action with parameters, deadline, and
  idempotency key.
- `action.result`: records the result status and execution timing.

## Open-Standard Posture

- JSON Schema Draft 2020-12 is the first public contract format.
- Application Profiles may add vocabulary, fixtures, and optional extensions, but
  Core remains the smallest shared contract.
- A concept should move from a profile into Core only when at least two profiles
  need it.
- OpenAPI and AsyncAPI specs will consume these schemas in later gateway and bus
  phases.
- CloudEvents can wrap OSIP messages at adapter boundaries, but OSIP payloads
  stay valid without a CloudEvents envelope.
- WoT, SOSA/SSN, and Brick mappings should remain adapter or mapping layers, not
  hard requirements inside the OSIP core package.
- ROS 2/DDS, URDF, SDFormat, OpenUSD, MuJoCo, Gazebo, Isaac Sim, and PyBullet
  integrations should remain adapters or benchmark environments, not core
  dependencies.
- Physical actuators require explicit Action Contracts with bounds, rate limits,
  stop conditions, and safe states before any real hardware adapter is allowed.

## Export

Regenerate public schemas with:

```bash
docker compose run --rm dev uv run python scripts/export_osip_schemas.py
```

Then verify:

```bash
docker compose run --rm dev make test
docker compose run --rm dev make lint
docker compose run --rm dev make typecheck
```
