import type { DataCitation } from '@/lib/types'
import { cn } from '@/lib/utils'

interface VerifiedCitationProps {
  citation: DataCitation
  className?: string
}

function fmtFecha(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return iso
  }
}

/** Cita verificable: fuente + fecha de recuperación + enlace al dato
 * original. Solo debe usarse con datos reales — nunca con hashes o fechas
 * inventadas (ver docs/frontend-architecture.md). */
export default function VerifiedCitation({ citation, className }: VerifiedCitationProps) {
  return (
    <a
      href={citation.source_url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn('inline-flex items-center gap-2 text-[12px] transition-colors', className)}
      style={{ color: 'var(--brand-text-muted)', fontFamily: 'var(--font-mono)' }}
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path
          d="M9 12l2 2 4-4M12 21a9 9 0 100-18 9 9 0 000 18z"
          stroke="var(--brand-verified)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span>
        {citation.source_name} · verificado {fmtFecha(citation.retrieved_at)}
      </span>
    </a>
  )
}
