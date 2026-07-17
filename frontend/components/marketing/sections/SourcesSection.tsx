import Container from '../Container'
import SectionHeading from '../SectionHeading'
import SourceBadge from '../SourceBadge'

const SOURCES: { label: string; status: 'connected' | 'planned' }[] = [
  { label: 'SECOP II', status: 'connected' },
  { label: 'SECOP I', status: 'planned' },
  { label: 'Tienda Virtual del Estado Colombiano', status: 'planned' },
  { label: 'Planes Anuales de Adquisiciones', status: 'planned' },
  { label: 'Datos Abiertos Colombia', status: 'planned' },
  { label: 'Colombia Compra Eficiente', status: 'planned' },
]

const TRACE_FIELDS = ['Fuente', 'URL original', 'Fecha de recuperación', 'Fecha de actualización', 'Identificador de dataset', 'Estado de calidad']

export default function SourcesSection() {
  return (
    <section id="fuentes" className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading
          eyebrow="Fuentes primarias"
          title="Cada dato tiene un origen verificable"
          description="ContrataData no reemplaza a SECOP: lo consolida, normaliza y enlaza de vuelta al registro original."
        />

        <div className="flex flex-wrap gap-2.5">
          {SOURCES.map(s => (
            <SourceBadge key={s.label} label={s.label} status={s.status} />
          ))}
        </div>

        <div className="rounded-[var(--radius-lg)] p-6" style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}>
          <h3 className="mb-4 text-[14px] font-semibold" style={{ color: 'var(--brand-text)' }}>
            Trazabilidad de cada registro
          </h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {TRACE_FIELDS.map(f => (
              <div key={f} className="flex items-center gap-2 text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
                <span aria-hidden style={{ color: 'var(--brand-verified)' }}>✓</span>
                {f}
              </div>
            ))}
          </div>
        </div>
      </Container>
    </section>
  )
}
