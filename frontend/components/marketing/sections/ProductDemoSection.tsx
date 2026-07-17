import Container from '../Container'
import SectionHeading from '../SectionHeading'
import SourceBadge from '../SourceBadge'
import { SecondaryButton } from '../Button'

const DEMO_OPORTUNIDAD = {
  titulo: 'Desarrollo de plataforma web de trámites en línea',
  entidad: 'Alcaldía de Medellín',
  cuantia: '$480.000.000',
  cierre: '28 de agosto de 2026',
  modalidad: 'Selección abreviada',
  ubicacion: 'Antioquia',
}

export default function ProductDemoSection() {
  return (
    <section className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading
          eyebrow="ContrataData Explore"
          title="Busca como en un buscador real, no como en un PDF de 300 páginas"
          description="Filtra por entidad, sector, cuantía y ubicación. Cada resultado enlaza al proceso original en SECOP."
        />

        <div
          className="overflow-hidden rounded-[var(--radius-lg)]"
          style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
        >
          <div className="flex items-center justify-between gap-3 px-5 py-3.5" style={{ borderBottom: '1px solid var(--brand-border)' }}>
            <span className="text-[11px] font-semibold uppercase" style={{ color: 'var(--brand-text-muted)', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)' }}>
              Vista de producto — datos de ejemplo
            </span>
            <SourceBadge label="SECOP II" />
          </div>

          <div className="flex flex-col gap-3 px-5 py-4" style={{ borderBottom: '1px solid var(--brand-border)' }}>
            <div
              className="flex items-center gap-2 rounded-[var(--radius-md)] px-3.5 py-2.5 text-[13.5px]"
              style={{ background: 'var(--brand-surface-elevated)', color: 'var(--brand-text-muted)' }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden>
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="M20 20l-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              software en Antioquia
            </div>
            <div className="flex flex-wrap gap-2">
              {['Modalidad: Selección abreviada', 'Cierra esta semana', 'Cuantía > $100M'].map(f => (
                <span
                  key={f}
                  className="rounded-[var(--radius-full)] px-2.5 py-1 text-[11.5px]"
                  style={{ background: 'var(--brand-surface-elevated)', color: 'var(--brand-text-muted)', border: '1px solid var(--brand-border)' }}
                >
                  {f}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-col gap-2">
              <h3 className="text-[15.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                {DEMO_OPORTUNIDAD.titulo}
              </h3>
              <p className="text-[13px]" style={{ color: 'var(--brand-text-muted)' }}>
                {DEMO_OPORTUNIDAD.entidad} · {DEMO_OPORTUNIDAD.ubicacion}
              </p>
              <div className="flex flex-wrap gap-x-5 gap-y-1 text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
                <span>Cuantía: <strong style={{ color: 'var(--brand-text)' }}>{DEMO_OPORTUNIDAD.cuantia}</strong></span>
                <span>Cierra: <strong style={{ color: 'var(--brand-text)' }}>{DEMO_OPORTUNIDAD.cierre}</strong></span>
                <span>{DEMO_OPORTUNIDAD.modalidad}</span>
              </div>
            </div>
            <SecondaryButton href="/explorar">Abrir explorador</SecondaryButton>
          </div>
        </div>
      </Container>
    </section>
  )
}
