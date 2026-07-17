'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { fmtInt, fmtAbbr, fmtDateTime } from '@/lib/format'
import Container from '../Container'
import DataMetric from '../DataMetric'

/** Métricas de confianza — datos reales de GET /pipeline/stats (endpoint
 * público, ya existente). No bloquea el hero: esta sección es la única que
 * espera al backend, con skeleton mientras carga. Si falla, simplemente no
 * muestra números — nunca cifras inventadas. */
export default function TrustMetricsSection() {
  const { data, isLoading } = useQuery({
    queryKey: ['global-stats'],
    queryFn: api.globalStats,
    staleTime: 5 * 60_000,
  })

  const metrics = [
    { label: 'Contratos indexados', value: data ? fmtInt(data.total_contratos) : undefined },
    { label: 'Entidades analizadas', value: data ? fmtInt(data.entidades_unicas) : undefined },
    { label: 'Contratistas', value: data ? fmtInt(data.contratistas_unicos) : undefined },
    { label: 'Valor público analizado', value: data ? fmtAbbr(data.valor_total) : undefined },
  ]

  return (
    <section className="py-14" style={{ borderTop: '1px solid var(--brand-border)', borderBottom: '1px solid var(--brand-border)' }}>
      <Container className="flex flex-col gap-8">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {metrics.map(m => (
            <DataMetric key={m.label} label={m.label} value={m.value} loading={isLoading} />
          ))}
        </div>
        {data?.fecha_mas_reciente && (
          <p className="text-[12px]" style={{ color: 'var(--brand-text-muted)', fontFamily: 'var(--font-mono)' }}>
            Último contrato registrado: {fmtDateTime(data.fecha_mas_reciente)} · fuente SECOP II
          </p>
        )}
      </Container>
    </section>
  )
}
