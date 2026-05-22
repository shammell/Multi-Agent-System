import asyncio
import threading
import uuid


def _run_coro_in_thread(coro):
    box = {"result": None, "error": None}

    def _target():
        try:
            box["result"] = asyncio.run(coro)
        except Exception as exc:
            box["error"] = exc

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join()
    if box["error"] is not None:
        raise box["error"]
    return box["result"]


def run_query_sync(goal: str, manager, timeout_s: float = 2.0, trace_id: str | None = None):
    cleaned = (goal or "").strip()
    if not cleaned:
        raise ValueError("goal cannot be empty")

    tid = trace_id or f"trace-{uuid.uuid4().hex[:8]}"

    async def _execute():
        runtime = getattr(manager, "runtime", None)
        if runtime is not None:
            await runtime["researcher"].start()
            await runtime["writer"].start()
        await manager.start()
        try:
            output = await asyncio.wait_for(manager.handle_query(cleaned, trace_id=tid, timeout_s=timeout_s), timeout=timeout_s)
        except TypeError:
            output = await asyncio.wait_for(manager.handle_query(cleaned, trace_id=tid), timeout=timeout_s)
        transitions = manager.get_transitions(tid)
        assert isinstance(transitions, list)
        assert output.get("kind") == "DraftPayload"
        return {
            "trace_id": tid,
            "output": output,
            "transitions": transitions,
            "envelopes": [
                {"trace_id": tid, "kind": "TaskEnvelope"},
                {"trace_id": tid, "kind": "ResearchPayload"},
                {"trace_id": tid, "kind": "DraftPayload"},
            ],
        }

    try:
        asyncio.get_running_loop()
        return _run_coro_in_thread(_execute())
    except RuntimeError:
        return asyncio.run(_execute())
