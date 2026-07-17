import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Sobre ContrataData',
  description: 'ContrataData es una plataforma independiente de datos abiertos que consolida y visualiza contratos públicos del Estado colombiano desde SECOP y datos.gov.co.',
  alternates: { canonical: 'https://contratadata.xyz/sobre' },
}

export default function SobrePage() {
  return (
    <main style={{ maxWidth: 'var(--container-xl)', margin: '0 auto', padding: '64px 28px 96px' }} className="animate-fade">
      <div style={{ maxWidth: 680 }}>
        <h1
          style={{ margin: '0 0 20px', fontSize: 36, fontWeight: 400, letterSpacing: '-0.01em', color: 'var(--brand-text)', fontFamily: 'var(--font-serif)' }}
        >
          Sobre el proyecto
        </h1>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--brand-text-muted)', margin: '0 0 16px' }}>
          ContrataData es una plataforma de datos abiertos que consolida, normaliza y visualiza contratos públicos del Estado colombiano extraídos de{' '}
          <span style={{ color: 'var(--brand-text)', fontWeight: 600 }}>SECOP</span> y{' '}
          <span style={{ color: 'var(--brand-text)', fontWeight: 600 }}>datos.gov.co</span>.
        </p>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--brand-text-muted)', margin: '0 0 16px' }}>
          El propósito es hacer la contratación pública fácilmente explorable por periodistas, investigadores, veedores y ciudadanía.
        </p>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--brand-text-muted)', margin: '0 0 28px' }}>
          ContrataData es un proyecto independiente — no es un sitio oficial del Estado colombiano ni reemplaza a SECOP. Cada dato mostrado puede rastrearse hasta su fuente original.
        </p>
      </div>
    </main>
  )
}
