'use client'

import Link from 'next/link'
import type { FeatureKey } from '@/lib/api'

interface ProUpgradeCardProps {
  feature?: FeatureKey
}

const BENEFICIOS = [
  'Alertas guardadas por entidad, contratista o filtro',
  'Monitor de competidores',
  'Reportes Excel/PDF de entidades y contratistas',
  'Acceso anticipado a nuevas funciones',
]

export default function ProUpgradeCard({ feature }: ProUpgradeCardProps) {
  const href = feature ? `/premium?feature=${feature}` : '/premium'

  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12,
      padding: '24px 22px',
    }}>
      <div style={{ fontSize: 17, fontWeight: 800, color: 'var(--text)', marginBottom: 4 }}>
        ContrataData Pro
      </div>
      <div style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 16 }}>
        Inteligencia comercial para venderle al Estado colombiano.
      </div>

      <div style={{
        display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 16,
        padding: '10px 14px', borderRadius: 8, background: 'var(--primary-weak)',
      }}>
        <span style={{ fontSize: 20, fontWeight: 800, color: 'var(--primary)' }}>COP $149.000</span>
        <span style={{ fontSize: 12.5, color: 'var(--muted)' }}>/mes · o ahorra con el plan anual</span>
      </div>

      <ul style={{ margin: '0 0 18px', padding: '0 0 0 18px', fontSize: 13, color: 'var(--text)', lineHeight: 1.9 }}>
        {BENEFICIOS.map(b => <li key={b}>{b}</li>)}
      </ul>

      <Link
        href={href}
        style={{
          display: 'inline-block', background: 'var(--primary)', color: '#fff', textDecoration: 'none',
          border: 'none', borderRadius: 8, padding: '10px 18px', fontSize: 13.5, fontWeight: 600,
        }}
      >
        Ver planes y precios
      </Link>
    </div>
  )
}
