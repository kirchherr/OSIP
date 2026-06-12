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

The first NATS layer is `NatsBridgeCodec`. NATS subjects already use
dot-separated tokens, so the default mapping keeps OSIP bus topics unchanged.
Deployment prefixes such as `site_a.osip` are supported while decoded bus topics
remain rooted at `omnisense`. Core NATS versus JetStream intent, explicit ack,
retention, and max-age hints are derived from the shared QoS mapping.

`NatsOutboundBridge` and `NatsInboundBridge` mirror the MQTT bridge structure.
They use small broker-independent transport/source protocols so unit tests stay
broker-free while a live adapter can later wrap `nats-py`.

The first ROS 2 / DDS layer is `Ros2BridgeCodec`. It does not import `rclpy` or
require a robot middleware runtime. Instead, it maps OSIP bus topics to absolute
ROS 2 topic names, serializes OSIP JSON through `std_msgs/msg/String`, and
attaches DDS QoS hints derived from the shared bus `QoSProfile`. Because ROS 2
topic tokens do not safely cover every OSIP bus segment, suffix tokens are
encoded reversibly, for example `physical-ai` becomes `tphysical_dai`.

`Ros2OutboundBridge` and `Ros2InboundBridge` mirror the MQTT/NATS bridge
structure with middleware-independent transport/source protocols. A live adapter
can later wrap `rclpy`, ROS 2 Actions, or a DDS vendor-specific bridge while the
reference tests remain deterministic and hardware-free.

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
- Live ROS 2 adapters may use `rclpy`, but OSIP Core and unit tests must not
  require ROS 2, DDS vendors, robot descriptions, or hardware.

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

## NATS Subject Mapping

Default mapping:

```text
omnisense.percepts.audio.audio.event_classifier_v1
omnisense.percepts.audio.audio.event_classifier_v1
```

Custom NATS prefixes are allowed for deployments, for example
`site_a.osip.percepts.audio.>`, while decoded bus topics remain rooted at
`omnisense`.

## ROS 2 Topic Mapping

Default mapping:

```text
omnisense.percepts.audio.audio.event_classifier_v1
/omnisense/tpercepts/taudio/taudio/tevent_uclassifier_uv1
```

Custom ROS 2 namespaces are allowed for deployments, for example
`/site_a/osip/tpercepts/taudio/taudio/tevent_uclassifier_uv1`, while decoded
bus topics remain rooted at `omnisense`.
