import { estadoStyle } from '@/lib/format'

export default function EstadoBadge({ estado }: { estado: string }) {
  const { fg, bg } = estadoStyle(estado)
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      padding: '3px 9px',
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 600,
      color: fg,
      background: bg,
      whiteSpace: 'nowrap',
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: fg, display: 'block' }} />
      {estado}
    </span>
  )
}
