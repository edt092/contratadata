import { fuenteStyle } from '@/lib/format'

export default function FuenteBadge({ fuente }: { fuente: string }) {
  const { fg, bg } = fuenteStyle(fuente)
  return (
    <span style={{
      display: 'inline-block',
      padding: '3px 9px',
      borderRadius: 6,
      fontSize: 11.5,
      fontWeight: 600,
      fontFamily: 'var(--font-mono)',
      color: fg,
      background: bg,
      whiteSpace: 'nowrap',
    }}>
      {fuente}
    </span>
  )
}
