'use client'

import { useFeedback } from '@/lib/feedback-context'

export default function FeedbackBanner() {
  const { openFeedback } = useFeedback()

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 16,
      flexWrap: 'wrap',
      marginBottom: 24,
      padding: '14px 18px',
      borderRadius: 'var(--radius-lg)',
      background: 'var(--primary-weak)',
      border: '1px solid var(--border)',
    }}>
      <div>
        <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text)' }}>
          Ayúdanos a mejorar ContrataData
        </div>
        <div style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 2 }}>
          ¿No encontraste algo, fue incómodo buscar o tienes una idea? Envíanos feedback sin login.
        </div>
      </div>
      <button
        onClick={openFeedback}
        style={{
          background: 'var(--primary)',
          color: 'var(--on-primary)',
          border: 'none',
          borderRadius: 'var(--radius-sm)',
          padding: '9px 16px',
          fontSize: 13,
          fontWeight: 700,
          cursor: 'pointer',
          flexShrink: 0,
        }}
      >
        Enviar feedback
      </button>
    </div>
  )
}
