'use client'

import { BarChart } from '@tremor/react'
import type { CalidadItem } from '@/lib/api'

interface Props {
  data: CalidadItem[]
}

export default function CalidadChart({ data }: Props) {
  // Pivot rows into { motivo, SECOP: n, 'datos.gov.co': n }
  const pivot: Record<string, { SECOP: number; 'datos.gov.co': number }> = {}
  for (const r of data) {
    if (!pivot[r.motivo]) pivot[r.motivo] = { SECOP: 0, 'datos.gov.co': 0 }
    if (r.fuente === 'SECOP') pivot[r.motivo].SECOP += r.cantidad
    else pivot[r.motivo]['datos.gov.co'] += r.cantidad
  }
  const chartData = Object.entries(pivot).map(([motivo, counts]) => ({
    motivo: motivo.replace(/_/g, ' '),
    SECOP: counts.SECOP,
    'datos.gov.co': counts['datos.gov.co'],
  }))

  return (
    <div>
      <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)', marginBottom: 3 }}>
        Registros rechazados por motivo y fuente
      </div>
      <div style={{ fontSize: 12.5, color: 'var(--muted)', marginBottom: 20 }}>
        Contratos descartados durante el proceso de validación ETL.
      </div>
      <BarChart
        data={chartData}
        index="motivo"
        categories={['SECOP', 'datos.gov.co']}
        colors={['blue', 'violet']}
        valueFormatter={(v: number) => String(v)}
        showAnimation
        className="h-56 mt-2"
      />
    </div>
  )
}
