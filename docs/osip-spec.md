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
OSIP also prepares a controlled Experience & Learning Layer that can turn
runtime traces into datasets and evaluated models without changing live behavior
automatically.
Emergent autonomy is treated as future goal-hypothesis generation through
`goal.packet`, not as direct action authority.

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

Future learning-related messages should stay out of v0.1 runtime-critical paths:

- `goal.packet`: records a generated goal hypothesis from surprise, epistemic
  value, or homeostatic pressure. It includes triggering context, scores,
  target, allowed/forbidden contract classes, expiry, safety class, review
  state, evidence, and contradictions.
- `experience.trace`: links percepts, context updates, proposals, commands,
  results, and outcomes for replay and learning.
- `decision.trace`: records one decision cycle, including active state,
  selected or blocked Action Contract, decision source, latency, and safety
  checks.
- `outcome.evaluation`: interprets post-action percepts over a profile-defined
  feedback window.
- `reward.signal`: stores explicit learning signal metadata, including source,
  delay, confidence, evaluator version, and known confounders.
- `learning.dataset`: describes versioned datasets, source traces, labels,
  splits, provenance, and hashes.
- `learning.run`: records training, calibration, or evaluation runs.
- `model.registry.entry`: records model version, approval state, benchmark gate,
  aliases, rollback target, and deployment constraints.

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
- Generated goals must be routed through profiles, policies, Decision Runtime,
  Action Contracts, benchmark evidence, and audit trails before they can affect
  the world.
- `goal.packet` may suggest information gathering or human confirmation even
  when no physical action is allowed.
- Learning lineage should align with W3C PROV and OpenLineage concepts.
- Learned models require dataset documentation, model cards, benchmark results,
  shadow-mode evaluation, registry state, and rollback before runtime use.
- Learned models must not bypass Action Contracts, safety bounds, preconditions,
  or profile safety cases.

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
