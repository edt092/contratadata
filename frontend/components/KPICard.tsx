interface KPICardProps {
  label: string
  value: string
  sub?: string
  subColor?: string
  accentColor: string
}

export default function KPICard({ label, value, sub, subColor, accentColor }: KPICardProps) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-sm)',
      padding: '20px 20px 18px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: accentColor, flexShrink: 0 }} />
        <span style={{
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--muted)',
          fontFamily: 'var(--font-mono)',
        }}>
          {label}
        </span>
      </div>
      <div style={{
        fontSize: 34,
        fontWeight: 700,
        letterSpacing: '-0.02em',
        lineHeight: 1,
        color: 'var(--text)',
        fontVariantNumeric: 'tabular-nums',
      }}>
        {value}
      </div>
      {sub && (
        <div style={{
          marginTop: 12,
          fontSize: 12.5,
          color: subColor ?? 'var(--muted)',
          fontWeight: subColor ? 600 : 500,
          fontFamily: subColor ? undefined : 'var(--font-mono)',
        }}>
          {sub}
        </div>
      )}
    </div>
  )
}
