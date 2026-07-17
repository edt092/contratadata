import { Search, TrendingUp, Users, Building2, BarChart3, Code2 } from 'lucide-react'
import Container from '../Container'
import SectionHeading from '../SectionHeading'
import UseCaseCard from '../UseCaseCard'

const USE_CASES = [
  { icon: Search, title: 'Descubrir licitaciones', description: 'Encuentra procesos que coinciden con lo que vende tu empresa antes de que se te pasen.' },
  { icon: TrendingUp, title: 'Preparar estrategia comercial', description: 'Entiende qué entidades compran, cuándo y en qué montos para priorizar tu pipeline.' },
  { icon: Users, title: 'Monitorear competidores', description: 'Sigue a contratistas específicos y recibe aviso cuando ganen un nuevo contrato.' },
  { icon: Building2, title: 'Investigar entidades', description: 'Revisa el historial de contratación de una entidad antes de participar en un proceso.' },
  { icon: BarChart3, title: 'Analizar mercados públicos', description: 'Mide el tamaño real de un sector dentro de la contratación estatal colombiana.' },
  { icon: Code2, title: 'Automatizar flujos mediante API', description: 'Integra datos verificables de SECOP directamente en tus propios sistemas.' },
]

export default function UseCasesSection() {
  return (
    <section className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading eyebrow="Casos de uso" title="Para quién es ContrataData" />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {USE_CASES.map(uc => (
            <UseCaseCard
              key={uc.title}
              icon={<uc.icon size={18} strokeWidth={2} />}
              title={uc.title}
              description={uc.description}
            />
          ))}
        </div>
      </Container>
    </section>
  )
}
