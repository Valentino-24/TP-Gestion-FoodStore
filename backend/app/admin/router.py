"""Admin router — aggregated stats endpoint for the admin dashboard."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from app.database import AsyncSession, get_db
from app.dependencies import require_role
from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem
from app.models.producto import Producto
from app.models.cliente import Cliente

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(["ADMIN"]))])


@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Return aggregated metrics for the admin dashboard."""
    today = date.today()

    pedidos_hoy_result = await db.execute(
        select(func.count(Pedido.id)).where(func.date(Pedido.creado_en) == today)
    )
    pedidos_hoy = pedidos_hoy_result.scalar() or 0

    ingresos_result = await db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0)).where(func.date(Pedido.creado_en) == today)
    )
    ingresos_hoy = float(ingresos_result.scalar() or 0)

    productos_result = await db.execute(
        select(func.count(Producto.id)).where(Producto.activo == True)
    )
    total_productos = productos_result.scalar() or 0

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


@router.get("/stats/detailed")
async def get_admin_stats_detailed(db: AsyncSession = Depends(get_db)):
    """Return detailed stats for charts: ingresos_por_dia, pedidos_por_estado, top_productos."""
    seven_days_ago = date.today() - timedelta(days=6)

    # Ingresos por día (últimos 7 días)
    ingresos_result = await db.execute(
        select(
            func.date(Pedido.creado_en).label("fecha"),
            func.coalesce(func.sum(Pedido.total), 0).label("total"),
        )
        .where(func.date(Pedido.creado_en) >= seven_days_ago)
        .group_by(func.date(Pedido.creado_en))
        .order_by(func.date(Pedido.creado_en))
    )
    ingresos_por_dia = [
        {"fecha": str(row.fecha), "total": float(row.total)}
        for row in ingresos_result.all()
    ]

    # Pedidos por estado
    estados_result = await db.execute(
        select(Pedido.estado, func.count(Pedido.id).label("cantidad"))
        .group_by(Pedido.estado)
        .order_by(Pedido.estado)
    )
    pedidos_por_estado = [
        {"estado": row.estado, "cantidad": row.cantidad}
        for row in estados_result.all()
    ]

    # Top 5 productos más vendidos
    top_result = await db.execute(
        select(
            PedidoItem.producto_nombre.label("nombre"),
            func.sum(PedidoItem.cantidad).label("cantidad"),
        )
        .group_by(PedidoItem.producto_nombre)
        .order_by(func.sum(PedidoItem.cantidad).desc())
        .limit(5)
    )
    top_productos = [
        {"nombre": row.nombre, "cantidad": int(row.cantidad)}
        for row in top_result.all()
    ]

    return {
        "ingresos_por_dia": ingresos_por_dia,
        "pedidos_por_estado": pedidos_por_estado,
        "top_productos": top_productos,
    }
