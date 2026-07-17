'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { api, downloadBlob } from '@/lib/api'
import { useFeatureGate } from '@/lib/useFeatureGate'
import PaywallModal from './PaywallModal'

interface ExportReportButtonProps {
  kind: 'entity' | 'contractor'
  nombre: string
}

export default function ExportReportButton({ kind, nombre }: ExportReportButtonProps) {
  const { attempt, showPaywall, closePaywall, feature } = useFeatureGate('reports')
  const { getToken } = useAuth()
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)

  const fetchReport = (format: 'xlsx' | 'pdf') =>
    kind === 'entity' ? api.downloadEntityReport(getToken, nombre, format) : api.downloadContractorReport(getToken, nombre, format)

  const download = (format: 'xlsx' | 'pdf') => {
    setOpen(false)
    attempt(async () => {
      setBusy(true)
      try {
        const { blob, filename } = await fetchReport(format)
        downloadBlob(blob, filename)
      } catch {
        alert('No pudimos generar el reporte ahora. Intenta de nuevo en unos minutos.')
      } finally {
        setBusy(false)
      }
    })
  }

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(o => !o)}
        disabled={busy}
        style={{
          background: 'var(--surface2)',
          color: 'var(--text)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-sm)',
          padding: '9px 14px',
          fontSize: 13,
          fontWeight: 600,
          cursor: busy ? 'wait' : 'pointer',
          opacity: busy ? 0.7 : 1,
        }}
      >
        {busy ? 'Generando…' : '↓ Exportar reporte'}
      </button>

      {open && (
        <>
          <div onClick={() => setOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 90 }} />
          <div style={{
            position: 'absolute', top: '110%', right: 0, zIndex: 100,
            background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-md)', overflow: 'hidden', minWidth: 140,
          }}>
            <button
              onClick={() => download('xlsx')}
              style={{
                display: 'block', width: '100%', textAlign: 'left', background: 'transparent',
                border: 'none', padding: '10px 14px', fontSize: 13, color: 'var(--text)', cursor: 'pointer',
              }}
              className="row-hover"
            >
              Excel (.xlsx)
            </button>
            <button
              onClick={() => download('pdf')}
              style={{
                display: 'block', width: '100%', textAlign: 'left', background: 'transparent',
                border: 'none', padding: '10px 14px', fontSize: 13, color: 'var(--text)', cursor: 'pointer',
                borderTop: '1px solid var(--border)',
              }}
              className="row-hover"
            >
              PDF
            </button>
          </div>
        </>
      )}

      {showPaywall && <PaywallModal feature={feature} onClose={closePaywall} />}
    </div>
  )
}
