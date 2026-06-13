# Context Engine v0.1

Phase 4 adds the first deterministic context fusion layer and the runtime
boundary for Application Profile fusion. The default profile is `rooms`, but the
engine now selects fusion through a registry instead of importing room rules as
core logic.

## Components

- `TemporalWindow`: stores currently valid `PerceptPacket` objects.
- `ClaimIndex`: indexes active claims by label and confidence.
- `ContextGraph`: append-only in-memory world-state graph that can serialize
  and restore deterministic `ContextGraphSnapshot` JSON.
- `ContextFusion`: profile-facing interface for fusing active percepts.
- `ContextFusionRegistry`: maps application profile ids to fusion
  implementations.
- `RoomsFusion`: profile-specific rules for the first rooms scenarios, provided
  by `omnisense_profiles.rooms`.
- `ContextEngine`: ingests percepts, builds `ContextUpdate` payloads, and
  publishes them on the bus.

## Profile Registry

`ContextEngine(bus)` keeps `rooms` as the default profile for the MVP. A new
profile attaches by implementing `ContextFusion`, assigning a stable
`profile_id`, registering that implementation, and constructing the engine with
`application_profile`.

```python
registry = ContextFusionRegistry([XxxFusion()])
engine = ContextEngine(bus, application_profile="xxx", registry=registry)
```

Unknown profiles fail closed with `UnknownApplicationProfileError`.

An `ApplicationProfile` can also provide the `ContextFusion` implementation so
larger runtimes can load profile bundles and feed the Context Engine registry
without importing domain logic into OSIP Core.

## Initial Contexts

- `context.possible_burning_food`
- `context.possible_fall`
- `context.high_occupancy_stale_air`
- `context.sensor_conflict`

Each emitted event carries evidence and contradictions. Normal cooking with
contradictory smoke evidence remains quiet.

Rooms fusion now emits both compatible label evidence and structured
`EvidenceRef` entries so later replay, audit, and learning tools can trace a
context event back to the source percept claims.

## Persistable Context Graph

`ContextGraph` turns emitted `ContextUpdate` messages into a portable graph
snapshot without introducing a database dependency. The graph stores updates by
`context_id`, tracks the latest context per room, and exposes entity/event
records with context provenance.

Snapshots are intentionally simple:

- `schema_version`: `context_graph/0.1`,
- `graph_id`: stable graph or replay id,
- `generated_at`: timezone-aware snapshot time,
- `updates`: ordered `ContextUpdate` payloads,
- `latest_context_by_room`: deterministic room-to-context index.

The reference graph rejects duplicate context ids, naive timestamps, missing
latest-context references, and latest-context entries that point to the wrong
room. Future file, SQLite, object-store, Neo4j, or graph-database adapters
should preserve this snapshot contract instead of changing OSIP payloads.

## Boundary

The engine is not a monolithic world model. The current rules belong to the
`rooms` profile package. Future Physical-AI or other profile rules should live
in their own profile modules and only promote shared concepts to OSIP Core when
multiple profiles need them.
