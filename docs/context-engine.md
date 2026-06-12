# Context Engine v0.1

Phase 4 adds the first deterministic context fusion layer for the `rooms`
application profile. The implementation is intentionally transparent: it uses a
temporal window, a claim index, and small weighted rules instead of learned
fusion.

## Components

- `TemporalWindow`: stores currently valid `PerceptPacket` objects.
- `ClaimIndex`: indexes active claims by label and confidence.
- `RoomsFusion`: profile-specific rules for the first rooms scenarios.
- `ContextEngine`: ingests percepts, builds `ContextUpdate` payloads, and
  publishes them on the bus.

## Initial Contexts

- `context.possible_burning_food`
- `context.possible_fall`
- `context.high_occupancy_stale_air`
- `context.sensor_conflict`

Each emitted event carries evidence and contradictions. Normal cooking with
contradictory smoke evidence remains quiet.

## Boundary

The engine is not a monolithic world model. The current rules belong to the
`rooms` profile. Future Physical-AI or other profile rules should live in their
own profile modules and only promote shared concepts to OSIP Core when multiple
profiles need them.
