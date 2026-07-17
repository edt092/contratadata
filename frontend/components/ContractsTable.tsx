'use client'

import type { TableRow } from '@/lib/types'
import EstadoBadge from './EstadoBadge'
import FuenteBadge from './FuenteBadge'

interface ContractsTableProps {
  rows: TableRow[]
  pageInfo: string
  currentPage: number
  totalPages: number
  isEmpty: boolean
  onPrev: () => void
  onNext: () => void
  onExport: () => void
  onClearFilters: () => void
}

const thStyle: React.CSSProperties = {
  padding: '11px 16px',
  fontSize: 10.5,
  fontWeight: 600,
  letterSpacing: '0.07em',
  textTransform: 'uppercase',
  color: 'var(--muted)',
  fontFamily: 'var(--font-mono)',
  borderBottom: '1px solid var(--border)',
  textAlign: 'left',
  whiteSpace: 'nowrap',
}

export default function ContractsTable({
  rows, pageInfo, currentPage, totalPages, isEmpty,
  onPrev, onNext, onExport, onClearFilters,
}: ContractsTableProps) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-sm)',
      overflow: 'hidden',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 18px',
        borderBottom: '1px solid var(--border)',
      }}>
        <span style={{ fontSize: 13, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
          {pageInfo}
        </span>
        <button
          onClick={onExport}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 7,
            background: 'var(--surface2)',
            color: 'var(--text)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding: '7px 13px',
            fontSize: 12.5,
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          ↓ Exportar CSV
        </button>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13.5 }}>
          <thead>
            <tr>
              <th style={thStyle}>Fecha</th>
              <th style={thStyle}>Entidad</th>
              <th style={thStyle}>Contratista</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Valor</th>
              <th style={thStyle}>Estado</th>
              <th style={thStyle}>Fuente</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} className="row-hover" style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '13px 16px', fontFamily: 'var(--font-mono)', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                  {r.fecha}
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <button className="btn-link-ent" onClick={r.openEnt}>
                    {r.entidad}
                  </button>
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <button className="btn-link-con" onClick={r.openCon}>
                    {r.contratista}
                  </button>
                </td>
                <td style={{
                  padding: '13px 16px',
                  textAlign: 'right',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 600,
                  color: 'var(--text)',
                  whiteSpace: 'nowrap',
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  {r.valorFmt}
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <EstadoBadge estado={r.estado} />
                </td>
                <td style={{ padding: '13px 16px' }}>
                  <FuenteBadge fuente={r.fuente} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isEmpty && (
        <div style={{ padding: '56px 20px', textAlign: 'center' }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)', marginBottom: 6 }}>
            Sin resultados para estos filtros
          </div>
          <div style={{ fontSize: 13.5, color: 'var(--muted)', marginBottom: 16 }}>
            Prueba ampliar el rango de fechas o limpiar los filtros activos.
          </div>
          <button
            onClick={onClearFilters}
            style={{
              background: 'var(--surface2)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '9px 16px',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Limpiar filtros
          </button>
        </div>
      )}

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '13px 18px',
        borderTop: '1px solid var(--border)',
      }}>
        <span style={{ fontSize: 12.5, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
          Página {currentPage} de {totalPages}
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={onPrev}
            disabled={currentPage <= 1}
            style={{
              background: 'var(--surface2)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '7px 14px',
              fontSize: 13,
              fontWeight: 600,
              cursor: currentPage <= 1 ? 'default' : 'pointer',
              opacity: currentPage <= 1 ? 0.4 : 1,
            }}
          >
            ← Anterior
          </button>
          <button
            onClick={onNext}
            disabled={currentPage >= totalPages}
            style={{
              background: 'var(--surface2)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '7px 14px',
              fontSize: 13,
              fontWeight: 600,
              cursor: currentPage >= totalPages ? 'default' : 'pointer',
              opacity: currentPage >= totalPages ? 0.4 : 1,
            }}
          >
            Siguiente →
          </button>
        </div>
      </div>
    </div>
  )
}
