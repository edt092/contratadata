import Image from 'next/image'
import Link from 'next/link'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <header style={{ padding: '20px 28px' }}>
        <Link
          href="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 10,
            textDecoration: 'none',
            fontWeight: 800,
            fontSize: 15,
            color: 'var(--text)',
          }}
        >
          <Image src="/favicon.svg" alt="ContrataData" width={28} height={19} priority />
          ContrataData
        </Link>
      </header>
      {children}
    </div>
  )
}
