---
name: osip-project
description: Use when working on OmniSense Runtime or OSIP: repository foundation, OSIP schemas, bus, context fusion, decision runtime, simulation, benchmarks, gateway APIs, open-standard alignment, scientific reproducibility, or open-source governance.
---

# OSIP Project

## Overview

Use this skill to keep Codex aligned with the OSIP/OmniSense masterplan: open interfaces first, simulation before hardware, bounded autonomy, reproducible benchmarks, and open-source-ready project hygiene.

## Required Reading

Before architectural, schema, benchmark, or public-interface work:

1. Read `Masterplan.md`.
2. Read `AGENTS.md`.
3. Read `docs/project-preparation.md` when standards, research method, governance, or public API shape matters.

## Work Loop

1. Identify the Masterplan phase: foundation, OSIP schemas, bus, simulator, context engine, decision runtime, gateway, benchmark, adapter, or dashboard.
2. Identify the public contract first: Pydantic model, JSON Schema, fixture, topic, endpoint, or Action Contract.
3. Implement the smallest module-local change that advances the phase.
4. Add positive and negative tests for public behavior.
5. Keep simulation deterministic; do not require sensors, external model APIs, network brokers, or hardware in tests.
6. Run relevant checks and report what passed or could not be run.
7. Update docs or examples for every public interface change.

## Architecture Guardrails

- Treat OSIP as the semantic core; transports are adapters.
- Keep OSIP, bus, simulator, context engine, decision runtime, gateway, adapters, and SDK separated.
- Avoid hard-coded model implementation names in core logic. Model capabilities and claims should drive behavior.
- Keep Reflex Layer free of blocking network, database, LLM, and slow filesystem calls.
- Do not execute or propose actions without Action Contracts.
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
- Telemetry: OpenTelemetry concepts and Prometheus/OpenMetrics-compatible metrics.
- Open-source hygiene: OSI license, SPDX/REUSE, CI tests, pinned dependencies, SLSA provenance path, OpenSSF Scorecard readiness.

## Scientific Method

- Prefer falsifiable acceptance criteria over demos that only look plausible.
- Use scenario replay, deterministic clocks, JSONL traces, and benchmark reports.
- Record p50/p95/p99 latencies, false positives, false negatives, schema failures, action contract blocks, and sensor dropout survival.
- Treat calibration as a first-class question; do not interpret model confidence as probability unless capability metadata says confidence is calibrated.
- Keep raw benchmark data machine-readable and results reproducible from scripts.

## Done Checklist

- Public data structures are typed and validated.
- JSON examples or fixtures exist.
- Positive and negative tests cover new public behavior.
- No hardware dependency was introduced into tests.
- Fast paths do not contain obvious blocking operations.
- Docs/specs/examples changed with public contracts.
- Final summary names files changed, design decisions, tests run, and remaining limits.
