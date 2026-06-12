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

## Required Rooms Scenarios

- `scenarios/kitchen_burning_food.yaml`
- `scenarios/fall_candidate.yaml`
- `scenarios/stale_air_high_occupancy.yaml`

The remaining negative and conflict scenarios from the masterplan should be
added before the Context Engine phase becomes a hard benchmark gate.
