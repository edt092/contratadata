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
      borderRadius: 12,
      padding: '18px 18px 16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <span style={{ width: 9, height: 9, borderRadius: 2, background: accentColor, flexShrink: 0 }} />
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
        fontSize: 38,
        fontWeight: 800,
        letterSpacing: '-0.03em',
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
