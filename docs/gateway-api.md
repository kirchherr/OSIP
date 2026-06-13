# Gateway API v1

The Gateway API exposes the current OSIP MVP through HTTP and WebSocket
interfaces. It composes the in-memory bus, Context Engine, and Decision Runtime
inside one FastAPI application for local demos and tests.

## Endpoints

- `POST /v1/models/register`: validates and stores a
  `ModelCapabilityDescriptor`, publishes it on the model capability bus topic,
  and streams a WebSocket event.
- `POST /v1/model-plugins/register`: validates and stores a declarative
  `ModelPluginManifest`, then registers its contained
  `ModelCapabilityDescriptor` with the same capability gate.
- `POST /v1/percepts`: validates a `PerceptPacket`, checks it against the
  registered `ModelCapabilityDescriptor`, publishes it on the bus, runs context
  fusion, runs bounded decision evaluation, and returns the current
  `ContextUpdate` plus any `ActionProposal` messages.
- `GET /v1/context/current`: returns the latest context, optionally filtered by
  `?room=<room_id>`.
- `GET /openapi.json`: FastAPI-generated OpenAPI contract.
- `WS /ws/events`: streams gateway events such as model registrations, ingested
  percepts, context updates, and action proposals.

## SDK

`omnisense_sdk.OmniSensePublisher` is a small async publisher for:

- `register_model(capability)`
- `publish_percept(percept)`
- `current_context(room=...)`

It accepts an injected `httpx.AsyncClient`, which keeps tests network-free with
`httpx.ASGITransport`.

## Capability Gate

The gateway rejects percepts from unregistered source models. It also rejects
percepts whose modality or claim labels are not declared in the registered
`ModelCapabilityDescriptor`. This keeps open model ingestion bounded by an
explicit public capability contract before data reaches context fusion or action
proposal logic.

Model plug-in registration is a convenience boundary over the same gate. The
gateway stores the manifest but does not import code, start processes, call
HTTP endpoints, or access hardware.

## Safety Boundary

The gateway does not execute real actions. It can create proposals through the
Decision Runtime and can later dispatch commands through adapter boundaries, but
hardware, cloud services, robot SDKs, and building systems remain out of core
tests.

## OpenAPI Export

Regenerate the static OpenAPI artifact with:

```bash
docker compose run --rm dev make openapi
```

The generated file is written to `protocols/openapi/openapi.json`.
