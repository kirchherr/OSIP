from __future__ import annotations

import pytest
from omnisense_decision import ActionContractRegistry, DuplicateActionContractError
from omnisense_decision.policy import default_rooms_contracts


def test_action_contract_registry_matches_contexts() -> None:
    registry = ActionContractRegistry(default_rooms_contracts())

    actions = [
        contract.action_id
        for contract in registry.matching_context("context.possible_burning_food")
    ]

    assert actions == ["action.notify.local", "action.hvac.ventilation_boost"]


def test_action_contract_registry_rejects_duplicate_action_ids() -> None:
    contract = default_rooms_contracts()[0]
    registry = ActionContractRegistry([contract])

    with pytest.raises(DuplicateActionContractError, match=contract.action_id):
        registry.register(contract)
