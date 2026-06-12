# OSIP Experience & Learning Layer

OSIP should not only execute a Perception-to-Action loop. It should also capture
what happened in a form that can later become training, evaluation, calibration,
and governance material for better models.

The Experience & Learning Layer is the controlled path from runtime behavior to
machine learning artifacts:

```text
PerceptPacket
  -> ContextUpdate
  -> ActionProposal
  -> ActionCommand
  -> ActionResult
  -> Post-action PerceptPackets
  -> Outcome / Feedback
  -> Reward Signal
  -> Experience Dataset
  -> Offline Training / Evaluation
  -> Model Registry
  -> Controlled Deployment
```

It is deliberately outside the fast Reflex Layer. Learning may improve future
models, fusion weights, calibration, and action-success prediction, but it must
not silently rewrite live behavior.

## Decision Trace As Dataset Factory

Every bounded action creates a natural closed-loop training opportunity. OSIP
knows the state before the action, the exact contract that was executed, and the
post-action sensory feedback that follows.

The canonical experience tuple is:

```text
ExperienceTuple = (
  State_t,
  ActionContract_t,
  PostActionPercepts_t+delta,
  Outcome_t+delta,
  RewardSignal_t+delta
)
```

- `State_t`: context graph or compact state snapshot derived from the active
  `ContextUpdate`, including evidence, contradictions, quality, latency,
  validity windows, and profile vocabulary.
- `ActionContract_t`: the bounded action that was proposed, blocked, approved,
  or executed, including preconditions, parameters, cooldown, deadline,
  idempotency key, and safe-state rules.
- `PostActionPercepts_t+delta`: the sensory feedback window after the action,
  linked back to the command and result by trace id, correlation id, scenario id,
  and time window.
- `Outcome_t+delta`: profile-specific interpretation of what happened after the
  action, such as comfort improved, smoke risk dropped, person became cold,
  object was grasped, collision was avoided, or action had no effect.
- `RewardSignal_t+delta`: an explicitly derived learning signal, never raw
  truth by default. It should include confidence, source, delay, evaluator
  version, and known confounders.

This produces unusually rich multimodal data, but it is not automatically
perfect data. Rewards can be delayed, noisy, biased, confounded, or based on
missing sensors. OSIP must preserve that uncertainty instead of pretending that
every post-action percept is a clean label.

OSIP v0.1 starts this lineage path with optional `trace_id` and
`correlation_id` fields on every top-level message plus structured
`EvidenceRef` entries on context events. The label lists remain for
compatibility, while `EvidenceRef` provides machine-readable links from fused
contexts back to source percept claims.

## Responsibilities

- Capture versioned runtime traces across perception, context, decision, action,
  result, and outcome.
- Link post-action percepts back to the action that caused or preceded them,
  including feedback windows and correlation ids.
- Extract learnable examples without losing provenance, timestamps, schema
  versions, profile id, scenario id, and model capability metadata.
- Build datasets for false positives, false negatives, action success, action
  blocks, degraded sensors, conflicting evidence, and recovery behavior.
- Derive reward signals from explicit outcome evaluators, not from hidden
  side-effects or undocumented heuristics.
- Support offline training, calibration, benchmark replay, shadow-mode
  evaluation, and controlled model promotion.
- Keep model artifacts documented through dataset datasheets and model cards.

## Non-Goals

- No online self-training in the Reflex Layer.
- No automatic production promotion of a learned model.
- No learned policy may bypass Action Contracts, preconditions, bounds, safe
  states, cooldowns, or idempotency.
- No training data export without explicit profile-level data governance,
  retention, privacy, and consent rules where real-world data is involved.

## Open Contracts

Future OSIP learning contracts should stay vendor-neutral:

- `decision.trace`: compact runtime bundle for one decision cycle, linking
  active state, selected or blocked contract, decision layer, rule/model source,
  latency, and safety checks.
- `experience.trace`: ordered event bundle linking percepts, context updates,
  proposals, commands, results, and outcomes.
- `outcome.evaluation`: profile-specific interpretation of post-action sensory
  feedback, including evaluator version, time horizon, confidence, and
  uncertainty.
- `reward.signal`: explicit training signal derived from one or more outcome
  evaluations, with delay, source, weight, confidence, and caveats.
- `experience.example`: one extracted learning example with features, labels,
  provenance, split assignment, quality flags, and policy constraints.
- `learning.dataset`: versioned dataset manifest with schema versions, source
  traces, filters, label definitions, splits, hashes, license/retention notes,
  and datasheet metadata.
- `learning.run`: training or calibration run metadata, parameters, code
  revision, inputs, metrics, and lineage.
- `model.card`: documented intended use, limitations, benchmark results,
  failure modes, calibration status, and profile compatibility.
