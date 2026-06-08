import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS: Record<string, string> = {
  PENDIENTE: '#eab308',
  CONFIRMADO: '#3b82f6',
  EN_PREPARACION: '#6366f1',
  EN_CAMINO: '#a855f7',
  ENTREGADO: '#22c55e',
  CANCELADO: '#ef4444',
}

interface Props {
  data: Array<{ estado: string; cantidad: number }>
}

export default function PedidosPorEstadoChart({ data }: Props) {
  const chartData = data.map((d) => ({
    name: d.estado,
    value: d.cantidad,
    color: COLORS[d.estado] ?? '#9ca3af',
  }))

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">Pedidos por estado</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
              label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
              labelLine={{ strokeWidth: 1 }}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value: unknown) => [Number(value), 'Pedidos']} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
