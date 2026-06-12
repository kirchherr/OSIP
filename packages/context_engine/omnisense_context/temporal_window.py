"""Temporal window for active percept packets."""

from __future__ import annotations

from datetime import datetime, timedelta

from omnisense_osip import PerceptPacket


class TemporalWindow:
    """Stores percepts that are valid at the current simulated time."""

    def __init__(self, window_ms: int) -> None:
        if window_ms <= 0:
            msg = "window_ms must be greater than zero"
            raise ValueError(msg)
        self.window_ms = window_ms
        self._percepts: list[PerceptPacket] = []

    def add(self, packet: PerceptPacket) -> None:
        self._percepts.append(packet)

    def active_at(self, now: datetime, *, room: str | None = None) -> list[PerceptPacket]:
        self.prune(now)
        return [
            packet
            for packet in self._percepts
            if self._is_active(packet, now) and (room is None or self._packet_room(packet) == room)
        ]

    def prune(self, now: datetime) -> None:
        earliest = now - timedelta(milliseconds=self.window_ms)
        self._percepts = [
            packet
            for packet in self._percepts
            if packet.timestamp >= earliest and self._expires_at(packet) >= now
        ]

    @staticmethod
    def _packet_room(packet: PerceptPacket) -> str | None:
        if packet.location is None:
            return None
        return packet.location.room

    @staticmethod
    def _expires_at(packet: PerceptPacket) -> datetime:
        return packet.timestamp + timedelta(milliseconds=packet.valid_for_ms)

    def _is_active(self, packet: PerceptPacket, now: datetime) -> bool:
        earliest = now - timedelta(milliseconds=self.window_ms)
        return earliest <= packet.timestamp <= now and self._expires_at(packet) >= now
