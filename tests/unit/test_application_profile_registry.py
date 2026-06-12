from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pytest
from omnisense_context import ContextFusion, ContextFusionRegistry
from omnisense_decision import (
    ActionContractRegistry,
    ContractMatch,
    DecisionProfile,
    DecisionProfileRegistry,
)
from omnisense_osip import ActionContract, ContextUpdate, GlobalRisk, PerceptPacket
from omnisense_osip.schemas import ActionPriority, ContextEvent
from omnisense_profiles import (
    ApplicationProfileMetadata,
    ApplicationProfileRegistry,
    UnknownApplicationProfileIdError,
)


class DummyFusion:
    profile_id = "dummy"

    def fuse(
        self,
        percepts: list[PerceptPacket],
        *,
        context_id: str,
        timestamp: datetime,
        room: str,
        time_window_ms: int,
    ) -> ContextUpdate:
        return ContextUpdate(
            context_id=context_id,
            timestamp=timestamp,
            time_window_ms=time_window_ms,
            room=room,
            entities=[],
            events=[],
            global_risk=GlobalRisk(safety=0.0, comfort=0.0, maintenance=0.0),
        )


class DummyPolicy:
    profile_id = "dummy"

    def matches(
        self,
        context: ContextUpdate,
        registry: ActionContractRegistry,
    ) -> list[ContractMatch]:
        return []

    def priority(self, event: ContextEvent, contract: ActionContract) -> ActionPriority:
        return "low"

    def requires_confirmation(self, contract: ActionContract) -> bool:
        return False

    def reason(self, event: ContextEvent, contract: ActionContract) -> str:
        return "dummy decision"


@dataclass(frozen=True, slots=True)
class DummyApplicationProfile:
    profile_id: str = "dummy"
    metadata: ApplicationProfileMetadata = ApplicationProfileMetadata(
        profile_id="dummy",
        display_name="Dummy",
        version="0.1",
        domain="Test domain",
        description="Dummy Application Profile for registry tests.",
    )
    context_fusion: ContextFusion = DummyFusion()
    decision_profile: DecisionProfile = DecisionProfile(
        profile_id="dummy",
        policy=DummyPolicy(),
        contracts=(),
    )


def test_default_application_profile_registry_resolves_rooms_bundle() -> None:
    registry = ApplicationProfileRegistry.with_defaults()

    profile = registry.get("rooms")

    assert registry.profile_ids == ("rooms",)
    assert profile.metadata.display_name == "Rooms"
    assert profile.context_fusion.profile_id == "rooms"
    assert profile.decision_profile.profile_id == "rooms"
    assert profile.decision_profile.policy.profile_id == "rooms"
    assert len(profile.decision_profile.contracts) == 3


def test_application_profile_can_feed_runtime_registries() -> None:
    profile_registry = ApplicationProfileRegistry.with_defaults()

    context_registry = ContextFusionRegistry(profile_registry.context_fusions())
    decision_registry = DecisionProfileRegistry(profile_registry.decision_profiles())

    assert context_registry.get("rooms").profile_id == "rooms"
    assert decision_registry.get("rooms").policy.profile_id == "rooms"


def test_application_profile_registry_rejects_unknown_profile() -> None:
    registry = ApplicationProfileRegistry()

    with pytest.raises(UnknownApplicationProfileIdError) as error:
        registry.get("physical-ai")

    assert error.value.profile_id == "physical-ai"


def test_application_profile_registry_rejects_duplicate_profile() -> None:
    registry = ApplicationProfileRegistry([DummyApplicationProfile()])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyApplicationProfile())


def test_application_profile_registry_rejects_mismatched_metadata() -> None:
    profile = DummyApplicationProfile(
        metadata=ApplicationProfileMetadata(
            profile_id="other",
            display_name="Other",
            version="0.1",
            domain="Test domain",
            description="Mismatch.",
        )
    )

    with pytest.raises(ValueError, match="metadata.profile_id"):
        ApplicationProfileRegistry([profile])


def test_application_profile_registry_rejects_mismatched_context_fusion() -> None:
    class OtherFusion(DummyFusion):
        profile_id = "other"

    profile = DummyApplicationProfile(context_fusion=OtherFusion())

    with pytest.raises(ValueError, match="context_fusion.profile_id"):
        ApplicationProfileRegistry([profile])


def test_application_profile_registry_rejects_mismatched_decision_profile() -> None:
    profile = DummyApplicationProfile(
        decision_profile=DecisionProfile(
            profile_id="other",
            policy=DummyPolicy(),
            contracts=(),
        )
    )

    with pytest.raises(ValueError, match="decision_profile.profile_id"):
        ApplicationProfileRegistry([profile])
