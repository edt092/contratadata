import Link from 'next/link'
import Container from './Container'

interface FooterColumn {
  title: string
  links: { label: string; href?: string }[]
}

const COLUMNS: FooterColumn[] = [
  {
    title: 'Producto',
    links: [
      { label: 'Explorar contratos', href: '/explorar' },
      { label: 'Alertas', href: '/alertas' },
      { label: 'Competidores', href: '/competidores' },
      { label: 'Planes', href: '/premium' },
    ],
  },
  {
    title: 'Recursos',
    links: [
      { label: 'Sobre ContrataData', href: '/sobre' },
      { label: 'Documentación (próximamente)' },
      { label: 'API (próximamente)' },
    ],
  },
  {
    title: 'Empresa',
    links: [
      { label: 'Sobre el proyecto', href: '/sobre' },
      { label: 'Estado del sistema', href: '/pipeline' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacidad (próximamente)' },
      { label: 'Términos (próximamente)' },
    ],
  },
]

export default function Footer() {
  return (
    <footer style={{ borderTop: '1px solid var(--brand-border)', background: 'var(--brand-bg)' }}>
      <Container className="grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-5">
        <div className="flex flex-col gap-3 lg:col-span-1">
          <span className="text-[16px] font-extrabold" style={{ color: 'var(--brand-text)', letterSpacing: '-0.02em' }}>
            ContrataData
          </span>
          <p className="max-w-[220px] text-[12.5px] leading-relaxed" style={{ color: 'var(--brand-text-muted)' }}>
            Plataforma independiente. No es un sitio oficial del Estado
            colombiano — consolida y analiza datos públicos de SECOP y
            datos.gov.co.
          </p>
        </div>

        {COLUMNS.map(col => (
          <div key={col.title} className="flex flex-col gap-3">
            <h4
              className="text-[11px] font-semibold uppercase"
              style={{ color: 'var(--brand-text-muted)', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)' }}
            >
              {col.title}
            </h4>
            <ul className="flex flex-col gap-2">
              {col.links.map(link =>
                link.href ? (
                  <li key={link.label}>
                    <Link href={link.href} className="text-[13.5px] transition-colors hover:opacity-80" style={{ color: 'var(--brand-text)' }}>
                      {link.label}
                    </Link>
                  </li>
                ) : (
                  <li key={link.label} className="text-[13.5px]" style={{ color: 'var(--brand-text-muted)' }}>
                    {link.label}
                  </li>
                ),
              )}
            </ul>
          </div>
        ))}
      </Container>

      <Container className="flex flex-col gap-2 border-t py-6 sm:flex-row sm:items-center sm:justify-between" style={{ borderColor: 'var(--brand-border)' }}>
        <p className="text-[12px]" style={{ color: 'var(--brand-text-muted)' }}>
          © {new Date().getFullYear()} ContrataData. Datos de SECOP I, SECOP II y datos.gov.co.
        </p>
        <a href="mailto:hola@contratadata.xyz" className="text-[12px] transition-colors hover:opacity-80" style={{ color: 'var(--brand-text-muted)' }}>
          hola@contratadata.xyz
        </a>
      </Container>
    </footer>
  )
}
