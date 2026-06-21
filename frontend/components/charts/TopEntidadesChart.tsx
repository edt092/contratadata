'use client'

import { BarList } from '@tremor/react'
import { fmtAbbr } from '@/lib/format'
import type { BarItem } from '@/lib/api'

interface Props {
  items: BarItem[]
  onItemClick?: (nombre: string) => void
}

export default function TopEntidadesChart({ items, onItemClick }: Props) {
  const data = items.map(e => ({
    name: e.nombre,
    value: e.valor_total,
    href: onItemClick ? undefined : undefined,
  }))

  return (
    <div>
      <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)', marginBottom: 3 }}>
        Top entidades por valor contratado
      </div>
      <div style={{ fontSize: 12.5, color: 'var(--muted)', marginBottom: 20 }}>
        Suma del valor de todos los contratos por entidad pública — refleja los filtros activos.
      </div>
      <BarList
        data={data}
        valueFormatter={v => fmtAbbr(v)}
        onValueChange={onItemClick ? item => onItemClick(item.name) : undefined}
        color="blue"
        className="mt-2"
      />
    </div>
  )
}
