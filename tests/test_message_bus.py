import asyncio
import json
import pytest

from src.core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_pub_sub_deterministic_ordering():
    bus = MessageBus()
    received = []
    done = asyncio.Event()

    async def handler(msg):
        payload = msg.get("payload", msg)
        received.append(payload["seq"])
        if len(received) == 3:
            done.set()

    bus.subscribe("topic", handler)
    await asyncio.wait_for(bus.publish("topic", {"seq": 1}), timeout=0.05)
    await asyncio.wait_for(bus.publish("topic", {"seq": 2}), timeout=0.05)
    await asyncio.wait_for(bus.publish("topic", {"seq": 3}), timeout=0.05)

    await asyncio.wait_for(bus.drain(), timeout=0.1)
    await asyncio.wait_for(done.wait(), timeout=0.1)
    assert received == [1, 2, 3]


@pytest.mark.asyncio
async def test_publish_requires_strict_json_object_string():
    bus = MessageBus()
    with pytest.raises(ValueError):
        await bus.publish("topic", "not-json")


@pytest.mark.asyncio
async def test_publish_rejects_missing_required_keys():
    bus = MessageBus()
    bad_payload = json.dumps({"trace_id": "t1", "payload": {"x": 1}})
    with pytest.raises(ValueError):
        await bus.publish("topic", bad_payload)


@pytest.mark.asyncio
async def test_publish_rejects_checksum_mismatch():
    bus = MessageBus()
    payload = {
        "trace_id": "t1",
        "kind": "TaskEnvelope",
        "payload": {"query": "x"},
        "checksum": "bad",
    }
    with pytest.raises(ValueError):
        await bus.publish("topic", json.dumps(payload))
