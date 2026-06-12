# Application Profile: Physical AI

The `physical-ai` profile applies OSIP Core to embodied agents, robots, mobile
platforms, manipulators, autonomous systems, and Sim2Real workflows.

OSIP Core remains the shared contract. Physical-AI-specific details live in this
profile, simulator adapters, and later robotics bridges.

## Domain Mapping

| OSIP Layer | Physical AI / Robotics |
| --- | --- |
| Perception | cameras, LiDAR, radar, IMU, joint states, force/torque, tactile arrays |
| Context | world model, 3D objects, transforms, robot state, graspability, obstacles |
| Action | mobile-base commands, manipulator actions, gripper control, safe stop |
| Safety | workspace limits, velocity/force/rate bounds, collision zones, emergency stop |
| Simulation | Sim2Real, domain randomization, physics simulation, robot/world descriptions |

## Principles

- Treat simulators, robot middleware, and vendor SDKs as adapters.
- Never require real hardware in core tests.
- Do not model physical control as arbitrary free-form commands.
- Keep high-frequency realtime control inside dedicated controllers.
- OSIP carries contracts, bounds, commands, events, evidence, and audit trails.
- Represent uncertainty, latency, quality, evidence, contradictions, and
  calibration explicitly.

## Standards And Tooling Anchors

- ROS 2 / DDS for future robotics transport adapters and QoS mapping.
- URDF, SDFormat, and OpenUSD for robot/world/scene description references.
- MuJoCo, Gazebo, Isaac Sim, and PyBullet as simulator adapter candidates.
- W3C/OGC SOSA/SSN for sensor/actuator semantics.
- WoT for action affordance alignment.
- ISO 10218, ISO/TS 15066, ISO 26262, and IEC 61508 as safety-design
  references, not as certification claims.

## Roadmap

Physical AI should not interrupt the Smart-Room MVP. It becomes a profile after
the first reliable pipeline exists:

1. Extend vocabulary for robot state, 3D pose, transforms, proprioception,
   manipulation, navigation, and safety events.
2. Add schema examples for 3D pose, joint state, wrench/tactile claims, workspace
   bounds, and continuous-action contracts.
3. Build simulator adapter boundaries without pulling simulator dependencies into
   OSIP Core.
4. Add Sim2Real benchmark metadata: simulator version, robot/world description,
   seed, sensor noise, domain randomization, latency jitter, safe-stop events,
   and action-bound violations.
5. Design ROS 2/DDS bridge semantics with QoS kept in adapter configuration.

## Acceptance Criteria

- A valid Physical-AI percept fixture validates through OSIP schemas.
- An invalid continuous-action contract without bounds is rejected.
- A JSONL trace can replay robot/sensor percepts through the in-memory bus.
- Benchmark metadata captures simulator, seed, robot/world description, and
  safety outcomes.
