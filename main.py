import os

from dotenv import load_dotenv

from src.core.message_bus import MessageBus
from src.orchestrator.manager import OrchestratorManager
from src.agents.researcher_agent import ResearcherAgent
from src.agents.writer_agent import WriterAgent
from src.llm.groq_client import build_live_client_from_env


class MockLLMClient:
    async def complete(self, prompt: str) -> str:
        return f"mock:{prompt}"


def build_runtime(mode: str = "mock"):
    load_dotenv()
    env_mode = os.getenv("APP_MODE", "").strip().lower()
    if env_mode in {"mock", "live"} and mode == "mock":
        mode = env_mode

    if mode not in {"mock", "live"}:
        raise ValueError("mode must be mock or live")

    bus = MessageBus()
    llm = build_live_client_from_env() if mode == "live" else MockLLMClient()
    manager = OrchestratorManager(bus=bus)
    researcher = ResearcherAgent(bus=bus, mock_llm_client=llm)
    writer = WriterAgent(bus=bus, mock_llm_client=llm)

    runtime = {
        "bus": bus,
        "manager": manager,
        "researcher": researcher,
        "writer": writer,
        "mode": mode,
    }
    manager.runtime = runtime

    return {
        "bus": bus,
        "manager": manager,
        "researcher": researcher,
        "writer": writer,
        "mode": mode,
    }
