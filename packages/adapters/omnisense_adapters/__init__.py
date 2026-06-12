"""Adapter contracts and hardware-free reference adapters for OSIP."""

from omnisense_adapters.interfaces import (
    AdapterMetadata,
    AdapterRole,
    AdapterRunResult,
    OSIPSourceAdapter,
)
from omnisense_adapters.jsonl import DEFAULT_ALLOWED_MESSAGE_TYPES, JSONLOSIPSourceAdapter
from omnisense_adapters.mqtt import (
    CHANNEL_MESSAGE_TYPES,
    MqttBridgeCodec,
    MqttDecodedRecord,
    MqttInboundBridge,
    MqttInboundMessage,
    MqttMessageSource,
    MqttOutboundBridge,
    MqttPublishRecord,
    MqttPublishTransport,
    MqttTopicMapper,
    channel_id_for_bus_topic,
    ensure_mqtt_topic,
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
    "OSIPSourceAdapter",
    "channel_id_for_bus_topic",
    "ensure_mqtt_topic",
]
