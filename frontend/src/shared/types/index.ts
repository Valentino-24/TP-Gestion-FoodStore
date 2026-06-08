// ── Shared domain types ──────────────────────────────────────────

export interface User {
  id: number
  nombre: string
  apellido: string
  email: string
  roles: string[]
}

export interface Producto {
  id: number
  nombre: string
  descripcion: string | null
  precio: number
  imagen_url: string | null
  categoria_id: number
  categoria_nombre?: string
  disponible: boolean
  stock_cantidad?: number
  activo: boolean
  creado_en?: string
  actualizado_en?: string
}

export interface ProductoListResponse {
  items: Producto[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Categoria {
  id: number
  nombre: string
  descripcion: string
  activo: boolean
}

export interface PedidoItem {
  id: number
  producto_id: number
  producto_nombre: string
  cantidad: number
  precio_unitario: number
  precio_snapshot: number
  subtotal: number
}

export interface Pedido {
  id: number
  total: number
  estado: string
  items: PedidoItem[]
  direccion_id: number | null
  direccion_snapshot?: string | null
  forma_pago_id: number | null
  creado_en: string
  actualizado_en: string
  historial?: HistorialEstado[]
}

export interface PedidoListResponse {
  items: Pedido[]
  total: number
  page: number
  size: number
  pages: number
}

export interface HistorialEstado {
  id: number
  pedido_id: number
  estado_desde: string | null
  estado_hasta: string
  usuario_id: number | null
  observacion: string | null
  creado_en: string
}

export interface Direccion {
  id: number
  calle: string
  numero: string
  ciudad: string
  provincia: string
  codigo_postal: string
  telefono_contacto: string | null
}

export interface Pago {
  id: number
  pedido_id: number
  monto: number
  metodo: string
  estado: string
  mp_pago_id: string | null
  mp_status: string | null
}

export interface AdminStats {
  pedidos_hoy: number
  ingresos_hoy: number
  total_productos: number
  total_clientes: number
}

export interface AdminDetailedStats {
  ingresos_por_dia: Array<{ fecha: string; total: number }>
  pedidos_por_estado: Array<{ estado: string; cantidad: number }>
  top_productos: Array<{ nombre: string; cantidad: number }>
}
