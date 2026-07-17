import MarketingHeader from '@/components/marketing/MarketingHeader'
import Footer from '@/components/marketing/Footer'

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="marketing flex min-h-screen flex-col">
      <MarketingHeader />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  )
}
