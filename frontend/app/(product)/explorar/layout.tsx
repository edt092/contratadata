import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Explorar contratos',
  description: 'Explora contratos del Estado colombiano por entidad, contratista, valor y fecha, con datos actualizados diariamente desde SECOP.',
  alternates: { canonical: 'https://contratadata.xyz/explorar' },
}

export default function ExplorarLayout({ children }: { children: React.ReactNode }) {
  return children
}
