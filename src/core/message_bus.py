import asyncio
import hashlib
import json
from typing import Awaitable, Callable


class ExponentialBackoff:
    def __init__(
        self,
        base_delay: float = 0.1,
        max_delay: float = 2.0,
        jitter: float = 0.2,
        max_retries: int = 5,
        rng: Callable[[], float] | None = None,
    ) -> None:
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.max_retries = max_retries
        self.rng = rng or (lambda: 0.5)

    def should_retry(self, status_code: int) -> bool:
        return status_code == 429

    def next_delay(self, attempt: int) -> float:
        if attempt > self.max_retries:
            raise RuntimeError("max retries exceeded")
        raw = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        if self.jitter <= 0:
            return raw
        factor = 1.0 + ((self.rng() * 2.0) - 1.0) * self.jitter
        value = raw * factor
        return min(max(value, 0.0), self.max_delay)


class MessageBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict], Awaitable[None]]]] = {}
        self._queue: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()
        self._drain_lock = asyncio.Lock()

    def subscribe(self, topic: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    def _normalize_payload(self, payload: dict | str) -> dict:
        if isinstance(payload, dict):
            if "trace_id" not in payload:
                payload = {
                    "trace_id": "local",
                    "kind": "Generic",
                    "payload": payload,
                }
            if "kind" not in payload or "payload" not in payload:
                raise ValueError("missing required keys")
            body = json.dumps(payload["payload"], sort_keys=True, separators=(",", ":"))
            payload["checksum"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
            return payload

        if not isinstance(payload, str):
            raise ValueError("payload must be dict or json string")

        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid json") from exc

        if not isinstance(parsed, dict):
            raise ValueError("payload must decode to object")

        required = {"trace_id", "kind", "payload", "checksum"}
        if not required.issubset(parsed.keys()):
            raise ValueError("missing required keys")

        body = json.dumps(parsed["payload"], sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if parsed["checksum"] != expected:
            raise ValueError("checksum mismatch")

        return parsed

    async def publish(self, topic: str, payload: dict | str) -> None:
        message = self._normalize_payload(payload)
        await self._queue.put((topic, message))

    async def drain(self) -> None:
        async with self._drain_lock:
            while not self._queue.empty():
                topic, message = await self._queue.get()
                handlers = self._subscribers.get(topic, [])
                for handler in handlers:
                    await handler(message)
                self._queue.task_done()
