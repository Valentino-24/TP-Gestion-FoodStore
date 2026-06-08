"""In-process pub/sub event manager for real-time KDS updates.

Uses asyncio.Queue for each subscriber. Works in single-instance mode.
For multi-instance deployments, replace with Redis Pub/Sub.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class KitchenEvent:
    """A kitchen event to be broadcast via SSE."""

    type: str
    pedido_id: int
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_sse(self) -> str:
        """Format as SSE message."""
        payload = {
            "type": self.type,
            "pedido_id": self.pedido_id,
            "data": self.data,
            "timestamp": self.timestamp,
        }
        return f"event: {self.type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


class EventManager:
    """In-process pub/sub event manager.

    Manages subscriber queues per channel. Each SSE connection gets an
    asyncio.Queue. Events are broadcast non-blocking: if a subscriber's
    queue is full, the subscriber is disconnected.
    """

    CHANNEL_KITCHEN = "kitchen"

    def __init__(self):
        self._channels: dict[str, set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, channel: str) -> asyncio.Queue:
        """Register a new subscriber queue for a channel.

        Returns:
            An asyncio.Queue that will receive KitchenEvent objects.
        """
        queue: asyncio.Queue = asyncio.Queue(maxsize=128)
        async with self._lock:
            if channel not in self._channels:
                self._channels[channel] = set()
            self._channels[channel].add(queue)
        logger.debug("Subscriber added to channel '%s'. Total: %d", channel, len(self._channels[channel]))
        return queue

    async def unsubscribe(self, channel: str, queue: asyncio.Queue) -> None:
        """Remove a subscriber queue from a channel."""
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(queue)
                if not self._channels[channel]:
                    del self._channels[channel]
        logger.debug("Subscriber removed from channel '%s'", channel)

    async def broadcast(self, channel: str, event: KitchenEvent) -> None:
        """Broadcast an event to all subscribers of a channel.

        Non-blocking: if a queue is full, the subscriber is silently
        disconnected (queue full = client too slow or disconnected).
        """
        async with self._lock:
            queues = self._channels.get(channel, set()).copy()

        dead: set[asyncio.Queue] = set()
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead.add(queue)
                logger.warning("Subscriber queue full, disconnecting from '%s'", channel)

        if dead:
            async with self._lock:
                if channel in self._channels:
                    self._channels[channel] -= dead
                    if not self._channels[channel]:
                        del self._channels[channel]

    @property
    def subscriber_count(self) -> dict[str, int]:
        """Return number of subscribers per channel."""
        return {ch: len(qs) for ch, qs in self._channels.items()}


# Singleton instance — import this wherever needed
event_manager = EventManager()
