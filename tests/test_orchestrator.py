import asyncio
import pytest

from src.core.message_bus import MessageBus
from src.orchestrator.manager import OrchestratorManager
from src.agents.researcher_agent import ResearcherAgent
from src.agents.writer_agent import WriterAgent


class DummyLLM:
    async def complete(self, prompt: str) -> str:
        return f"LLM:{prompt}"


@pytest.mark.asyncio
async def test_orchestrator_routes_query_to_final_output_deterministically():
    bus = MessageBus()
    manager = OrchestratorManager(bus=bus)
    researcher = ResearcherAgent(bus=bus, mock_llm_client=DummyLLM())
    writer = WriterAgent(bus=bus, mock_llm_client=DummyLLM())

    await researcher.start()
    await writer.start()
    await manager.start()

    final = await asyncio.wait_for(manager.handle_query("test topic", trace_id="trace-123"), timeout=2.0)
    assert final["kind"] == "DraftPayload"
    assert final["trace_id"] == "trace-123"

    transitions = manager.get_transitions("trace-123")
    assert transitions == ["RECEIVED", "RESEARCHED", "DRAFTED", "COMPLETED"]
