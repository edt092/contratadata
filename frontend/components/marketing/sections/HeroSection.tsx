import Container from '../Container'
import { PrimaryButton, SecondaryButton } from '../Button'
import HeroVisual from '../HeroVisual'

const TRUST_POINTS = [
  'Datos de fuentes oficiales',
  'Actualización diaria',
  'Cada dato enlaza a su fuente',
]

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-14 pb-20 sm:pt-20 sm:pb-28">
      <Container className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="flex flex-col items-start gap-6">
          <h1
            className="max-w-xl text-[38px] leading-[1.08] sm:text-[52px]"
            style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, letterSpacing: '-0.01em', color: 'var(--brand-text)' }}
          >
            Encuentra oportunidades para contratar con el Estado colombiano.
          </h1>

          <p className="max-w-lg text-[16px] leading-relaxed sm:text-[17px]" style={{ color: 'var(--brand-text-muted)' }}>
            Analiza procesos, entidades y competidores con información
            verificable de SECOP. Recibe alertas y descubre dónde puede
            crecer tu empresa.
          </p>

          <div className="flex flex-wrap gap-3">
            <PrimaryButton href="/explorar" size="lg">Explorar oportunidades</PrimaryButton>
            <SecondaryButton href="#como-funciona" size="lg">Ver cómo funciona</SecondaryButton>
          </div>

          <ul className="mt-2 flex flex-wrap gap-x-6 gap-y-2">
            {TRUST_POINTS.map(point => (
              <li key={point} className="flex items-center gap-2 text-[12.5px]" style={{ color: 'var(--brand-text-muted)' }}>
                <span aria-hidden className="inline-block h-1 w-1 rounded-full" style={{ background: 'var(--brand-verified)' }} />
                {point}
              </li>
            ))}
          </ul>
        </div>

        <div aria-hidden className="relative hidden aspect-[3/2] w-full lg:block">
          <HeroVisual />
        </div>
      </Container>
    </section>
  )
}
