---
name: osip-project
description: Use when working on OmniSense Runtime or OSIP: repository foundation, OSIP Core, Application Profiles such as rooms / physical-ai / xxx, schemas, bus, context fusion, decision runtime, simulation, benchmarks, gateway APIs, robotics adapters, Sim2Real, safety bounds, Experience & Learning Layer, trace-to-dataset extraction, emergent autonomy, Goal Generation Engine, goal.packet, ML lifecycle, open-standard alignment, scientific reproducibility, or open-source governance.
---

# OSIP Project

## Overview

Use this skill to keep Codex aligned with the OSIP/OmniSense masterplan: OSIP Core first, Application Profiles second, open interfaces first, simulation before hardware, bounded autonomy, Physical-AI-ready Perception-to-Action boundaries, controlled Experience-to-Learning loops, emergent goal hypotheses, reproducible benchmarks, and open-source-ready project hygiene.

## Required Reading

Before architectural, schema, benchmark, or public-interface work:

1. Read `Masterplan.md`.
2. Read `AGENTS.md`.
3. Read `docs/project-preparation.md` when standards, research method, governance, or public API shape matters.
4. Read `docs/learning-layer.md` when traces, datasets, calibration, model lifecycle, registries, model promotion, or learning-related schemas matter.
5. Read `docs/emergent-autonomy.md` when goal generation, autonomy semantics, surprise/epistemic/homeostatic scores, `goal.packet`, or goal-to-contract mapping matters.

## Work Loop

1. Identify the Masterplan phase: foundation, OSIP schemas, bus, simulator, context engine, decision runtime, gateway, benchmark, Application Profile, Experience & Learning Layer, Emergent Autonomy / Goal Generation, robotics adapter, safety-case, or dashboard.
2. Identify the boundary first: OSIP Core or a specific Application Profile (`rooms`, `physical-ai`, or future `xxx`).
3. Identify the public contract first: Pydantic model, JSON Schema, fixture, topic, endpoint, profile vocabulary, or Action Contract.
4. Implement the smallest module-local change that advances the phase.
5. Add positive and negative tests for public behavior.
6. Keep simulation deterministic; do not require sensors, external model APIs, network brokers, or hardware in tests.
7. For learning work, define trace provenance, dataset manifest, label/outcome semantics, benchmark gates, model card, registry state, shadow mode, and rollback before adding training code.
8. For autonomy work, define `goal.packet`, forbidden-goal behavior, missing-contract behavior, profile permission, review state, and goal-to-contract traceability before adding live goal execution.
9. Run relevant checks and report what passed or could not be run.
10. Update docs or examples for every public interface change.

## Architecture Guardrails

- Treat OSIP as the semantic core; transports are adapters.
- Treat Application Profiles as first-class attachments to OSIP Core. `rooms`, `physical-ai`, and future `xxx` profiles own domain vocabulary, fixtures, scenarios, adapters, and safety notes.
- Keep OSIP, bus, simulator, context engine, decision runtime, gateway, adapters, and SDK separated.
- Treat Smart Rooms as the first demonstrator, not as the limit of the architecture. Physical AI, embodied agents, robots, autonomous systems, manipulators, mobile platforms, and smart environments should share the same Perception -> Context -> Action principle.
- Promote profile concepts to OSIP Core only when at least two profiles need the same concept.
- Avoid hard-coded model implementation names in core logic. Model capabilities and claims should drive behavior.
- Treat emergent autonomy as goal-hypothesis generation, not as direct action authority.
- Treat surprise/prediction error as an investigation trigger first, not as an automatic instruction to restore a prior state.
- Do not let digital homeostasis or agency maintenance outrank people, safety cases, profile rules, or explicit human-confirmation requirements.
- Keep Reflex Layer free of blocking network, database, LLM, and slow filesystem calls.
- Keep learning, training, registry access, and model promotion out of the Reflex/Fast Path.
- Treat the chain `PerceptPacket -> ContextUpdate -> ActionProposal -> ActionCommand -> ActionResult -> Outcome` as the future Experience Trace boundary.
- Treat closed-loop feedback as `State_t + ActionContract_t + PostActionPercepts_t+delta -> Outcome_t+delta -> RewardSignal_t+delta`; preserve action ids, feedback windows, delay, uncertainty, and confounders.
- Do not execute or propose actions without Action Contracts.
- Do not execute or propose actions directly from generated goals; route goals through Decision Runtime, policy checks, Action Contracts, and audit trails.
- Do not allow learned models to bypass Action Contracts, Preconditions, Bounds, Safe States, Cooldowns, Idempotency, or profile safety cases.
- Do not promote a learned model without provenance, dataset datasheet, model card, benchmark pass, shadow-mode evaluation, rollback target, and explicit approval state.
- Do not send direct physical actuator, motor, robot, vehicle, or manipulator commands without explicit bounds, rate limits, workspace limits, stop conditions, and a safe state.
- Keep continuous or high-frequency control loops out of OSIP Core. OSIP should describe contracts, state, bounds, commands, results, and evidence; hard realtime control belongs in specialized controllers or adapters.
- Preserve schema versioning and backwards-compatibility notes.
- Represent uncertainty explicitly: claim confidence, quality, latency, validity window, evidence, contradictions, and calibration status.

