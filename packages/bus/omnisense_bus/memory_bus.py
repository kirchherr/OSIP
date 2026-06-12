"""Deterministic in-memory bus for tests, simulation, and local demos."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from types import TracebackType
from typing import Any, TypeVar, cast

from omnisense_bus.messages import BusMessage
from omnisense_bus.topics import ensure_valid_topic, topic_matches

PayloadT = TypeVar("PayloadT")

_SENTINEL = object()


class BackpressureError(RuntimeError):
    """Raised when a bounded subscription queue cannot accept a message."""


class SubscriptionClosedError(RuntimeError):
    """Raised when receiving from a closed subscription."""


@dataclass(slots=True)
class _Subscriber:
    topic_filter: str
    queue: asyncio.Queue[BusMessage[Any] | object]
    active: bool = False


class InMemorySubscription:
    """Async context manager returned by :class:`InMemoryBus.subscribe`."""

    def __init__(self, bus: InMemoryBus, subscriber: _Subscriber) -> None:
        self._bus = bus
        self._subscriber = subscriber

    @property
    def topic_filter(self) -> str:
        return self._subscriber.topic_filter

    @property
    def pending_count(self) -> int:
        return self._subscriber.queue.qsize()

    async def __aenter__(self) -> InMemorySubscription:
        await self._bus._register(self._subscriber)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def receive(self) -> BusMessage[Any]:
        item = await self._subscriber.queue.get()
        if item is _SENTINEL:
            msg = f"subscription for '{self.topic_filter}' is closed"
            raise SubscriptionClosedError(msg)
        return cast(BusMessage[Any], item)

    async def aclose(self) -> None:
        await self._bus._unregister(self._subscriber)
        try:
            self._subscriber.queue.put_nowait(_SENTINEL)
        except asyncio.QueueFull:
            pass


class InMemoryBus:
    """An in-process pub/sub bus with NATS-like topic filters.

    Messages are not retained. Subscribers receive messages published after they
    enter their async context manager. Sequence numbers are deterministic and
    scoped to the exact published topic.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._subscribers: list[_Subscriber] = []
        self._sequences: defaultdict[str, int] = defaultdict(int)

    def subscribe(
        self,
        topic_filter: str,
        *,
        max_queue_size: int = 0,
    ) -> InMemorySubscription:
        ensure_valid_topic(topic_filter, allow_wildcards=True)
        if max_queue_size < 0:
            msg = "max_queue_size must be greater than or equal to zero"
            raise ValueError(msg)
        subscriber = _Subscriber(
            topic_filter=topic_filter,
            queue=asyncio.Queue(maxsize=max_queue_size),
        )
        return InMemorySubscription(self, subscriber)

    async def publish(self, topic: str, payload: PayloadT) -> BusMessage[PayloadT]:
        ensure_valid_topic(topic)
        async with self._lock:
            self._sequences[topic] += 1
            message = BusMessage(
                topic=topic,
                sequence=self._sequences[topic],
                payload=payload,
            )
            for subscriber in tuple(self._subscribers):
                if topic_matches(subscriber.topic_filter, topic):
                    try:
                        subscriber.queue.put_nowait(message)
                    except asyncio.QueueFull as exc:
                        msg = f"subscription queue for '{subscriber.topic_filter}' is full"
                        raise BackpressureError(msg) from exc
            return message

    async def _register(self, subscriber: _Subscriber) -> None:
        async with self._lock:
            if subscriber.active:
                return
            self._subscribers.append(subscriber)
            subscriber.active = True

    async def _unregister(self, subscriber: _Subscriber) -> None:
        async with self._lock:
            if not subscriber.active:
                return
            self._subscribers = [item for item in self._subscribers if item is not subscriber]
            subscriber.active = False
