# Scenario Replay

Phase 3 adds deterministic scenario replay for OSIP payloads. The simulator
package does not require real sensors, hardware, brokers, or sleeps. It advances
a virtual clock and publishes OSIP `PerceptPacket` objects onto the bus.

## Components

- `ScenarioLoader`: reads YAML scenario files and validates them with Pydantic.
- `SimulatedClock`: monotonic virtual time in milliseconds.
- `build_percept_packet`: converts one scenario percept into an OSIP
  `PerceptPacket`.
- `ReplayRunner`: replays a scenario onto any `AsyncMessageBus`.

## Scenario Format

```yaml
id: kitchen_burning_food
name: Kitchen burning food scenario
application_profile: rooms
duration_ms: 3000
room: kitchen
expected_contexts:
  - context.possible_burning_food
expected_actions:
  - action.hvac.ventilation_boost
latency_budget_ms:
  first_context_update: 250
  first_action_proposal: 500
sim2real:
  simulator: gazebo
  simulator_version: "11.13"
  seed: 42
  robot_description_ref: robots/mobile_manipulator.urdf
  world_description_ref: worlds/kitchen.sdf
  sensor_noise_model: gaussian_pose_noise_v1
  latency_jitter_ms: 4
  domain_randomization:
    - parameter: friction.table
      distribution: uniform
      range:
        min: 0.4
        max: 0.9
        unit: coefficient
safety:
  safety_case:
    schema_version: osip/0.1
    type: profile.safety_case
    safety_case_id: safety_rooms_demo
    profile_id: rooms
    heartbeat_timeout_ms: 50
    stale_context_ms: 120
    default_safe_states:
      - target: room.speaker
        safe_state: speaker.silent
        triggers:
          - heartbeat_timeout
  evaluate_at_ms: 230
  heartbeats:
    - at_ms: 0
      adapter_id: room_speaker_bridge
      profile_id: rooms
      status: alive
      ttl_ms: 50
  expect_safe: false
  expected_safe_states:
    - target: room.speaker
      safe_state: speaker.silent
      trigger: heartbeat_timeout
percepts:
  - at_ms: 0
    source_model: object_state.device_status_v1
    modality: object_state
    location:
      room: kitchen
      zone: stove_area
    claims:
      - label: object.stove.power_on
        confidence: 0.99
        value: true
```

`sim2real` is optional and mainly intended for Physical-AI scenarios. It records
the simulator, seed, robot/world descriptions, sensor noise model, latency
jitter, and domain-randomization settings needed to reproduce imperfect
simulation conditions.

`safety` is optional. When present, the benchmark runner evaluates the embedded
`profile.safety_case` with simulated heartbeats and runtime fault flags. A
scenario can pass with a safe-state activation when that activation is declared
in `expected_safe_states`.

## Required Rooms Scenarios

- `scenarios/kitchen_burning_food.yaml`
- `scenarios/fall_candidate.yaml`
- `scenarios/stale_air_high_occupancy.yaml`

The remaining negative and conflict scenarios from the masterplan should be
added before the Context Engine phase becomes a hard benchmark gate.