- `model.registry.entry`: model version, aliases, approval state, rollback
  target, benchmark gate, and deployment constraints.

These should be introduced as schemas only when the runtime trace and benchmark
phases are stable enough to produce useful examples.

## Safety Gates

A model learned from OSIP experience can only be used in a runtime path after:

1. The dataset has provenance, label definitions, train/eval/test splits, and a
   datasheet.
2. The model has a model card with intended use, limitations, and benchmark
   results.
3. Scenario replay and benchmark gates pass for the target Application Profile.
4. The model has run in shadow mode against representative traces.
5. Action Contracts still block unsafe or unsupported actions.
6. Rollback and version pinning are defined before deployment.
7. Reward signals have been audited for leakage, confounding, delay, and profile
   mismatch.

## Extractable Model Families

### A. Knowledge Distillation: Deliberative To Reflex

Use the slower Deliberative Layer, ensembles, or human-reviewed traces as a
teacher and train a small student model for a narrow Reflex-Layer detection or
ranking task.

OSIP use:

- compress slow multimodal decisions into low-latency student models,
- produce tiny claim-specific models for one sensor or one context,
- reduce latency while preserving the teacher's decision boundary,
- keep the student inside the same Action Contracts as the teacher.

Required gates:

- teacher identity and version recorded in the dataset,
- student evaluated against held-out scenarios and hard negative traces,
- latency measured against the Reflex budget,
- student can only publish claims or rank existing contracts until explicitly
  approved for a broader role.

### B. Predictive World Models: Action Dry-Runs

Train a model to predict future percepts or context states:

```text
P(Percepts_t+h, Context_t+h | State_t, ActionContract_t)
```

OSIP use:

- simulate action consequences before execution,
- estimate side-effects such as comfort loss, delayed smoke signals, collision
  risk, or sensor dropout,
- improve scenario generation and benchmark coverage,
- support Physical-AI Sim2Real gap analysis.

Required gates:

- predictions are advisory until validated against replay and profile
  benchmarks,
- uncertainty must be exported with every prediction,
- world-model predictions cannot directly execute or expand action contracts,
- evaluation tracks horizon-specific error, calibration, rare-event behavior,
  and safety-relevant false negatives.

### C. Inverse Reinforcement Learning: Reward Discovery

Use successful traces, blocked-action traces, explicit feedback, and human review
to infer candidate reward functions for profile-specific goals such as comfort,
safety, energy efficiency, or manipulation success.

OSIP use:

- discover implicit comfort and safety preferences in a room,
- bootstrap a new profile or location with a prior reward model,
- compare rule-based behavior against inferred objectives,
- make hidden trade-offs reviewable instead of leaving them in code.

Required gates:

- inferred rewards are candidate models, not normative truth,
- human or profile-owner review is required before optimization against them,
- transfer requires target-profile validation and drift monitoring,
- reward models must never optimize around Action Contracts or safety bounds.

## Learning Tasks

Near-term learning candidates:

- confidence calibration per model and claim label,
- fusion-weight estimation from repeated scenarios,
- false-positive and false-negative mining,
- action-success and action-block prediction,
- sensor dropout and degraded-quality robustness analysis,
- profile-specific context pattern discovery for human review.

Later learning candidates:

- teacher-student distillation from Deliberative decisions into small
  low-latency models,
- predictive world models for action dry-runs and future percept forecasts,
- inverse-reinforcement or reward models for comfort, safety, energy, and
  profile-specific objectives,
- learned fusion modules that replace selected rule weights after benchmark
  approval,
- learned anomaly detection for unseen sensor conflicts,
- recommendation of new Action Contracts or preconditions for human review,
- Sim2Real gap analysis for Physical AI profiles.

## Standards Anchors

- W3C PROV for provenance and derivation.
- OpenLineage for open lineage metadata around dataset, job, and run entities.
- MLflow Model Registry concepts for model lifecycle, lineage, versioning,
  aliases, tags, and controlled promotion.
- NIST AI Risk Management Framework for trustworthiness and risk-management
  thinking around AI systems.
- Model Cards for transparent model reporting.
- Datasheets for Datasets for dataset motivation, composition, collection,
  recommended use, and limitations.
- Knowledge Distillation for teacher-student model compression.
- World Models for predictive environment modeling and policy dry-runs.
- Inverse Reinforcement Learning / reward learning for deriving candidate
  reward functions from demonstrations or successful traces.

## Placement In OSIP

OSIP Core should define only the generic trace and learning contract primitives.
Application Profiles own domain-specific labels, sensitive-data policy, outcome
definitions, evaluation metrics, and safety cases.

The first implementation should be a deterministic trace exporter and dataset
manifest generator. Model training itself should remain optional and outside
core CI until the MVP pipeline, benchmark runner, and governance contracts are
solid.
