from __future__ import annotations

from src.core.agent import Agent
from src.core.message_bus import MessageBus


class ResearcherAgent(Agent):
    def __init__(self, bus: MessageBus, mock_llm_client) -> None:
        super().__init__(name="researcher", bus=bus, mock_llm_client=mock_llm_client)

    async def start(self) -> None:
        self.bus.subscribe("researcher.in", self._handle)

    async def _handle(self, msg: dict) -> None:
        payload = msg.get("payload", msg)
        goal = payload.get("goal") or payload.get("query", "")
        trace_id = msg.get("trace_id", "local")
        synthesis = await self.mock_llm_client.complete(goal)
        out = {
            "trace_id": trace_id,
            "kind": "ResearchPayload",
            "payload": {
                "goal": goal,
                "query": goal,
                "findings": [synthesis],
            },
        }
        await self.bus.publish("writer.in", out)
