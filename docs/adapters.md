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

The first MQTT bridge layer is `MqttBridgeCodec`. It does not open a broker
connection. Instead, it defines the deterministic boundary that a live MQTT
adapter must preserve:

- OSIP bus topics use dots; MQTT topics use slash-separated levels.
- Bus wildcard filters `*` and `>` map to MQTT `+` and `#`.
- Payloads are serialized OSIP JSON and validated on decode.
- MQTT 5 QoS, retained delivery, and message-expiry hints are derived from the
  bus `QoSProfile` through the reference MQTT mapping.
- The codec rejects topic/message mismatches, for example a safety case on a
  percept topic.

`MqttOutboundBridge` adds the first sink-adapter shape. It accepts a small
`MqttPublishTransport` protocol, so tests can use an in-memory fake while a live
adapter can later wrap `aiomqtt` or another broker client. The bridge returns an
`AdapterRunResult` with both OSIP bus topics and MQTT target topics.

`MqttInboundBridge` mirrors this for subscriptions. It accepts a small
`MqttMessageSource` protocol, decodes `MqttInboundMessage` records through the
same codec, validates the OSIP message type against the topic, and publishes the
typed payload to an `AsyncMessageBus`.

## Rules

- Tests must not require real sensors, brokers, robot middleware, or hardware.
- A source adapter must reject malformed OSIP payloads before publishing.
- A source adapter must declare supported OSIP message types in metadata.
- Broker or hardware adapters must remain outside OSIP Core and use the same
  public bus and schema contracts.
- QoS mappings remain adapter configuration and telemetry intent, not payload
  semantics.
- Live broker adapters may use `aiomqtt`, but unit tests for adapter contracts
  must stay broker-free.

## JSONL Format

Each line is one JSON object:

```json
{"topic":"omnisense.percepts.audio.audio.event_classifier_v1","payload":{"schema_version":"osip/0.1","type":"percept.packet"}}
```

The payload above is abbreviated. Real records must validate against the OSIP
JSON Schemas.

## MQTT Topic Mapping

Default mapping:

```text
omnisense.percepts.audio.audio.event_classifier_v1
omnisense/percepts/audio/audio/event_classifier_v1
```

Custom MQTT prefixes are allowed for deployments, for example
`site_a/osip/percepts/audio/#`, while decoded bus topics remain rooted at
`omnisense`.
