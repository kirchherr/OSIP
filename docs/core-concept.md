# OSIP Core Concept

OSIP Core is the domain-neutral Perception-to-Action contract behind OmniSense
Runtime.

It is not a Smart-Room-only architecture and it is not a robotics framework by
itself. It is the shared semantic layer that applications can use to connect
specialized perception models, context/world modeling, emergent goal
hypotheses, bounded actions, and controlled learning from runtime experience.

```text
Perception -> Context / World Model -> Goal Hypothesis -> Bounded Action -> Result / Outcome -> Learning
```

## Core Responsibilities

- Define versioned message contracts.
- Validate payloads through JSON Schema and the Python reference models.
- Keep payload semantics independent from HTTP, NATS, MQTT, ROS 2, DDS, or any
  vendor SDK.
- Represent uncertainty, latency, validity windows, quality, evidence,
  contradictions, calibration, and action boundaries.
- Provide deterministic replay and benchmark hooks.
- Provide persistable context/world-model snapshots without making a database
  part of OSIP Core.
- Provide hooks for goal hypotheses derived from surprise, epistemic value, and
  system health without turning them into direct action authority.
- Provide trace hooks for later experience datasets, model evaluation, and
  controlled model promotion.
- Keep tests simulation-first and hardware-free.

## Emergent Autonomy

Emergent autonomy is a bounded goal-generation layer between context/world
modeling and decision making. It can produce auditable `goal.packet` candidates
from:

- prediction error or surprise,
- epistemic value or information gain,
- digital homeostasis or agency maintenance.

Generated goals are not permissions. They must be evaluated by Application
Profiles, policies, simulation/benchmark gates, and Action Contracts before any
proposal or command is emitted.

Surprise should usually produce an investigation goal first. For example, an
unexpected sensor shift can ask for more evidence or human confirmation before
it attempts to change the physical environment.

## Experience & Learning Layer

The Learning Layer turns OSIP runtime behavior into reviewable training and
evaluation material. It links `PerceptPacket`, `ContextUpdate`,
`ActionProposal`, `ActionCommand`, `ActionResult`, and later outcome or feedback
signals into versioned traces.

Learning is not part of the fast Reflex Layer. Learned models may improve future
fusion, calibration, anomaly detection, or action-success prediction only after
dataset documentation, provenance, benchmark replay, shadow-mode evaluation,
model-card documentation, registry approval, and rollback are defined.

Closed-loop sensory feedback is the key learning source. OSIP links the state
before an action, the selected or blocked Action Contract, the post-action
percepts, the evaluated outcome, and the derived reward signal into one
experience tuple. That tuple can later feed three distinct model families:

- distilled student models for faster bounded reflex decisions,
- predictive world models for action dry-runs,
- reward or inverse-reinforcement models for reviewable profile objectives.

Reward signals remain explicit, uncertain artifacts. They are not treated as
ground truth until their source, delay, evaluator version, and confounders are
documented.

## Application Profiles

Applications attach to OSIP Core as profiles:

- `rooms`: intelligent rooms, buildings, ambient sensing, HVAC, lights, speakers,
  safety and comfort workflows.
- `physical-ai`: robots, embodied agents, mobile platforms, manipulators,
  autonomous systems, Sim2Real workflows, and physical safety bounds.
- `xxx`: a future profile slot for any domain that can be modeled as
  Perception -> Context -> Bounded Action.

Each profile owns:

- an `ApplicationProfile` implementation with metadata and profile id,
- domain vocabulary,
- example fixtures,
- scenarios and benchmarks,
- adapter recommendations,
- safety and governance notes,
- optional schema extensions,
- context fusion implementations registered through profile registries,
- profile decision policies and Action Contract bundles,
- acceptance tests.

## Core Boundary

OSIP Core must not absorb profile-specific implementation details.

Good core additions:

- generic message fields,
- versioning rules,
- validation helpers,
- transport-neutral topics,
- action-contract primitives,
- goal packet primitives,
- replay metadata hooks.
- context graph snapshot metadata,
- experience trace metadata,
- dataset and model lifecycle primitives.

Profile-only additions:

- Brick-specific room labels,
- robot joint naming conventions,
- simulator-specific scene formats,
- vendor device APIs,
- context-fusion rules for one domain,
- decision-policy heuristics for one domain,
- learned models,
- profile-specific labels and outcomes for learning,
- profile-specific autonomy priorities and preference envelopes,
- hardware drivers.

When in doubt, put the detail in an application profile first. Promote it to
Core only when at least two profiles need the same concept.
