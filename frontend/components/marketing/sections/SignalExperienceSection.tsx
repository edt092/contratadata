import Container from '../Container'
import SectionHeading from '../SectionHeading'
import { SecondaryButton } from '../Button'

const STEPS = [
  { label: 'Alerta configurada', detail: '"Software · Antioquia · > $100.000.000"', done: true },
  { label: 'Nueva coincidencia', detail: 'Alcaldía de Medellín publicó un proceso hoy', done: true },
  { label: 'Resumen diario', detail: '3 procesos nuevos, 1 entidad monitoreada con movimiento', done: true },
  { label: 'Envío por email', detail: 'Enviado a las 7:00 a. m. hora Colombia', done: true },
  { label: 'Webhook / WhatsApp', detail: 'Integraciones adicionales', done: false },
]

export default function SignalExperienceSection() {
  return (
    <section className="py-20 sm:py-28">
      <Container className="grid items-center gap-10 lg:grid-cols-2">
        <SectionHeading
          eyebrow="ContrataData Signal"
          title="Deja de revisar SECOP todos los días"
          description="Configura una alerta una vez y recibe solo lo relevante — con la fuente y la fecha de cada coincidencia."
        />

        <div className="flex flex-col gap-3 rounded-[var(--radius-lg)] p-5" style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}>
          {STEPS.map(step => (
            <div key={step.label} className="flex items-start gap-3">
              <span
                aria-hidden
                className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold"
                style={{
                  background: step.done ? 'color-mix(in srgb, var(--brand-primary) 18%, transparent)' : 'transparent',
                  color: step.done ? 'var(--brand-primary)' : 'var(--brand-text-muted)',
                  border: step.done ? 'none' : '1px dashed var(--brand-border)',
                }}
              >
                {step.done ? '✓' : '···'}
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[13.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                    {step.label}
                  </span>
                  {!step.done && (
                    <span className="text-[10px] font-semibold uppercase" style={{ color: 'var(--brand-text-muted)', letterSpacing: '0.06em' }}>
                      Futuro
                    </span>
                  )}
                </div>
                <p className="text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
                  {step.detail}
                </p>
              </div>
            </div>
          ))}
          <div className="pt-2">
            <SecondaryButton href="/alertas">Configurar una alerta</SecondaryButton>
          </div>
        </div>
      </Container>
    </section>
  )
}
