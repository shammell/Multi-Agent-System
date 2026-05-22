import asyncio
import tracemalloc
import pytest

from src.core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_peak_rss_under_40mb_during_message_passing():
    bus = MessageBus()

    async def handler(_msg):
        return None

    bus.subscribe("mem", handler)

    tracemalloc.start()
    for i in range(3000):
        await asyncio.wait_for(bus.publish("mem", {"seq": i, "data": "x" * 128}), timeout=0.05)

    await asyncio.wait_for(bus.drain(), timeout=0.2)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024.0 * 1024.0)
    assert peak_mb < 40.0
