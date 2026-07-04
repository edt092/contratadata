'use client'

import { useState } from 'react'
import { api, type FeatureKey } from '@/lib/api'

interface ProUpgradeCardProps {
  feature?: FeatureKey
}

const BENEFICIOS = [
  'Alertas guardadas por entidad, contratista o filtro',
  'Monitor de competidores',
  'Reportes Excel/PDF de entidades y contratistas',
  'Acceso anticipado a nuevas funciones',
]

type Status = 'idle' | 'enviando' | 'enviado' | 'error'

export default function ProUpgradeCard({ feature }: ProUpgradeCardProps) {
  const [status, setStatus] = useState<Status>('idle')

  const solicitar = async () => {
    setStatus('enviando')
    try {
      await api.requestProAccess({ feature })
      setStatus('enviado')
    } catch {
      setStatus('error')
    }
  }

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
        <span style={{ fontSize: 12.5, color: 'var(--muted)' }}>/mes · precio beta</span>
      </div>

      <ul style={{ margin: '0 0 18px', padding: '0 0 0 18px', fontSize: 13, color: 'var(--text)', lineHeight: 1.9 }}>
        {BENEFICIOS.map(b => <li key={b}>{b}</li>)}
      </ul>

      {status === 'enviado' ? (
        <p style={{ fontSize: 13.5, color: 'var(--success)', fontWeight: 600, margin: 0 }}>
          ✓ Gracias por tu interés. Te contactaremos pronto para coordinar el acceso beta.
        </p>
      ) : (
        <>
          {status === 'error' && (
            <div style={{
              padding: '10px 12px', borderRadius: 8, fontSize: 13, marginBottom: 12,
              background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--danger)',
            }}>
              No pudimos registrar tu interés ahora. Intenta de nuevo en unos minutos.
            </div>
          )}
          <button
            onClick={solicitar}
            disabled={status === 'enviando'}
            style={{
              background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: 8,
              padding: '10px 18px', fontSize: 13.5, fontWeight: 600,
              cursor: status === 'enviando' ? 'not-allowed' : 'pointer',
              opacity: status === 'enviando' ? 0.6 : 1,
            }}
          >
            {status === 'enviando' ? 'Enviando…' : 'Solicitar acceso Pro'}
          </button>
        </>
      )}
    </div>
  )
}
