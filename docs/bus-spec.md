# OmniSense Bus v0.1

The OmniSense bus layer is the transport boundary between OSIP producers,
context fusion, decision runtime, adapters, and simulations. Phase 2 provides a
deterministic in-memory implementation for tests and local demos. Broker
adapters such as NATS, MQTT, or ROS 2/DDS should preserve the same topic and
message semantics.

## Message Envelope

Every delivered bus message has:

- `topic`: the exact published topic.
- `sequence`: deterministic sequence number scoped to that exact topic.
- `payload`: the original payload object.

The bus does not inspect OSIP semantics. A payload can be a Pydantic OSIP model,
a dict, or any object the producer and consumer agree on. OSIP validation stays
in `packages/osip`.

## Topic Rules

- Topics are dot-separated lowercase segments.
- Valid segment characters: `a-z`, `0-9`, `_`, `-`.
- Subscribe filters may use `*` for one segment and `>` as the final tail
  wildcard.
- Messages are not retained. Subscribers receive messages published after their
  async context manager has been entered.

## Core Topics

- `omnisense.models.capabilities`
- `omnisense.percepts.<modality>.<source_model>`
- `omnisense.context.updates.<room>`
- `omnisense.events.detected.<event_label>`
- `omnisense.actions.contracts`
- `omnisense.actions.proposals`
- `omnisense.actions.commands.<target>`
- `omnisense.actions.results.<action_id>`

Labels such as `audio.event_classifier_v1` or `event.fall_candidate` may expand
into multiple dot segments. Consumers that need a whole branch should subscribe
with a tail wildcard, for example `omnisense.percepts.audio.>`.

## JSONL Replay

Bus replay fixtures use one JSON object per line:

```json
{"topic":"omnisense.percepts.audio.audio.event_classifier_v1","payload":{}}
```

`replay_jsonl` can publish raw payload objects or accept a parser function such
as `validate_osip_message` to validate and convert OSIP payloads before publish.

## AsyncAPI Export

The public event API is exported as AsyncAPI 3.1.0 at
`protocols/asyncapi/asyncapi.json`. It documents the core OSIP channels above,
their publish/subscribe operations, and message payload references into
`protocols/schemas`.

Regenerate it with:

```bash
docker compose run --rm dev make asyncapi
```
