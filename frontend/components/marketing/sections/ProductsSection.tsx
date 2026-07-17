import Container from '../Container'
import SectionHeading from '../SectionHeading'
import ProductCard from '../ProductCard'
import { SecondaryButton } from '../Button'

export default function ProductsSection() {
  return (
    <section id="producto" className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading
          eyebrow="Tres pilares"
          title="Explore, Signal y Ask"
          description="Una base de datos, tres formas de usarla: buscar, vigilar y preguntar."
        />

        <div className="grid gap-5 sm:grid-cols-3">
          <ProductCard
            name="ContrataData Explore"
            tagline="Busca y analiza procesos, contratos, entidades y proveedores."
            example="explorar.contratadata.xyz → filtra por entidad, sector y cuantía"
            status="disponible"
            accentColor="var(--brand-primary)"
            cta={<SecondaryButton href="/explorar">Abrir Explore</SecondaryButton>}
          />
          <ProductCard
            name="ContrataData Signal"
            tagline="Recibe alertas y monitorea entidades, competidores y oportunidades."
            example="Alerta: 'software · Antioquia · > $100M' → nuevo proceso hoy"
            status="disponible"
            accentColor="var(--brand-accent-blue)"
            cta={<SecondaryButton href="/alertas">Configurar alertas</SecondaryButton>}
          />
          <ProductCard
            name="ContrataData Ask"
            tagline="Haz preguntas en lenguaje natural y obtén respuestas respaldadas por fuentes oficiales."
            example="'¿Qué procesos de software en Antioquia cierran esta semana?'"
            status="proximamente"
            accentColor="var(--brand-accent-amber)"
          />
        </div>
      </Container>
    </section>
  )
}
