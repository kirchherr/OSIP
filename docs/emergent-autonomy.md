# Emergent Autonomy

Emergent autonomy is OSIP's controlled path from perception to self-generated
goal hypotheses. It does not mean unbounded self-directed action. It means the
runtime can detect when its world model is surprised, uncertain, or losing
operational capability, then generate a bounded `goal.packet` for later
deliberation.

```text
PerceptPacket
  -> Context / World Model
  -> Goal Generation Engine
  -> GoalPacket
  -> Deliberative / Decision Runtime
  -> Action Contracts
  -> ActionProposal / ActionCommand
  -> ActionResult / Outcome
  -> Experience & Learning
```

## Autonomy Definition

OSIP autonomy is bounded, inspectable, and contract-mediated:

- The system may generate goals from perception, uncertainty, prediction error,
  and system health.
- The system may not execute arbitrary actions to satisfy those goals.
- Every physical or user-visible action still requires an Action Contract,
  preconditions, cooldown/idempotency, safety bounds, and rollback or safe-state
  behavior where relevant.
- Every generated goal is a hypothesis with provenance, confidence, expiry, and
  a safety class.

Emergent autonomy therefore lives between context fusion and decision making. It
adds a goal layer, not a shortcut around safety.

## Goal Generation Engine

The Goal Generation Engine (GGE) evaluates three families of intrinsic signals:

### 1. Surprise / Prediction Error

The runtime compares predicted context or percepts against observed
`PerceptPacket` and `ContextUpdate` evidence. High prediction error can generate
goals such as:

- explain an unexpected state transition,
- verify whether a surprising event is real,
- update the world model through additional sensing,
- suppress false assumptions after repeated mismatch.

Important boundary: OSIP should not blindly "restore normality." Sometimes the
surprising state is desirable, human-initiated, or safer than the predicted
state. Surprise creates an investigation goal, not an automatic correction.

### 2. Epistemic Value / Information Gain

The runtime detects low confidence, contradictions, missing modalities, or high
ambiguity in a context graph. It can generate goals such as:

- reduce ambiguity in a room zone,
- request another modality,
- increase sampling rate for a bounded duration,
- ask for human confirmation when sensing cannot resolve the uncertainty.

Epistemic goals are especially useful for Physical AI, where viewpoint, tactile
feedback, depth, and proprioception can change the confidence of the world
model.

### 3. Digital Homeostasis / Agency Maintenance

The runtime monitors its own sensing and acting capability:

- sensor drift,
- camera obstruction,
- degraded model latency,
- overloaded node,
- missing actuator acknowledgement,
- stale calibration,
- repeated action-contract blocks.

These can generate maintenance goals such as `goal.restore_sensor_quality`,
`goal.reduce_runtime_load`, or `goal.request_calibration`.

Homeostasis is subordinate to profile safety. The system may maintain its
operational capability, but not at the expense of people, safety rules, or
explicit profile priorities.

## GoalPacket Draft

Future OSIP goal messages should be vendor-neutral and schema-versioned:

```json
{
  "schema_version": "osip/0.1",
  "type": "goal.packet",
  "goal_id": "goal_000123",
  "based_on_context": "ctx_kitchen_000042",
  "profile": "rooms",
  "label": "goal.reduce_ambiguity",
  "source": "goal_generation_engine",
  "priority": "normal",
  "confidence": 0.76,
  "scores": {
    "surprise": 0.31,
    "epistemic_value": 0.84,
    "homeostatic_pressure": 0.12
  },
  "target": {
    "room": "kitchen",
    "zone": "stove_area"
  },
  "constraints": {
    "allowed_contexts": ["context.sensor_conflict"],
    "allowed_action_contracts": ["action.request_more_evidence"],
    "forbidden_action_contracts": ["action.physical_destructive_probe"],
    "expires_in_ms": 5000,
    "requires_confirmation": false
  },
  "evidence": ["chemical.air.smoke_like_pattern"],
  "contradictions": ["vision.no_smoke_visible"],
  "reason": "Smoke-like chemistry conflicts with visual no-smoke evidence."
}
```

The exact schema should be introduced only after MVP benchmark traces exist. The
draft contract is enough to align architecture and roadmap now.

## Contract-Mediated Goal Handling

Goal handling should use this order:

1. Generate a goal from surprise, epistemic value, or homeostatic pressure.
2. Check whether the goal is allowed by the Application Profile.
3. Search only registered Action Contracts that can satisfy the goal.
4. Reject or decompose the goal if no safe contract exists.
5. Prefer information-gathering subgoals before high-impact actions.
6. Publish a normal `ActionProposal`; do not create an out-of-band action path.
7. Record the goal and outcome as an Experience Trace.

Example:

- Goal: "explain unknown chemical pattern in zone 3."
- Unsafe direct action: "open wall."
- Contract check: no such contract exists.
- Safe subgoal: "request additional spectral sample" or "ask human
  confirmation."

## Standards And Research Anchors

- Active inference and Expected Free Energy for action selection under
  uncertainty and epistemic value.
- Intrinsic motivation literature for information-seeking behavior.
- Homeostasis/allostasis as inspiration for agency maintenance and operational
  health, translated into explicit system-health metrics.
- NIST AI RMF for risk-management thinking around autonomous AI behavior.
- OSIP Action Contracts, benchmark replay, model cards, dataset datasheets, and
  audit trails as the practical governance layer.

## Guardrails

- No hidden values: profile priors and preference envelopes must be explicit.
- No raw "minimize surprise" command: surprise generates investigation goals,
  not automatic world correction.
- No self-preservation override: digital homeostasis cannot outrank human
  safety or profile safety cases.
- No physical action without an Action Contract.
- No learned or generated goal may bypass the Decision Runtime.
- No automatic goal-policy promotion without simulation, benchmark, shadow mode,
  audit trail, rollback, and review.

## First Implementation Slice

The first implementation should be a deterministic `GoalGenerationEngine` that:

- consumes `ContextUpdate` and later world-model prediction metadata,
- computes transparent `surprise_score`, `epistemic_score`, and
  `homeostatic_score`,
- emits draft `GoalPacket` objects or blocks with reasons,
- maps goals only to existing Action Contracts,
- includes positive and negative tests for forbidden goals and missing contracts.

This can come after the benchmark runner, because reliable autonomy needs
measurable replay, latency, false-positive/false-negative, and action-block
reports.
