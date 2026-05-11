"""Admin router — aggregated stats endpoint for the admin dashboard."""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from app.database import AsyncSession, get_db
from app.dependencies import require_role
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.cliente import Cliente

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(["ADMIN"]))])


@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Return aggregated metrics for the admin dashboard.

    Returns:
        Dict with: pedidos_hoy, ingresos_hoy, total_productos, total_clientes
    """
    today = date.today()

    # Pedidos created today
    pedidos_hoy_result = await db.execute(
        select(func.count(Pedido.id)).where(func.date(Pedido.creado_en) == today)
    )
    pedidos_hoy = pedidos_hoy_result.scalar() or 0

    # Sum of totals for today's pedidos
    ingresos_result = await db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0)).where(func.date(Pedido.creado_en) == today)
    )
    ingresos_hoy = float(ingresos_result.scalar() or 0)

    # Active products
    productos_result = await db.execute(
        select(func.count(Producto.id)).where(Producto.activo == True)
    )
    total_productos = productos_result.scalar() or 0

    # Active clients
    clientes_result = await db.execute(
        select(func.count(Cliente.id)).where(Cliente.activo == True)
    )
    total_clientes = clientes_result.scalar() or 0

    return {
        "pedidos_hoy": pedidos_hoy,
        "ingresos_hoy": round(ingresos_hoy, 2),
        "total_productos": total_productos,
        "total_clientes": total_clientes,
    }
