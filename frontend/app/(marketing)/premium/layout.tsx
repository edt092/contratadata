import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Planes',
  description: 'Planes de ContrataData: gratis para explorar el dashboard público, o Profesional para alertas, monitor de competidores y reportes.',
  alternates: { canonical: 'https://contratadata.xyz/premium' },
  openGraph: {
    title: 'Planes · ContrataData',
    description: 'Alertas guardadas, monitor de competidores y reportes Excel/PDF con el plan Profesional.',
    url: 'https://contratadata.xyz/premium',
  },
}

export default function PremiumLayout({ children }: { children: React.ReactNode }) {
  return children
}
