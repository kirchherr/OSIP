# Application Profile Template

Use this template when adding a new OSIP application profile.

Replace `xxx` with the new profile name. Keep OSIP Core untouched unless the new
profile and at least one existing profile need the same concept.

## Profile Identity

- Profile id: `xxx`
- Human name:
- Domain:
- Primary users:
- First demonstrator:

## Scope

- Perception sources:
- Context/world model entities:
- Action targets:
- Safety boundaries:
- Simulation or replay environment:

## Domain Vocabulary

- Claim labels:
- Context labels:
- Event labels:
- Action labels:
- Quality or calibration metadata:

## Standards Anchors

- Public schemas:
- Event/API standards:
- Domain standards:
- Safety or governance references:

## Adapters

- Input adapters:
- Output/action adapters:
- Simulation adapters:
- Optional external systems:

## Runtime Extension Points

- Context fusion implementation:
- Context fusion `profile_id`:
- Decision policy:
- Default Action Contract bundle:
- Decision profile `profile_id`:
- Gateway or SDK profile hooks:

## Fixtures And Scenarios

- Positive fixtures:
- Negative fixtures:
- Deterministic scenarios:
- Benchmark metrics:

## Learning Signals

- Outcome labels:
- Feedback sources:
- Post-action feedback windows:
- Reward signal derivation:
- Known confounders and delayed effects:
- False-positive / false-negative definitions:
- Action-success and action-block labels:
- Distillation candidates:
- Predictive world-model candidates:
- Reward / IRL candidates:
- Data retention, consent, privacy, and license rules:
- Dataset split and provenance requirements:
- Model-card and promotion gates:

## Autonomy Signals

- Surprise signals:
- Epistemic-value signals:
- Homeostatic / agency-maintenance signals:
- Allowed goal labels:
- Forbidden goal labels:
- Allowed goal-to-contract mappings:
- Goals requiring human confirmation:
- Autonomy-specific privacy or safety constraints:

## Acceptance Criteria

- Valid profile payloads validate through OSIP schemas or profile extensions.
- Invalid unsafe actions are rejected.
- Core tests do not require hardware, cloud APIs, or vendor SDKs.
- Profile documentation explains what stays in Core and what stays in profile.
- Learning exports cannot bypass Action Contracts or promote models without
  benchmark, model-card, registry, shadow-mode, and rollback evidence.
- Generated goals cannot bypass Action Contracts, profile permissions,
  confirmation rules, or negative autonomy tests.
