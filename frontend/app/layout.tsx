import type { Metadata } from 'next'
import { Inter, Instrument_Serif, JetBrains_Mono } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'
import { ThemeProvider } from '@/lib/theme-context'
import { QueryProvider } from '@/lib/query-provider'
import { FeedbackProvider } from '@/lib/feedback-context'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })
const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono', display: 'swap' })
// Serif editorial: solo para momentos de marca en la landing (titulares),
// no para texto de producto — un único peso para no inflar el bundle de fuentes.
const serif = Instrument_Serif({ subsets: ['latin'], weight: '400', variable: '--font-serif', display: 'swap' })

export const metadata: Metadata = {
  title: {
    default: 'ContrataData — Inteligencia de contratación pública en Colombia',
    template: '%s · ContrataData',
  },
  description: 'Encuentra oportunidades para contratar con el Estado colombiano. Analiza procesos, entidades y competidores con información verificable de SECOP.',
  metadataBase: new URL('https://contratadata.xyz'),
  icons: { icon: '/favicon.svg' },
  openGraph: {
    title: 'ContrataData — Inteligencia de contratación pública en Colombia',
    description: 'Encuentra oportunidades, monitorea entidades y competidores, y consulta datos verificables de SECOP.',
    url: 'https://contratadata.xyz',
    siteName: 'ContrataData',
    locale: 'es_CO',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ContrataData — Inteligencia de contratación pública en Colombia',
    description: 'Encuentra oportunidades, monitorea entidades y competidores, y consulta datos verificables de SECOP.',
  },
  alternates: {
    canonical: 'https://contratadata.xyz',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning className={`${inter.variable} ${mono.variable} ${serif.variable}`}>
      <body>
        <ClerkProvider>
          <QueryProvider>
            <ThemeProvider>
              <FeedbackProvider>
                {children}
              </FeedbackProvider>
            </ThemeProvider>
          </QueryProvider>
        </ClerkProvider>
      </body>
    </html>
  )
}
