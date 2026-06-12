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
- Express pose, object, joint-state, force, tactile, and localization
  uncertainty with structured covariance when available.
- Treat QoS as adapter intent: low-latency best-effort for sensor streams,
  reliable delivery for contracts/commands, and critical heartbeats for
  watchdogs.
- Define profile-level safe states and watchdog thresholds before connecting
  physical actuators.

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
3. Add covariance-backed uncertainty examples for pose, object, force, and joint
   state claims.
4. Publish `profile.safety_case` and `adapter.heartbeat` fixtures for robot and
   simulator adapters.
5. Provide a `physical-ai` context-fusion implementation through the profile
   registry once vocabulary and fixtures exist.
6. Provide a `physical-ai` decision profile with contract-bounded manipulation,
   navigation, safe-stop, and observation policies before any runtime proposals.
7. Build simulator adapter boundaries without pulling simulator dependencies into
   OSIP Core.
8. Add Sim2Real benchmark metadata: simulator version, robot/world description,
   seed, sensor noise, domain randomization, latency jitter, safe-stop events,
   and action-bound violations.
9. Design ROS 2/DDS bridge semantics with QoS kept in adapter configuration and
   mapped from OSIP `x-osip-qos` intent.

## Learning Signals

Physical-AI traces can later become learning examples for:

- Sim2Real gaps between simulator results and real measurements,
- action-bound violations and safe-stop events,
- grasp, navigation, or manipulation success and failure,
- sensor noise, dropout, latency jitter, and calibration drift,
- collision-risk contexts and recovery behavior.
- distilled reflex detectors for narrow safety or contact events,
- predictive world models for action rollout, collision-risk forecasting,
  manipulation outcome prediction, and simulator improvement,
- reward models for task success, safe recovery, energy, smoothness, or
  workspace preferences, subject to explicit safety review.

Learning for Physical AI must stay offline or shadow-mode until safety gates are
passed. No learned model may directly change continuous control, motor commands,
workspace limits, emergency-stop behavior, or action contracts without explicit
review, benchmark evidence, uncertainty reporting, and rollback.

## Autonomy Signals

The `physical-ai` profile can use emergent autonomy for bounded perception and
maintenance goals:

- surprise: predicted contact, pose, force, or obstacle state differs from
  observed sensor feedback,
- epistemic value: move to a better viewpoint, request tactile confirmation,
  slow down for more reliable perception, or ask a supervisor,
- homeostasis: degraded camera, overheated compute node, stale calibration,
  repeated safe-stop, or actuator acknowledgement loss.

Physical-AI autonomy must prefer information-gathering and safe-state goals over
high-impact manipulation. Generated goals cannot change continuous controllers,
workspace limits, emergency-stop behavior, or safety-rated monitored stops.

## Acceptance Criteria

- A valid Physical-AI percept fixture validates through OSIP schemas.
- An invalid continuous-action contract without bounds is rejected.
- A covariance-backed uncertainty fixture validates through OSIP schemas.
- A `profile.safety_case` fixture declares default safe states for heartbeat
  timeout, stale context, bus disconnect, manual stop, and sensor dropout.
- An `adapter.heartbeat` fixture validates and rejects stale or naive
  timestamps.
- A JSONL trace can replay robot/sensor percepts through the in-memory bus.
- Benchmark metadata captures simulator, seed, robot/world description, and
  safety outcomes.
- Learning exports capture simulator version, robot/world description, seed,
  outcome labels, and safety gate results before any model promotion.
- Generated goals require simulator or shadow-mode evidence before they can
  influence physical actions.
