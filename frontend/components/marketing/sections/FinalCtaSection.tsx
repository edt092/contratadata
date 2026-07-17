import Container from '../Container'
import { PrimaryButton } from '../Button'

export default function FinalCtaSection() {
  return (
    <section className="py-24 sm:py-32">
      <Container className="flex flex-col items-center gap-7 text-center">
        <h2
          className="max-w-2xl text-[28px] leading-[1.2] sm:text-[38px]"
          style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, color: 'var(--brand-text)' }}
        >
          Cada oportunidad pública debería ser más fácil de encontrar, entender y verificar.
        </h2>
        <PrimaryButton href="/explorar" size="lg">Explorar ContrataData</PrimaryButton>
      </Container>
    </section>
  )
}
