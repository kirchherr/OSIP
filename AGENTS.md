# AGENTS.md - OmniSense Runtime / OSIP

## Project Goal

Build OmniSense Runtime: an open, modular, simulation-first Perception-to-Action runtime with a domain-neutral OSIP Core and attachable Application Profiles. The first profile is `rooms`; later profiles include `physical-ai` and future domains such as `xxx`. Specialized sensory, proprioceptive, and kinematic models publish OSIP Percept Packets; a context engine fuses them into operational context/world state; a bounded decision runtime triggers actions only through Action Contracts and safety bounds.

## Read First

- Read `Masterplan.md` before architectural or interface work.
- Read `docs/project-preparation.md` before changing public schemas, protocols, benchmarks, source governance, or standards alignment.
- Use the repo skill `osip-project` when working on OSIP Core, Application Profiles, OSIP schemas, bus, context fusion, decision runtime, simulation, benchmarks, Physical AI, robotics adapters, safety bounds, or open-standard interface decisions.
- Check for a more specific `AGENTS.md` or `AGENTS.override.md` in subdirectories if the repository grows.

## Architecture Rules

- Interface first: define public schemas, message contracts, and examples before internal logic.
- Simulation first: tests and demos must not require real hardware.
- Modular by default: keep OSIP, bus, simulator, context engine, decision runtime, gateway, adapters, and SDK separate.
- Profile-aware by default: keep OSIP Core domain-neutral; put Rooms, Physical AI, and future XXX domain details into Application Profiles.
- Transport agnostic: OSIP semantics live in schemas and vocabulary, not in HTTP, NATS, MQTT, or ROS 2 code.
- Physical-AI aware: design Perception -> Context -> Action contracts so they can later support robot/world state, 3D transforms, proprioception, manipulation, navigation, and continuous-control boundaries without making hardware mandatory.
- Promote a concept from profile to Core only when at least two profiles need it.
- Version every public schema and avoid breaking `schema_version` without migration notes.
- No LLM, database, cloud API, or blocking network call in Reflex Layer or other fast-path decision logic.
- No action without an `action.contract`; check preconditions, confidence, cooldown, idempotency, deadline, rollback or safe state where possible.
- No direct actuator, motor, robot, vehicle, or manipulator command without explicit bounds, rate limits, workspace limits, stop conditions, and a safe-state path.
- Treat missing, late, duplicate, degraded, or conflicting sensor data as expected runtime conditions.
- Public interfaces need typed models, validation, examples, negative tests, and documentation.

## Standards Posture

- Prefer open standards and vendor-neutral protocols. If a needed interface does not exist, design a minimal open OSIP extension with versioning and JSON Schema.
- Align HTTP APIs with OpenAPI, event APIs with AsyncAPI, event envelopes optionally with CloudEvents, and schema exports with JSON Schema.
- Align sensor/actuator semantics with W3C SOSA/SSN and W3C WoT where practical.
- Align smart-building vocabulary with Brick where practical, while keeping OSIP labels stable and lightweight.
- Align Physical AI adapters with ROS 2/DDS concepts, QoS as adapter configuration, URDF/SDF/OpenUSD-style scene and robot descriptions, and simulator-first workflows such as MuJoCo, Gazebo, Isaac Sim, or PyBullet without adding them to core tests by default.
- Treat safety standards such as ISO 10218, ISO/TS 15066, ISO 26262, and IEC 61508 as design references for hazards, bounds, emergency stop, auditability, and functional safety, not as claims of certification.
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
- Do not let one application profile pollute OSIP Core with domain-specific vocabulary, simulator requirements, or vendor APIs.
- Do not make hardware, cloud services, or external model APIs required for tests.
- Do not couple OSIP Core directly to MuJoCo, Gazebo, Isaac Sim, PyBullet, ROS 2, DDS, or any robot vendor SDK; use adapters.
- Do not model continuous physical control as free-form arbitrary commands; use bounded contracts and simulator-verified examples first.
- Do not mix simulation-only behavior with production code without explicit boundaries.
- Do not add proprietary lock-in where an open interface or adapter is feasible.
