"""Public async bus interfaces."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol, TypeVar

from omnisense_bus.messages import BusMessage

PayloadT = TypeVar("PayloadT")


class Subscription(Protocol):
    """A live topic subscription."""

    @property
    def topic_filter(self) -> str: ...

    @property
    def pending_count(self) -> int: ...

    async def receive(self) -> BusMessage[Any]: ...

    async def aclose(self) -> None: ...


class AsyncMessageBus(Protocol):
    """Minimal contract shared by in-memory and future broker adapters."""

    async def publish(self, topic: str, payload: PayloadT) -> BusMessage[PayloadT]: ...

    def subscribe(
        self,
        topic_filter: str,
        *,
        max_queue_size: int = 0,
    ) -> AbstractAsyncContextManager[Subscription]: ...
