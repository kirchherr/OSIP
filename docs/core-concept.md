# OSIP Core Concept

OSIP Core is the domain-neutral Perception-to-Action contract behind OmniSense
Runtime.

It is not a Smart-Room-only architecture and it is not a robotics framework by
itself. It is the shared semantic layer that applications can use to connect
specialized perception models, context/world modeling, and bounded actions.

```text
Perception -> Context / World Model -> Bounded Action
```

## Core Responsibilities

- Define versioned message contracts.
- Validate payloads through JSON Schema and the Python reference models.
- Keep payload semantics independent from HTTP, NATS, MQTT, ROS 2, DDS, or any
  vendor SDK.
- Represent uncertainty, latency, validity windows, quality, evidence,
  contradictions, calibration, and action boundaries.
- Provide deterministic replay and benchmark hooks.
- Keep tests simulation-first and hardware-free.

## Application Profiles

Applications attach to OSIP Core as profiles:

- `rooms`: intelligent rooms, buildings, ambient sensing, HVAC, lights, speakers,
  safety and comfort workflows.
- `physical-ai`: robots, embodied agents, mobile platforms, manipulators,
  autonomous systems, Sim2Real workflows, and physical safety bounds.
- `xxx`: a future profile slot for any domain that can be modeled as
  Perception -> Context -> Bounded Action.

Each profile owns:

- domain vocabulary,
- example fixtures,
- scenarios and benchmarks,
- adapter recommendations,
- safety and governance notes,
- optional schema extensions,
- acceptance tests.

## Core Boundary

OSIP Core must not absorb profile-specific implementation details.

Good core additions:

- generic message fields,
- versioning rules,
- validation helpers,
- transport-neutral topics,
- action-contract primitives,
- replay metadata hooks.

Profile-only additions:

- Brick-specific room labels,
- robot joint naming conventions,
- simulator-specific scene formats,
- vendor device APIs,
- learned models,
- hardware drivers.

When in doubt, put the detail in an application profile first. Promote it to
Core only when at least two profiles need the same concept.
