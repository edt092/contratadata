import type { Metadata } from 'next'
import HeroSection from '@/components/marketing/sections/HeroSection'
import ProductDemoSection from '@/components/marketing/sections/ProductDemoSection'
import TrustMetricsSection from '@/components/marketing/sections/TrustMetricsSection'
import ProductsSection from '@/components/marketing/sections/ProductsSection'
import SourcesSection from '@/components/marketing/sections/SourcesSection'
import HowItWorksSection from '@/components/marketing/sections/HowItWorksSection'
import UseCasesSection from '@/components/marketing/sections/UseCasesSection'
import SignalExperienceSection from '@/components/marketing/sections/SignalExperienceSection'
import AskExperienceSection from '@/components/marketing/sections/AskExperienceSection'
import PlansPreviewSection from '@/components/marketing/sections/PlansPreviewSection'
import FAQSection from '@/components/marketing/sections/FAQSection'
import FinalCtaSection from '@/components/marketing/sections/FinalCtaSection'

export const metadata: Metadata = {
  title: 'ContrataData — Inteligencia de contratación pública en Colombia',
  description: 'Encuentra oportunidades para contratar con el Estado colombiano. Analiza procesos, entidades y competidores con información verificable de SECOP.',
  alternates: { canonical: 'https://contratadata.xyz' },
}

const ORG_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'ContrataData',
  url: 'https://contratadata.xyz',
  description: 'Plataforma independiente de inteligencia de contratación pública colombiana, basada en datos abiertos de SECOP y datos.gov.co.',
  logo: 'https://contratadata.xyz/favicon.svg',
}

const WEBAPP_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: 'ContrataData',
  url: 'https://contratadata.xyz',
  applicationCategory: 'BusinessApplication',
  operatingSystem: 'Web',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'COP' },
}

export default function LandingPage() {
  return (
    <>
      <HeroSection />
      <ProductDemoSection />
      <TrustMetricsSection />
      <ProductsSection />
      <SourcesSection />
      <HowItWorksSection />
      <UseCasesSection />
      <SignalExperienceSection />
      <AskExperienceSection />
      <PlansPreviewSection />
      <FAQSection />
      <FinalCtaSection />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(ORG_SCHEMA) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(WEBAPP_SCHEMA) }}
      />
    </>
  )
}
