'use client'

import { AreaChart } from '@tremor/react'
import { fmtAbbr } from '@/lib/format'
import type { MonthlyPoint } from '@/lib/api'

interface Props {
  data: MonthlyPoint[]
}

export default function EvolucionChart({ data }: Props) {
  const chartData = data.map(p => ({
    periodo: p.periodo,
    'Valor COP': p.valor_total,
  }))

  return (
    <div>
      <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)', marginBottom: 3 }}>
        Evolución temporal del valor contratado
      </div>
      <div style={{ fontSize: 12.5, color: 'var(--muted)', marginBottom: 20 }}>
        Valor total de contratos por mes.
      </div>
      <AreaChart
        data={chartData}
        index="periodo"
        categories={['Valor COP']}
        colors={['blue']}
        valueFormatter={(v: number) => fmtAbbr(v)}
        showAnimation
        showLegend={false}
        showGradient
        className="h-56 mt-2"
      />
    </div>
  )
}
