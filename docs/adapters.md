# OSIP Adapters

Adapters are the boundary between OSIP Core and external systems such as files,
model processes, gateways, brokers, robot middleware, building systems, and
future hardware bridges.

OSIP Core stays transport-agnostic. Adapters may use MQTT, NATS, ROS 2/DDS,
HTTP, files, SDK calls, or vendor APIs, but they must publish or consume
validated OSIP messages at the boundary.

## Contracts

`packages/adapters/omnisense_adapters` defines the first public adapter
contracts:

- `AdapterMetadata`: stable identity, role, supported OSIP message types,
  profile id, and whether real hardware is required.
- `AdapterRunResult`: deterministic machine-readable result for adapter test
  runs.
- `OSIPSourceAdapter`: async protocol for source adapters that validate payloads
  and publish them to an `AsyncMessageBus`.

The initial reference adapter is `JSONLOSIPSourceAdapter`. It reads JSONL
records with `topic` and `payload`, validates each payload through
`validate_osip_message`, checks the adapter's allowed message types, and then
publishes typed OSIP models to the bus.

## Rules

- Tests must not require real sensors, brokers, robot middleware, or hardware.
- A source adapter must reject malformed OSIP payloads before publishing.
- A source adapter must declare supported OSIP message types in metadata.
- Broker or hardware adapters must remain outside OSIP Core and use the same
  public bus and schema contracts.
- QoS mappings remain adapter configuration and telemetry intent, not payload
  semantics.

## JSONL Format

Each line is one JSON object:

```json
{"topic":"omnisense.percepts.audio.audio.event_classifier_v1","payload":{"schema_version":"osip/0.1","type":"percept.packet"}}
```

The payload above is abbreviated. Real records must validate against the OSIP
JSON Schemas.
