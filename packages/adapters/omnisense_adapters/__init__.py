"""Adapter contracts and hardware-free reference adapters for OSIP."""

from omnisense_adapters.channels import CHANNEL_MESSAGE_TYPES, channel_id_for_bus_topic
from omnisense_adapters.interfaces import (
    AdapterMetadata,
    AdapterRole,
    AdapterRunResult,
    OSIPSourceAdapter,
)
from omnisense_adapters.jsonl import DEFAULT_ALLOWED_MESSAGE_TYPES, JSONLOSIPSourceAdapter
from omnisense_adapters.mqtt import (
    MqttBridgeCodec,
    MqttDecodedRecord,
    MqttInboundBridge,
    MqttInboundMessage,
    MqttMessageSource,
    MqttOutboundBridge,
    MqttPublishRecord,
    MqttPublishTransport,
    MqttTopicMapper,
    ensure_mqtt_topic,
)
from omnisense_adapters.nats import (
    NatsBridgeCodec,
    NatsDecodedRecord,
    NatsPublishRecord,
    NatsSubjectMapper,
    ensure_nats_subject,
)

__all__ = [
    "CHANNEL_MESSAGE_TYPES",
    "DEFAULT_ALLOWED_MESSAGE_TYPES",
    "AdapterMetadata",
    "AdapterRole",
    "AdapterRunResult",
    "JSONLOSIPSourceAdapter",
    "MqttBridgeCodec",
    "MqttDecodedRecord",
    "MqttInboundBridge",
    "MqttInboundMessage",
    "MqttMessageSource",
    "MqttOutboundBridge",
    "MqttPublishRecord",
    "MqttPublishTransport",
    "MqttTopicMapper",
    "NatsBridgeCodec",
    "NatsDecodedRecord",
    "NatsPublishRecord",
    "NatsSubjectMapper",
    "OSIPSourceAdapter",
    "channel_id_for_bus_topic",
    "ensure_mqtt_topic",
    "ensure_nats_subject",
]
