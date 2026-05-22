from __future__ import annotations

import asyncio
from collections import defaultdict

from src.core.message_bus import MessageBus


class OrchestratorManager:
    def __init__(self, bus: MessageBus) -> None:
        self.bus = bus
        self._final: dict[str, dict] = {}
        self._events: dict[str, asyncio.Event] = {}
        self._transitions: dict[str, list[str]] = defaultdict(list)

    async def start(self) -> None:
        self.bus.subscribe("writer.in", self._on_researched)
        self.bus.subscribe("orchestrator.out", self._on_drafted)

    def _mark(self, trace_id: str, state: str) -> None:
        self._transitions[trace_id].append(state)

    async def _on_researched(self, msg: dict) -> None:
        trace_id = msg.get("trace_id", "local")
        if msg.get("kind") == "ResearchPayload":
            self._mark(trace_id, "RESEARCHED")

    async def _on_drafted(self, msg: dict) -> None:
        trace_id = msg.get("trace_id", "local")
        if msg.get("kind") == "DraftPayload":
            self._mark(trace_id, "DRAFTED")
            self._final[trace_id] = msg
            self._mark(trace_id, "COMPLETED")
            event = self._events.get(trace_id)
            if event:
                event.set()

    async def handle_query(self, query: str, trace_id: str = "local", timeout_s: float = 6.0) -> dict:
        self._events[trace_id] = asyncio.Event()
        self._mark(trace_id, "RECEIVED")

        task = {
            "trace_id": trace_id,
            "kind": "TaskEnvelope",
            "payload": {"query": query},
        }
        await asyncio.wait_for(self.bus.publish("researcher.in", task), timeout=timeout_s)

        while not self._events[trace_id].is_set():
            await asyncio.wait_for(self.bus.drain(), timeout=timeout_s)
            await asyncio.sleep(0)

        await asyncio.wait_for(self._events[trace_id].wait(), timeout=timeout_s)
        return self._final[trace_id]

    def get_transitions(self, trace_id: str) -> list[str]:
        return self._transitions.get(trace_id, [])