## Standards Defaults

- Schemas: JSON Schema Draft 2020-12 exported from Pydantic v2 where practical.
- HTTP API: OpenAPI 3.1+ initially; track later OpenAPI versions only when tooling supports them.
- Event API: AsyncAPI 3.1+ for channels and message operations.
- Optional event envelope: CloudEvents as adapter, not as mandatory OSIP payload.
- IoT semantics: W3C WoT for Things, Properties, Actions, Events.
- Sensor/actuator semantics: W3C/OGC SOSA/SSN.
- Building semantics: Brick Schema mapping where useful.
- Physical AI / robotics: ROS 2/DDS adapter concepts, QoS as adapter configuration, URDF/SDF/OpenUSD-style robot/world descriptions, and simulator adapters such as MuJoCo, Gazebo, Isaac Sim, or PyBullet outside core dependencies.
- Safety references: ISO 10218, ISO/TS 15066, ISO 26262, and IEC 61508 as design inputs for hazards, safe states, emergency stop, audit trails, functional-safety thinking, and certification readiness; do not imply certification.
- Telemetry: OpenTelemetry concepts and Prometheus/OpenMetrics-compatible metrics.
- Emergent autonomy: active inference, expected free energy, epistemic value, intrinsic motivation, and homeostatic/allostatic control as research inputs; OSIP implementation remains contract-bounded and auditable.
- Learning provenance and lineage: W3C PROV and OpenLineage concepts for trace, dataset, job, run, and derivation metadata.
- ML lifecycle: model registry concepts such as MLflow Model Registry for versioning, aliases, tags, approval state, and rollback.
- Model/dataset documentation: Model Cards and Datasheets for Datasets.
- AI governance: NIST AI RMF as a design reference for trustworthy AI risk management; do not imply certification.
- Open-source hygiene: OSI license, SPDX/REUSE, CI tests, pinned dependencies, SLSA provenance path, OpenSSF Scorecard readiness.

## Scientific Method

- Prefer falsifiable acceptance criteria over demos that only look plausible.
- Use scenario replay, deterministic clocks, JSONL traces, and benchmark reports.
- Record p50/p95/p99 latencies, false positives, false negatives, schema failures, action contract blocks, and sensor dropout survival.
- For Physical AI, record Sim2Real assumptions, simulator version, robot/world description version, sensor noise model, domain-randomization seed, action-bound violations, collision/safe-stop events, and latency jitter.
- For learning, record source trace IDs, schema versions, scenario IDs, profile IDs, split assignment, label definitions, feature extraction version, model capability metadata, calibration status, benchmark gates, and dataset/model hashes.
- For autonomy, record goal IDs, triggering context, surprise/epistemic/homeostatic scores, prediction model version, allowed/forbidden contracts, profile approval, rejected-goal reasons, and safe-subgoal decomposition.
- For distillation, record teacher version, student scope, teacher agreement, hard-negative behavior, latency budget, and allowed action-contract surface.
- For world models, record prediction horizon, uncertainty calibration, rare-event recall, safety false negatives, and Sim2Real assumptions.
- For inverse-reinforcement or reward models, record reward source, delay, confounders, human/profile-owner review, target profile, and reward-hacking counterexamples.
- Treat calibration as a first-class question; do not interpret model confidence as probability unless capability metadata says confidence is calibrated.
- Prefer shadow-mode and replay evaluation before any learned model affects live decisions.
- Keep raw benchmark data machine-readable and results reproducible from scripts.

## Done Checklist

- Public data structures are typed and validated.
- JSON examples or fixtures exist.
- Positive and negative tests cover new public behavior.
- No hardware dependency was introduced into tests.
- Fast paths do not contain obvious blocking operations.
- Docs/specs/examples changed with public contracts.
- Final summary names files changed, design decisions, tests run, and remaining limits.
