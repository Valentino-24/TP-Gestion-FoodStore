import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: Array<{ fecha: string; total: number }>
}

export default function IngresosChart({ data }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">Ingresos últimos 7 días</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="fecha"
              tick={{ fontSize: 12 }}
              tickFormatter={(val: string) => {
                const d = new Date(val)
                return d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' })
              }}
            />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(val: number) => `$${val}`} />
            <Tooltip
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Ingresos']}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              labelFormatter={(label: any) => new Date(String(label)).toLocaleDateString('es-AR')}
            />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ r: 4, fill: '#2563eb' }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
