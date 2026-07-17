import Container from '../Container'
import SectionHeading from '../SectionHeading'

const STEPS = [
  {
    n: '01',
    title: 'Define qué vende tu empresa',
    description: 'Sector, palabras clave, ubicación y rango de cuantía relevantes para tu negocio.',
  },
  {
    n: '02',
    title: 'ContrataData encuentra procesos y patrones relevantes',
    description: 'Cruza tus criterios con miles de procesos activos y el historial de entidades y competidores.',
  },
  {
    n: '03',
    title: 'Recibes oportunidades, alertas e inteligencia comercial',
    description: 'Notificaciones cuando aparece algo relevante, con la evidencia y el enlace a la fuente.',
  },
]

export default function HowItWorksSection() {
  return (
    <section id="como-funciona" className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading eyebrow="Cómo funciona" title="De datos públicos a decisiones comerciales" />

        <div className="grid gap-6 sm:grid-cols-3">
          {STEPS.map(step => (
            <div key={step.n} className="flex flex-col gap-3">
              <span
                className="text-[13px] font-bold"
                style={{ fontFamily: 'var(--font-mono)', color: 'var(--brand-primary)' }}
              >
                {step.n}
              </span>
              <h3 className="text-[15.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                {step.title}
              </h3>
              <p className="text-[13.5px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}
