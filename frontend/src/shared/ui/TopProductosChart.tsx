import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: Array<{ nombre: string; cantidad: number }>
}

export default function TopProductosChart({ data }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">Top 5 productos más vendidos</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis
              type="category"
              dataKey="nombre"
              tick={{ fontSize: 11 }}
              width={140}
              tickFormatter={(val: string) => val.length > 18 ? `${val.slice(0, 18)}…` : val}
            />
            <Tooltip formatter={(value: unknown) => [Number(value), 'Unidades vendidas']} />
            <Bar dataKey="cantidad" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
