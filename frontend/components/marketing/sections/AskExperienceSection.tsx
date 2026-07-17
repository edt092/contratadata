import Container from '../Container'
import SectionHeading from '../SectionHeading'
import VerifiedCitation from '../VerifiedCitation'

export default function AskExperienceSection() {
  return (
    <section id="ask" className="py-20 sm:py-28">
      <Container className="grid items-center gap-10 lg:grid-cols-2">
        <SectionHeading
          eyebrow="ContrataData Ask · Próximamente"
          title="Pregunta en lenguaje natural, verifica con la fuente"
          description="Ask está en construcción. Así se verá: respuestas respaldadas siempre por el proceso original de SECOP, nunca una cifra sin evidencia."
        />

        <div
          className="flex flex-col gap-4 rounded-[var(--radius-lg)] p-5"
          style={{ background: 'var(--brand-surface)', border: '1px dashed var(--brand-border)' }}
        >
          <div
            className="self-start rounded-[var(--radius-full)] px-3 py-1 text-[10.5px] font-semibold uppercase"
            style={{ background: 'var(--brand-surface-elevated)', color: 'var(--brand-text-muted)', letterSpacing: '0.06em' }}
          >
            Vista previa — no funcional todavía
          </div>

          <p className="text-[14.5px] font-medium" style={{ color: 'var(--brand-text)' }}>
            “¿Qué procesos de software en Antioquia cierran esta semana?”
          </p>

          <div className="rounded-[var(--radius-md)] p-4" style={{ background: 'var(--brand-surface-elevated)' }}>
            <p className="mb-3 text-[13.5px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
              Encontré 3 procesos de tecnología en Antioquia con cierre entre
              el 18 y el 24 de julio, por un total aproximado de $1.200M.
            </p>
            <VerifiedCitation
              citation={{
                source_name: 'SECOP II',
                source_url: 'https://www.colombiacompra.gov.co/secop-ii',
                retrieved_at: new Date().toISOString(),
              }}
            />
          </div>

          <p className="text-[11.5px]" style={{ color: 'var(--brand-text-muted)' }}>
            Toda respuesta de Ask deberá verificarse contra el proceso original antes de tomar una decisión.
          </p>
        </div>
      </Container>
    </section>
  )
}
