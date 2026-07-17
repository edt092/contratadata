'use client'

import { useEffect, useState } from 'react'
import { api, type FeedbackImportance, type FeedbackType } from '@/lib/api'

interface FeedbackModalProps {
  open: boolean
  onClose: () => void
}

type Status = 'idle' | 'enviando' | 'enviado' | 'error'

const TIPOS: { value: FeedbackType; label: string }[] = [
  { value: 'no_encontre', label: 'No encontré lo que buscaba' },
  { value: 'dificil_buscar', label: 'Fue difícil buscar' },
  { value: 'error', label: 'Encontré un error' },
  { value: 'sugerencia', label: 'Quiero sugerir una función' },
  { value: 'otro', label: 'Otro' },
]

const IMPORTANCIAS: { value: FeedbackImportance; label: string }[] = [
  { value: 'baja', label: 'Baja' },
  { value: 'media', label: 'Media' },
  { value: 'alta', label: 'Alta' },
]

const labelStyle: React.CSSProperties = {
  fontSize: 10.5,
  fontWeight: 600,
  letterSpacing: '0.07em',
  textTransform: 'uppercase',
  color: 'var(--muted)',
}

const inputStyle: React.CSSProperties = {
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  padding: '9px 11px',
  fontSize: 13.5,
  color: 'var(--text)',
  outline: 'none',
  width: '100%',
  fontFamily: 'inherit',
}

const primaryBtnStyle: React.CSSProperties = {
  background: 'var(--primary)',
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  padding: '10px 18px',
  fontSize: 13.5,
  fontWeight: 600,
  cursor: 'pointer',
}

export default function FeedbackModal({ open, onClose }: FeedbackModalProps) {
  const [tipo, setTipo] = useState<FeedbackType>('no_encontre')
  const [comentario, setComentario] = useState('')
  const [email, setEmail] = useState('')
  const [importancia, setImportancia] = useState<FeedbackImportance>('media')
  const [consentimiento, setConsentimiento] = useState(false)
  const [status, setStatus] = useState<Status>('idle')

  // Reinicia el estado al abrir sin pasar por un efecto extra (ver
  // https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes).
  const [prevOpen, setPrevOpen] = useState(open)
  if (open !== prevOpen) {
    setPrevOpen(open)
    if (open) setStatus('idle')
  }

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  const comentarioValido = comentario.trim().length >= 3

  const resetForm = () => {
    setTipo('no_encontre')
    setComentario('')
    setEmail('')
    setImportancia('media')
    setConsentimiento(false)
  }

  const handleSubmit = async () => {
    if (!comentarioValido || status === 'enviando') return
    setStatus('enviando')

    const search = window.location.search.replace(/^\?/, '')

    try {
      await api.submitFeedback({
        feedback_type: tipo,
        comment: comentario.trim(),
        email: email.trim() || undefined,
        importance: importancia,
        consent_contact: consentimiento,
        page_url: window.location.href,
        route: window.location.pathname,
        filters_json: search ? Object.fromEntries(new URLSearchParams(search)) : null,
        user_agent: navigator.userAgent,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        referrer: document.referrer || undefined,
      })
      setStatus('enviado')
      resetForm()
    } catch {
      setStatus('error')
    }
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 200,
        background: 'rgba(0,0,0,0.5)',
        backdropFilter: 'blur(3px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        className="animate-fade"
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          padding: 26,
          width: '100%',
          maxWidth: 460,
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 6 }}>
          <h2 style={{ margin: 0, fontSize: 19, fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.02em' }}>
            Ayúdanos a mejorar
          </h2>
          <button
            onClick={onClose}
            aria-label="Cerrar"
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: 18, lineHeight: 1, padding: 4 }}
          >
            ✕
          </button>
        </div>

        {status === 'enviado' ? (
          <>
            <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text)', margin: '14px 0 20px' }}>
              Gracias por ayudarnos a mejorar ContrataData. Si dejaste tu email, te tendremos en cuenta para créditos premium de la beta.
            </p>
            <button onClick={onClose} style={primaryBtnStyle}>Cerrar</button>
          </>
        ) : (
          <>
            <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--muted)', margin: '4px 0 18px' }}>
              Cuéntanos qué faltó, qué fue incómodo o qué te gustaría ver. No necesitas iniciar sesión. Si dejas tu email, te guardamos créditos premium para la beta.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <span style={labelStyle}>Tipo de feedback</span>
                <select
                  value={tipo}
                  onChange={e => setTipo(e.target.value as FeedbackType)}
                  style={{ ...inputStyle, cursor: 'pointer' }}
                >
                  {TIPOS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <span style={labelStyle}>Comentario *</span>
                <textarea
                  value={comentario}
                  onChange={e => setComentario(e.target.value)}
                  placeholder="Cuéntanos qué pasó…"
                  rows={4}
                  style={{ ...inputStyle, resize: 'vertical', minHeight: 80 }}
                />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <span style={labelStyle}>Email (opcional)</span>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="tu@email.com"
                  style={inputStyle}
                />
                <span style={{ fontSize: 11.5, color: 'var(--muted)' }}>
                  Déjalo si quieres recibir créditos premium
                </span>
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <span style={labelStyle}>Importancia</span>
                <div style={{ display: 'flex', gap: 8 }}>
                  {IMPORTANCIAS.map(i => (
                    <button
                      key={i.value}
                      type="button"
                      onClick={() => setImportancia(i.value)}
                      style={{
                        flex: 1,
                        background: importancia === i.value ? 'var(--primary)' : 'transparent',
                        color: importancia === i.value ? '#fff' : 'var(--muted)',
                        border: `1px solid ${importancia === i.value ? 'var(--primary)' : 'var(--border)'}`,
                        borderRadius: 8,
                        padding: '8px 0',
                        fontSize: 13,
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      {i.label}
                    </button>
                  ))}
                </div>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, color: 'var(--muted)', cursor: 'pointer' }}>
                <input type="checkbox" checked={consentimiento} onChange={e => setConsentimiento(e.target.checked)} />
                Acepto que me contacten sobre este comentario
              </label>

              {status === 'error' && (
                <div style={{
                  padding: '10px 12px', borderRadius: 8, fontSize: 13,
                  background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--danger)',
                }}>
                  No pudimos enviar el feedback ahora. Intenta de nuevo en unos minutos.
                </div>
              )}

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'space-between' }}>
                <span style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
                  🔒 100% confidencial
                </span>
                <button
                  onClick={handleSubmit}
                  disabled={!comentarioValido || status === 'enviando'}
                  style={{
                    ...primaryBtnStyle,
                    opacity: !comentarioValido || status === 'enviando' ? 0.6 : 1,
                    cursor: !comentarioValido || status === 'enviando' ? 'not-allowed' : 'pointer',
                  }}
                >
                  {status === 'enviando' ? 'Enviando…' : 'Enviar feedback'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
