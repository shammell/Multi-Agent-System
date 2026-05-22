from __future__ import annotations

from src.core.agent import Agent
from src.core.message_bus import MessageBus


class WriterAgent(Agent):
    def __init__(self, bus: MessageBus, mock_llm_client) -> None:
        super().__init__(name="writer", bus=bus, mock_llm_client=mock_llm_client)

    async def start(self) -> None:
        self.bus.subscribe("writer.in", self._handle)

    async def _handle(self, msg: dict) -> None:
        payload = msg.get("payload", msg)
        query = payload.get("query", "")
        findings = payload.get("findings", [])
        trace_id = msg.get("trace_id", "local")
        draft = await self.mock_llm_client.complete(f"{query} | {findings}")
        out = {
            "trace_id": trace_id,
            "kind": "DraftPayload",
            "payload": {
                "query": query,
                "draft": draft,
            },
        }
        await self.bus.publish("orchestrator.out", out)
