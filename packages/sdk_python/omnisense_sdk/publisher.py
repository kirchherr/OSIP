"""Small async SDK publisher for the OSIP Gateway API."""

from __future__ import annotations

from types import TracebackType

import httpx
from omnisense_osip import ContextUpdate, ModelCapabilityDescriptor, PerceptPacket


class OmniSensePublisher:
    """Async client for registering models and publishing percept packets."""

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(base_url=base_url)

    async def __aenter__(self) -> OmniSensePublisher:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def register_model(self, capability: ModelCapabilityDescriptor) -> str:
        response = await self._client.post(
            "/v1/models/register",
            json=capability.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        model_id = response.json()["model_id"]
        if not isinstance(model_id, str):
            msg = "gateway returned non-string model_id"
            raise TypeError(msg)
        return model_id

    async def publish_percept(self, percept: PerceptPacket) -> dict[str, object]:
        response = await self._client.post(
            "/v1/percepts",
            json=percept.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            msg = "gateway returned non-object percept response"
            raise TypeError(msg)
        return payload

    async def current_context(self, *, room: str | None = None) -> ContextUpdate:
        response = await self._client.get(
            "/v1/context/current",
            params={"room": room} if room is not None else None,
        )
        response.raise_for_status()
        return ContextUpdate.model_validate(response.json())
