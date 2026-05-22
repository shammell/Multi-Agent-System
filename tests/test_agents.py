import json
import pytest

from src.core.message_bus import MessageBus
from src.agents.researcher_agent import ResearcherAgent
from src.agents.writer_agent import WriterAgent


class DummyLLM:
    async def complete(self, prompt: str) -> str:
        return f"LLM:{prompt}"


@pytest.mark.asyncio
async def test_researcher_consumes_task_envelope_outputs_research_payload():
    bus = MessageBus()
    out = []

    async def collect(msg):
        out.append(msg)

    bus.subscribe("writer.in", collect)
    agent = ResearcherAgent(bus=bus, mock_llm_client=DummyLLM())
    await agent.start()

    envelope = {
        "trace_id": "t-1",
        "kind": "TaskEnvelope",
        "payload": {"query": "quantum batteries"},
    }
    await bus.publish("researcher.in", envelope)
    await bus.drain()

    assert len(out) == 1
    assert out[0]["kind"] == "ResearchPayload"
    assert out[0]["payload"]["query"] == "quantum batteries"


@pytest.mark.asyncio
async def test_writer_consumes_research_payload_outputs_draft_payload():
    bus = MessageBus()
    out = []

    async def collect(msg):
        out.append(msg)

    bus.subscribe("orchestrator.out", collect)
    agent = WriterAgent(bus=bus, mock_llm_client=DummyLLM())
    await agent.start()

    payload = {
        "trace_id": "t-2",
        "kind": "ResearchPayload",
        "payload": {"query": "ai chips", "findings": ["f1", "f2"]},
    }
    await bus.publish("writer.in", payload)
    await bus.drain()

    assert len(out) == 1
    assert out[0]["kind"] == "DraftPayload"
    assert "ai chips" in out[0]["payload"]["draft"]


def test_agent_state_isolation():
    bus = MessageBus()
    r = ResearcherAgent(bus=bus, mock_llm_client=DummyLLM())
    w = WriterAgent(bus=bus, mock_llm_client=DummyLLM())
    r.state["x"] = 1
    assert "x" not in w.state
