"""Action command stub for adapter-facing tests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from omnisense_bus import AsyncMessageBus, action_command_topic
from omnisense_osip import ActionCommand, ActionContract, ActionProposal


class ActionCommandExecutorStub:
    """Builds and publishes OSIP ActionCommand messages without real side effects."""

    def __init__(self, bus: AsyncMessageBus) -> None:
        self._bus = bus
        self._command_counter = 0

    async def dispatch(
        self,
        proposal: ActionProposal,
        contract: ActionContract,
        *,
        parameters: Mapping[str, Any] | None = None,
    ) -> ActionCommand:
        command = self.build_command(proposal, contract, parameters=parameters)
        await self._bus.publish(action_command_topic(command.target), command)
        return command

    def build_command(
        self,
        proposal: ActionProposal,
        contract: ActionContract,
        *,
        parameters: Mapping[str, Any] | None = None,
    ) -> ActionCommand:
        if proposal.action_id != contract.action_id:
            msg = (
                f"proposal action '{proposal.action_id}' does not match "
                f"contract '{contract.action_id}'"
            )
            raise ValueError(msg)

        self._command_counter += 1
        return ActionCommand(
            trace_id=proposal.trace_id,
            correlation_id=proposal.correlation_id or proposal.trace_id or proposal.proposal_id,
            command_id=f"cmd_{self._command_counter:06d}",
            proposal_id=proposal.proposal_id,
            action_id=contract.action_id,
            target=contract.target,
            operation=contract.operation,
            parameters=dict(parameters or {}),
            execute_before_ms=proposal.deadline_ms,
            idempotency_key=self._idempotency_key(proposal, contract),
        )

    @staticmethod
    def _idempotency_key(proposal: ActionProposal, contract: ActionContract) -> str:
        if contract.idempotent:
            return f"{proposal.based_on_context}:{proposal.action_id}"
        return f"{proposal.proposal_id}:{proposal.action_id}"
