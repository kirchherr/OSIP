from __future__ import annotations

import pytest
from omnisense_decision import (
    ActionContractRegistry,
    ContractMatch,
    DecisionProfile,
    DecisionProfileRegistry,
    RoomsDecisionPolicy,
    UnknownDecisionProfileError,
)
from omnisense_osip import ActionContract
from omnisense_osip.schemas import ActionPriority, ContextEvent, ContextUpdate


class DummyDecisionPolicy:
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


def dummy_profile(profile_id: str = "dummy") -> DecisionProfile:
    return DecisionProfile(
        profile_id=profile_id,
        policy=DummyDecisionPolicy(),
        contracts=(),
    )


def test_default_decision_profile_registry_resolves_rooms() -> None:
    registry = DecisionProfileRegistry.with_defaults()

    profile = registry.get("rooms")

    assert isinstance(profile.policy, RoomsDecisionPolicy)
    assert len(profile.contracts) == 3
    assert registry.profile_ids == ("rooms",)


def test_decision_profile_registry_rejects_unknown_profile() -> None:
    registry = DecisionProfileRegistry()

    with pytest.raises(UnknownDecisionProfileError) as error:
        registry.get("physical-ai")

    assert error.value.profile_id == "physical-ai"


def test_decision_profile_registry_rejects_duplicate_profile() -> None:
    registry = DecisionProfileRegistry([dummy_profile()])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(dummy_profile())


def test_decision_profile_registry_rejects_empty_profile_id() -> None:
    registry = DecisionProfileRegistry()

    with pytest.raises(ValueError, match="must not be empty"):
        registry.register(dummy_profile(" "))
