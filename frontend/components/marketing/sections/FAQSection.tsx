import Container from '../Container'
import SectionHeading from '../SectionHeading'

const FAQS = [
  {
    q: '¿De dónde provienen los datos?',
    a: 'De fuentes públicas oficiales: principalmente SECOP II (vía la API de Socrata/datos.gov.co) y, progresivamente, otras fuentes de contratación pública colombiana.',
  },
  {
    q: '¿Cada cuánto se actualizan?',
    a: 'El pipeline corre automáticamente todos los días. La fecha exacta de la última actualización se muestra en las métricas de la plataforma.',
  },
  {
    q: '¿ContrataData reemplaza a SECOP?',
    a: 'No. ContrataData es una plataforma independiente que consolida, normaliza y analiza datos públicos de SECOP y datos.gov.co — no es un sitio oficial del Estado colombiano. Cada dato enlaza al proceso original para que puedas verificarlo.',
  },
  {
    q: '¿Cómo funcionan las alertas?',
    a: 'Guardas una búsqueda con tus filtros (entidad, sector, cuantía, ubicación) y te avisamos por email cuando aparece un proceso nuevo que coincide.',
  },
  {
    q: '¿Puedo exportar información?',
    a: 'Sí, el plan Profesional incluye exportación de reportes en Excel y PDF para entidades y contratistas.',
  },
  {
    q: '¿Existe API?',
    a: 'Está en el roadmap como parte del plan API. Hoy la API interna alimenta el dashboard público; una API para terceros llega próximamente.',
  },
  {
    q: '¿Cómo verifico un resultado?',
    a: 'Cada contrato, proceso o cifra en ContrataData puede rastrearse hasta su fuente original en SECOP — busca el enlace o la referencia junto al dato.',
  },
  {
    q: '¿Qué incluye el plan gratuito?',
    a: 'El explorador completo de contratos, perfiles de entidades y contratistas, y gráficas básicas — sin necesidad de tarjeta de crédito.',
  },
]

export default function FAQSection() {
  return (
    <section className="py-20 sm:py-28">
      <Container className="flex flex-col gap-10">
        <SectionHeading eyebrow="Preguntas frecuentes" title="Lo que más nos preguntan" />

        <div className="flex flex-col gap-3">
          {FAQS.map(faq => (
            <details
              key={faq.q}
              className="group rounded-[var(--radius-lg)] px-5 py-4"
              style={{ background: 'var(--brand-surface)', border: '1px solid var(--brand-border)' }}
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[14.5px] font-semibold" style={{ color: 'var(--brand-text)' }}>
                {faq.q}
                <span aria-hidden className="shrink-0 transition-transform group-open:rotate-45" style={{ color: 'var(--brand-primary)' }}>
                  +
                </span>
              </summary>
              <p className="mt-3 text-[13.5px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
                {faq.a}
              </p>
            </details>
          ))}
        </div>
      </Container>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: FAQS.map(faq => ({
              '@type': 'Question',
              name: faq.q,
              acceptedAnswer: { '@type': 'Answer', text: faq.a },
            })),
          }),
        }}
      />
    </section>
  )
}
