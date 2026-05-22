import asyncio

from src.ui.bridge import run_query_sync


class DummyManager:
    def __init__(self):
        self.calls = []

    async def start(self):
        return None

    async def handle_query(self, goal: str, trace_id: str = "t"):
        self.calls.append((goal, trace_id))
        await asyncio.sleep(0)
        return {
            "trace_id": trace_id,
            "kind": "DraftPayload",
            "payload": {"draft": f"draft:{goal}"},
        }

    def get_transitions(self, trace_id: str):
        return ["RECEIVED", "RESEARCHED", "DRAFTED", "COMPLETED"]


def test_run_query_sync_happy_path():
    manager = DummyManager()

    result = run_query_sync("grow revenue", manager=manager, timeout_s=2.0, trace_id="x-1")

    assert result["output"]["kind"] == "DraftPayload"
    assert result["trace_id"] == "x-1"
    assert result["transitions"][-1] == "COMPLETED"


def test_run_query_sync_rejects_empty_goal():
    manager = DummyManager()
    try:
        run_query_sync("   ", manager=manager, timeout_s=1.0)
        assert False, "expected ValueError"
    except ValueError:
        assert True
