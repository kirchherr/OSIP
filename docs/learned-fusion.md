# Learned Fusion

Learned fusion is allowed in OSIP only as a controlled, offline or shadow-mode
experiment until replay, benchmark, documentation, and rollback gates pass.

The first implementation is `omnisense_context.learned_fusion`. It provides:

- `LearnedFusionCandidate`: declarative candidate metadata for one learned
  context-fusion model,
- `LearnedFusionEvaluation`: replay or benchmark evidence for that candidate,
- `LearnedFusionGatePolicy`: conservative promotion thresholds,
- `LearnedFusionPromotionGate`: deterministic gate evaluation,
- `LearnedFusionGateDecision`: machine-readable decision and rejection reasons.

This does not train, load, or execute learned models. It defines the evidence
contract that future learned fusion modules must satisfy before they can affect
runtime behavior.

## Promotion Rules

A learned fusion candidate cannot replace rule-based fusion unless:

- it has run in shadow mode,
- enough scenarios were evaluated,
- teacher/rule agreement is above policy threshold,
- schema failures, benchmark gate failures, and safety regressions are zero,
- false-positive and false-negative deltas stay within policy,
- latency regression stays within policy,
- dataset manifest, model card, benchmark report, and rollback target exist.

Draft candidates that pass gates move to `shadow`. Shadow candidates with the
required artifacts can be recommended for `approved`. Rejected candidates remain
blocked until a new candidate id or version is evaluated.

This keeps learned fusion out of the Reflex/Fast Path and preserves Action
Contracts, safety bounds, profile rules, and auditability.
