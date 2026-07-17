import Container from '../Container'
import SectionHeading from '../SectionHeading'
import PricingPreview, { type PricingPlanSummary } from '../PricingPreview'
import { PrimaryButton, SecondaryButton } from '../Button'

const PLANS: PricingPlanSummary[] = [
  {
    id: 'gratis',
    name: 'Gratis',
    price: '$0',
    audience: 'Para explorar el dashboard público',
    features: ['Explorador de contratos', 'Perfiles de entidades y contratistas', 'Gráficas básicas'],
    cta: <SecondaryButton href="/explorar">Empezar gratis</SecondaryButton>,
  },
  {
    id: 'profesional',
    name: 'Profesional',
    price: '$149.000',
    priceSuffix: '/mes',
    audience: 'Proveedores y equipos comerciales',
    features: ['Alertas guardadas ilimitadas', 'Monitor de competidores', 'Reportes Excel/PDF'],
    cta: <PrimaryButton href="/premium">Ver plan Profesional</PrimaryButton>,
    highlighted: true,
  },
  {
    id: 'equipo',
    name: 'Equipo',
    audience: 'Equipos comerciales B2B',
    features: ['Varios usuarios', 'Alertas compartidas', 'Soporte prioritario'],
    cta: <SecondaryButton href="/premium">Contáctanos</SecondaryButton>,
  },
]

export default function PlansPreviewSection() {
  return (
    <section className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading
          eyebrow="Planes"
          title="Un plan para cada forma de vender al Estado"
          description="Planes Equipo, API y Enterprise llegan próximamente — hoy puedes empezar gratis o con el plan Profesional."
        />

        <PricingPreview plans={PLANS} />

        <div className="flex justify-center">
          <SecondaryButton href="/premium">Ver todos los planes</SecondaryButton>
        </div>
      </Container>
    </section>
  )
}
