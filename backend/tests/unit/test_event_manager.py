"""Tests for EventManager — in-process pub/sub event system."""

import asyncio

import pytest

from app.cocina.event_manager import EventManager, KitchenEvent


@pytest.fixture
def manager():
    return EventManager()


@pytest.mark.asyncio
async def test_subscribe_and_broadcast(manager: EventManager):
    """Subscriber receives broadcast events."""
    queue = await manager.subscribe("test")
    event = KitchenEvent(type="TEST_EVENT", pedido_id=1, data={"msg": "hello"})

    await manager.broadcast("test", event)

    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.type == "TEST_EVENT"
    assert received.pedido_id == 1
    assert received.data["msg"] == "hello"


@pytest.mark.asyncio
async def test_multiple_subscribers(manager: EventManager):
    """All subscribers receive the same broadcast."""
    q1 = await manager.subscribe("test")
    q2 = await manager.subscribe("test")

    event = KitchenEvent(type="MULTI", pedido_id=42)
    await manager.broadcast("test", event)

    r1 = await asyncio.wait_for(q1.get(), timeout=1.0)
    r2 = await asyncio.wait_for(q2.get(), timeout=1.0)
    assert r1.pedido_id == 42
    assert r2.pedido_id == 42


@pytest.mark.asyncio
async def test_unsubscribe(manager: EventManager):
    """Unsubscribed queues no longer receive events."""
    queue = await manager.subscribe("test")
    await manager.unsubscribe("test", queue)

    event = KitchenEvent(type="GONE", pedido_id=99)
    await manager.broadcast("test", event)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), timeout=0.1)


@pytest.mark.asyncio
async def test_no_subscribers(manager: EventManager):
    """Broadcasting with no subscribers does not raise."""
    event = KitchenEvent(type="ORPHAN", pedido_id=0)
    try:
        await manager.broadcast("empty_channel", event)
    except Exception:
        pytest.fail("broadcast with no subscribers raised unexpectedly")


@pytest.mark.asyncio
async def test_subscriber_count(manager: EventManager):
    """Subscriber count reflects active subscriptions."""
    q1 = await manager.subscribe("ch1")
    q2 = await manager.subscribe("ch1")
    q3 = await manager.subscribe("ch2")

    counts = manager.subscriber_count
    assert counts.get("ch1") == 2
    assert counts.get("ch2") == 1

    await manager.unsubscribe("ch1", q1)
    counts = manager.subscriber_count
    assert counts.get("ch1") == 1


@pytest.mark.asyncio
async def test_queue_full_disconnects(manager: EventManager):
    """Subscriber with full queue is silently disconnected."""
    small_queue = asyncio.Queue(maxsize=1)
    manager._channels["test"] = {small_queue}

    event = KitchenEvent(type="FULL", pedido_id=1)
    await manager.broadcast("test", event)
    await manager.broadcast("test", event)

    # First event should be in queue, second should trigger disconnect
    assert small_queue.qsize() == 1
    assert "test" not in manager._channels or not manager._channels["test"]


@pytest.mark.asyncio
async def test_to_sse_format(manager: EventManager):
    """KitchenEvent.to_sse() returns correct SSE format."""
    event = KitchenEvent(type="PEDIDO_CONFIRMADO", pedido_id=5, data={"estado": "CONFIRMADO"})
    sse = event.to_sse()
    assert sse.startswith("event: PEDIDO_CONFIRMADO\n")
    assert 'data: {' in sse
    assert '"pedido_id": 5' in sse
    assert sse.endswith("\n\n")


@pytest.mark.asyncio
async def test_channel_isolation(manager: EventManager):
    """Events in one channel do NOT leak into another."""
    q1 = await manager.subscribe("cocina")
    q2 = await manager.subscribe("admin")

    await manager.broadcast("cocina", KitchenEvent(type="COCINA_EVENT", pedido_id=1))
    await manager.broadcast("admin", KitchenEvent(type="ADMIN_EVENT", pedido_id=2))

    r1 = await asyncio.wait_for(q1.get(), timeout=0.5)
    r2 = await asyncio.wait_for(q2.get(), timeout=0.5)

    # Each queue should only get events from its own channel
    all_in_q1 = []
    try:
        while True:
            all_in_q1.append(await asyncio.wait_for(q1.get(), timeout=0.1))
    except asyncio.TimeoutError:
        pass

    assert r1.type == "COCINA_EVENT"
    assert r2.type == "ADMIN_EVENT"
    assert len(all_in_q1) == 0  # No extra events leaked
