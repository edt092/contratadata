'use client'

import { api } from '@/lib/api'
import ChartImage from './ChartImage'

interface Props {
  theme: 'dark' | 'light'
  entidad?: string
  estado?: string
  desde?: string
  hasta?: string
}

export default function EvolucionChart({ theme, entidad, estado, desde, hasta }: Props) {
  return (
    <ChartImage
      src={api.imageUrl('/charts/images/monthly-evolution.png', { theme, entidad, estado, desde, hasta })}
      alt="Evolución mensual del valor contratado"
      title={entidad ? 'Evolución de gasto por mes' : 'Evolución temporal del valor contratado'}
      subtitle="Valor total por mes, con media móvil de 3 meses para separar la tendencia del ruido."
    />
  )
}
