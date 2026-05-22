from __future__ import annotations

from typing import Any

from src.core.message_bus import MessageBus


class Agent:
    def __init__(self, name: str, bus: MessageBus, mock_llm_client: Any) -> None:
        self.name = name
        self.bus = bus
        self.mock_llm_client = mock_llm_client
        self._state: dict[str, Any] = {}

    @property
    def state(self) -> dict[str, Any]:
        return self._state

    async def start(self) -> None:
        return None
