# Application Profile: Rooms

The `rooms` profile is the first OSIP demonstrator. It applies OSIP Core to
intelligent rooms and smart environments.

## Scope

- Ambient perception: audio, vision, radar, air quality, occupancy, tactile floor
  pressure, appliance state.
- Context: room state, zones, people, events, comfort, safety, maintenance risk.
- Context fusion: `omnisense_profiles.rooms.RoomsFusion` registered under
  profile id `rooms`.
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
3. Keep context fusion in the profile package and register it with the
   profile-aware Context Engine.
4. Add gateway and SDK only after schemas, bus, simulator, context, and decision
   runtime are stable.

## Learning Signals

Room traces can later become learning examples for:

- false alarms versus confirmed safety events,
- missed events found by later feedback,
- action blocks caused by missing preconditions or cooldown,
- occupancy, air-quality, and comfort outcome patterns,
- sensor conflicts, degraded sensors, and dropout recovery.
- distilled low-latency detectors for narrow room-safety contexts,
- predictive comfort/world models such as ventilation, temperature, VOC, and
  occupant-response forecasts,
- reward models for profile-owned objectives such as comfort, safety, air
  quality, energy use, and disturbance minimization.

The `rooms` profile owns privacy, retention, consent, and anonymization rules
for real-world room traces. OSIP Core should only define generic trace and
dataset contracts. Room reward signals should document feedback delay and
ambiguity, for example whether a jacket, opened window, cough, or user override
really reflects the action or an unrelated cause.

## Autonomy Signals

The `rooms` profile can use emergent autonomy for bounded investigation and
maintenance goals:

- surprise: unexpected air-quality shifts, open/closed device state changes,
  unusual occupancy transitions, or sensor/model disagreement,
- epistemic value: request another modality, ask for confirmation, increase
  sampling briefly, or inspect a zone with a permitted sensor,
- homeostasis: request sensor cleaning, calibration, degraded-node fallback, or
  maintenance notification.

Room autonomy must not "restore normality" automatically. A window opened by a
person, a user override, or a privacy-sensitive zone should normally produce a
confirmation or observation goal, not a corrective action.

## Acceptance Criteria

- Valid room percepts validate against OSIP schemas.
- Scenario replay works without hardware.
- Context updates include evidence and contradictions.
- No action is proposed without an Action Contract.
- Low-confidence or missing-precondition actions are blocked.
- Learning exports include provenance and cannot promote models automatically.
- Generated goals are blocked or decomposed when no safe Action Contract exists.
