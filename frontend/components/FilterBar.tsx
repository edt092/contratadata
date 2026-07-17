'use client'

interface FilterBarProps {
  entidadOptions: string[]
  estadoOptions: string[]
  dEntidad: string
  dContratista: string
  dEstado: string
  dDesde: string
  dHasta: string
  onEntidad: (v: string) => void
  onContratista: (v: string) => void
  onEstado: (v: string) => void
  onDesde: (v: string) => void
  onHasta: (v: string) => void
  onApply: () => void
  onClear: () => void
}

const inputStyle: React.CSSProperties = {
  background: 'var(--surface2)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '9px 11px',
  fontSize: 13.5,
  color: 'var(--text)',
  outline: 'none',
  width: '100%',
}

const labelStyle: React.CSSProperties = {
  fontSize: 10.5,
  fontWeight: 600,
  letterSpacing: '0.07em',
  textTransform: 'uppercase',
  color: 'var(--muted)',
}

export default function FilterBar({
  entidadOptions, estadoOptions,
  dEntidad, dContratista, dEstado, dDesde, dHasta,
  onEntidad, onContratista, onEstado, onDesde, onHasta,
  onApply, onClear,
}: FilterBarProps) {
  return (
    <div style={{
      position: 'sticky',
      top: 60,
      zIndex: 40,
      background: 'color-mix(in srgb, var(--bg) 90%, transparent)',
      backdropFilter: 'blur(8px)',
      padding: '14px 0',
      marginBottom: 8,
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: 10,
        flexWrap: 'wrap',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)',
        padding: 14,
      }}>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 5, flex: 1, minWidth: 190 }}>
          <span style={labelStyle}>Entidad</span>
          <select value={dEntidad} onChange={e => onEntidad(e.target.value)} style={{ ...inputStyle, cursor: 'pointer' }}>
            {entidadOptions.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </label>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 5, flex: 1, minWidth: 170 }}>
          <span style={labelStyle}>Contratista</span>
          <input
            value={dContratista}
            onChange={e => onContratista(e.target.value)}
            placeholder="Buscar nombre…"
            style={inputStyle}
          />
        </label>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 5, minWidth: 140 }}>
          <span style={labelStyle}>Desde</span>
          <input
            type="date"
            value={dDesde}
            onChange={e => onDesde(e.target.value)}
            style={{ ...inputStyle, fontFamily: 'var(--font-mono)', fontSize: 13 }}
          />
        </label>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 5, minWidth: 140 }}>
          <span style={labelStyle}>Hasta</span>
          <input
            type="date"
            value={dHasta}
            onChange={e => onHasta(e.target.value)}
            style={{ ...inputStyle, fontFamily: 'var(--font-mono)', fontSize: 13 }}
          />
        </label>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 5, minWidth: 150 }}>
          <span style={labelStyle}>Estado</span>
          <select value={dEstado} onChange={e => onEstado(e.target.value)} style={{ ...inputStyle, cursor: 'pointer' }}>
            {estadoOptions.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        </label>

        <button
          onClick={onApply}
          style={{
            background: 'var(--primary)',
            color: 'var(--on-primary)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 18px',
            fontSize: 13.5,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Aplicar filtros
        </button>

        <button
          onClick={onClear}
          style={{
            background: 'transparent',
            color: 'var(--muted)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 14px',
            fontSize: 13.5,
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Limpiar
        </button>
      </div>
    </div>
  )
}
