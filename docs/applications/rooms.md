# Application Profile: Rooms

The `rooms` profile is the first OSIP demonstrator. It applies OSIP Core to
intelligent rooms and smart environments.

## Scope

- Ambient perception: audio, vision, radar, air quality, occupancy, tactile floor
  pressure, appliance state.
- Context: room state, zones, people, events, comfort, safety, maintenance risk.
- Actions: HVAC, lighting, speakers, notifications, blinds, appliance controls.
- Safety: cooldowns, confirmations, preconditions, rollback, safe state, audit
  trail.

## Example Contexts

- `context.possible_burning_food`
- `context.possible_fall`
- `context.high_occupancy_stale_air`
- `context.possible_smoke_low_risk`
- `context.sensor_conflict`

## Standards Anchors

- W3C WoT for Things, Properties, Actions, and Events.
- W3C/OGC SOSA/SSN for sensor and actuator semantics.
- Brick Schema for buildings, rooms, HVAC, lighting, and equipment mapping.
- OpenAPI and AsyncAPI for external APIs and event channels.
- OpenTelemetry and Prometheus/OpenMetrics for observability.

## Roadmap

1. Keep the Smart-Room MVP as the primary near-term pipeline.
2. Build deterministic scenarios such as kitchen safety, fall candidate, stale
   air, sensor conflict, and sensor dropout.
3. Implement context fusion and decision runtime against OSIP Core contracts.
4. Add gateway and SDK only after schemas, bus, simulator, context, and decision
   runtime are stable.

## Acceptance Criteria

- Valid room percepts validate against OSIP schemas.
- Scenario replay works without hardware.
- Context updates include evidence and contradictions.
- No action is proposed without an Action Contract.
- Low-confidence or missing-precondition actions are blocked.
