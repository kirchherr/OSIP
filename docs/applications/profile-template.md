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

## Fixtures And Scenarios

- Positive fixtures:
- Negative fixtures:
- Deterministic scenarios:
- Benchmark metrics:

## Acceptance Criteria

- Valid profile payloads validate through OSIP schemas or profile extensions.
- Invalid unsafe actions are rejected.
- Core tests do not require hardware, cloud APIs, or vendor SDKs.
- Profile documentation explains what stays in Core and what stays in profile.
