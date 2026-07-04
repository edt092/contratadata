export default function SobrePage() {
  return (
    <main style={{ maxWidth: 1340, margin: '0 auto', padding: '32px 28px 80px' }} className="animate-fade">
      <div style={{ maxWidth: 680 }}>
        <h1 style={{ margin: '0 0 16px', fontSize: 30, fontWeight: 800, letterSpacing: '-0.025em', color: 'var(--text)' }}>
          Sobre el proyecto
        </h1>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--muted)', margin: '0 0 16px' }}>
          ContrataData es una plataforma de datos abiertos que consolida, normaliza y visualiza contratos públicos del Estado colombiano extraídos de{' '}
          <span style={{ color: 'var(--text)', fontWeight: 600 }}>SECOP</span> y{' '}
          <span style={{ color: 'var(--text)', fontWeight: 600 }}>datos.gov.co</span>.
        </p>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--muted)', margin: '0 0 28px' }}>
          El propósito es hacer la contratación pública fácilmente explorable por periodistas, investigadores, veedores y ciudadanía.
        </p>
      </div>
    </main>
  )
}
