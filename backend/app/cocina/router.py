"""Cocina router — REST and SSE endpoints for the Kitchen Display System."""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.cocina.event_manager import KitchenEvent, event_manager, EventManager
from app.cocina.schemas import PedidoCocinaResponse
from app.cocina.service import CocinaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cocina", tags=["cocina"])


def _get_service(db: AsyncSession) -> CocinaService:
    return CocinaService(db)


@router.get(
    "/pedidos",
    response_model=list[PedidoCocinaResponse],
    dependencies=[Depends(require_role(["COCINA", "PEDIDOS", "ADMIN"]))],
)
async def list_pedidos_cocina(
    db: AsyncSession = Depends(get_db),
):
    """List all pedidos in kitchen states (CONFIRMADO, EN_PREPARACION).

    Used for initial KDS load and as fallback polling endpoint.
    Ordered by kitchen entry time ascending (oldest first).
    """
    service = _get_service(db)
    return await service.get_pedidos_cocina()


@router.get("/eventos", dependencies=[Depends(require_role(["COCINA", "PEDIDOS", "ADMIN"]))])
async def sse_event_stream(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Server-Sent Events stream for real-time KDS updates.

    Uses the standard authentication chain (cookie or Bearer token).
    Returns a StreamingResponse that keeps the connection open
    and sends events as they occur.
    """

    async def event_generator():
        queue = await event_manager.subscribe(EventManager.CHANNEL_KITCHEN)
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event.to_sse()
                except asyncio.TimeoutError:
                    # Send keepalive comment to keep connection open
                    yield ": keepalive\n\n"

        finally:
            await event_manager.unsubscribe(EventManager.CHANNEL_KITCHEN, queue)
            logger.debug("SSE client disconnected")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
