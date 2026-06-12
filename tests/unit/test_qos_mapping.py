from __future__ import annotations

from typing import cast

import pytest
from omnisense_bus import (
    AdapterKind,
    Mqtt5QoSMapping,
    NatsQoSMapping,
    Ros2DDSQoSMapping,
    map_qos_profile,
    map_to_mqtt5,
    map_to_nats,
    map_to_ros2_dds,
    qos_for_channel,
)
from pydantic import ValidationError


def test_percept_qos_maps_to_low_latency_ros2_dds_sensor_policy() -> None:
    mapping = map_to_ros2_dds(qos_for_channel("percepts"))

    assert mapping == Ros2DDSQoSMapping(
        reliability="best_effort",
        durability="volatile",
        history="keep_last",
        depth=1,
        deadline_ms=10,
        lifespan_ms=50,
        priority="high",
        notes=[
            "Physical-AI adapters should map this to low-latency sensor-data QoS.",
            "max_latency_ms is measured as benchmark or telemetry, not a DDS policy",
        ],
    )


def test_action_command_qos_maps_to_reliable_mqtt5_publish_policy() -> None:
    mapping = map_qos_profile(qos_for_channel("actionCommands"), "mqtt5")

    assert isinstance(mapping, Mqtt5QoSMapping)
    assert mapping.qos == 1
    assert mapping.retain is False
    assert mapping.message_expiry_interval_ms is None
    assert mapping.priority == "critical"
    assert "deadline_ms requires adapter watchdog" in " ".join(mapping.notes)


def test_profile_safety_case_qos_maps_to_durable_native_policies() -> None:
    profile = qos_for_channel("profileSafetyCases")

    mqtt = map_to_mqtt5(profile)
    nats = map_to_nats(profile)
    ros2 = map_to_ros2_dds(profile)

    assert mqtt.qos == 1
    assert mqtt.retain is True
    assert nats == NatsQoSMapping(
        mode="jetstream",
        ack_policy="explicit",
        retain_last_per_subject=True,
        max_msgs_per_subject=8,
        max_age_ms=None,
        priority="critical",
        notes=["Adapters should load safe states before accepting action commands."],
    )
    assert ros2.durability == "transient_local"
    assert ros2.reliability == "reliable"


def test_best_effort_percept_qos_uses_nats_core_without_ack() -> None:
    mapping = map_to_nats(qos_for_channel("percepts"))

    assert mapping.mode == "core"
    assert mapping.ack_policy == "none"
    assert mapping.max_msgs_per_subject == 1
    assert mapping.max_age_ms == 50
    assert "max_latency_ms should be reported" in " ".join(mapping.notes)


def test_unknown_adapter_kind_is_rejected() -> None:
    adapter = cast(AdapterKind, "amqp")

    with pytest.raises(ValueError, match="unsupported adapter kind"):
        map_qos_profile(qos_for_channel("percepts"), adapter)


def test_adapter_mapping_models_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Ros2DDSQoSMapping.model_validate(
            {
                "reliability": "best_effort",
                "durability": "volatile",
                "history": "keep_last",
                "depth": 1,
                "priority": "high",
                "unexpected": "ignored would be unsafe",
            }
        )
