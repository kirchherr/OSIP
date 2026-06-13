from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from omnisense_model_plugins import ModelPluginManifest, ModelPluginRegistry
from omnisense_osip import ModelCapabilityDescriptor
from pydantic import ValidationError

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


def load_capability() -> ModelCapabilityDescriptor:
    data = json.loads((FIXTURE_DIR / "model_capability.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return ModelCapabilityDescriptor.model_validate(data)


def manifest_payload(**updates: Any) -> dict[str, Any]:
    capability = load_capability()
    payload: dict[str, Any] = {
        "plugin_id": capability.model_id,
        "display_name": "Vision Pose Activity Plug-in",
        "version": "0.1.0",
        "capability": capability.model_dump(mode="json", exclude_none=True),
        "runtime": "simulation_stub",
        "application_profiles": ["rooms", "physical-ai"],
        "tags": ["vision", "pose"],
    }
    payload.update(updates)
    return payload


def test_model_plugin_manifest_validates_capability_alignment() -> None:
    manifest = ModelPluginManifest.model_validate(manifest_payload())

    assert manifest.plugin_id == "vision.pose_activity_v1"
    assert manifest.capability.model_id == manifest.plugin_id
    assert manifest.runtime == "simulation_stub"
    assert manifest.application_profiles == ("rooms", "physical-ai")
    assert manifest.tags == ("vision", "pose")


def test_model_plugin_manifest_rejects_mismatched_capability() -> None:
    payload = manifest_payload(plugin_id="vision.other_model_v1")

    with pytest.raises(ValidationError, match="plugin_id must match"):
        ModelPluginManifest.model_validate(payload)


def test_model_plugin_manifest_requires_entrypoint_for_live_runtimes() -> None:
    payload = manifest_payload(runtime="python_callable")

    with pytest.raises(ValidationError, match="requires an entrypoint"):
        ModelPluginManifest.model_validate(payload)


def test_model_plugin_manifest_rejects_unsafe_simulation_hardware_mix() -> None:
    payload = manifest_payload(requires_hardware=True)

    with pytest.raises(ValidationError, match="must not require hardware"):
        ModelPluginManifest.model_validate(payload)


def test_model_plugin_manifest_rejects_whitespace_entrypoint() -> None:
    payload = manifest_payload(runtime="python_callable", entrypoint="models.pose: make")

    with pytest.raises(ValidationError, match="entrypoint"):
        ModelPluginManifest.model_validate(payload)


def test_model_plugin_registry_registers_and_replaces_manifest() -> None:
    registry = ModelPluginRegistry()
    timestamp = datetime(2026, 6, 13, 8, 0, tzinfo=UTC)
    manifest = ModelPluginManifest.model_validate(
        manifest_payload(runtime="python_callable", entrypoint="models.pose:create")
    )

    first = registry.register(manifest, registered_at=timestamp)
    second_manifest = manifest.model_copy(update={"version": "0.2.0"})
    second = registry.register(second_manifest, registered_at=timestamp)

    assert first.status == "registered"
    assert second.status == "replaced"
    assert registry.get(manifest.plugin_id) == second_manifest
    assert registry.registration(manifest.plugin_id) == second
    assert registry.capabilities() == (second_manifest.capability,)


def test_model_plugin_registry_filters_by_application_profile() -> None:
    capability = load_capability()
    rooms = ModelPluginManifest.model_validate(manifest_payload(application_profiles=["rooms"]))
    physical = ModelPluginManifest.model_validate(
        {
            **manifest_payload(),
            "plugin_id": "vision.pose_activity_v2",
            "capability": capability.model_copy(
                update={"model_id": "vision.pose_activity_v2"}
            ).model_dump(mode="json", exclude_none=True),
            "application_profiles": ["physical-ai"],
        }
    )
    global_manifest = ModelPluginManifest.model_validate(
        {
            **manifest_payload(),
            "plugin_id": "vision.pose_activity_v3",
            "capability": capability.model_copy(
                update={"model_id": "vision.pose_activity_v3"}
            ).model_dump(mode="json", exclude_none=True),
            "application_profiles": [],
        }
    )
    registry = ModelPluginRegistry([physical, global_manifest, rooms])

    assert [manifest.plugin_id for manifest in registry.manifests(profile_id="rooms")] == [
        "vision.pose_activity_v1",
        "vision.pose_activity_v3",
    ]
    assert [manifest.plugin_id for manifest in registry.manifests(profile_id="physical-ai")] == [
        "vision.pose_activity_v2",
        "vision.pose_activity_v3",
    ]
