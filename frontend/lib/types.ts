export interface DonutSlice {
  estado: string
  count: number
  pct: number
  color: string
  dash: string
  offset: string
}

/** Contrato de trazabilidad de datos — ver docs/frontend-architecture.md.
 * No todos los endpoints actuales de FastAPI devuelven esta forma todavía;
 * se usa donde hay evidencia suficiente (fuente + fecha reales), nunca con
 * valores inventados. */
export interface DataQuality {
  updated_at: string
  freshness_seconds: number
  status: 'verified' | 'delayed' | 'unknown'
}

export interface DataCitation {
  source_name: string
  source_url: string
  dataset_id?: string
  retrieved_at: string
  content_hash?: string
}

export interface TableRow {
  id: string
  fecha: string
  entidad: string
  contratista: string
  valorFmt: string
  estado: string
  estadoFg: string
  estadoBg: string
  fuente: string
  fuenteFg: string
  fuenteBg: string
  openEnt?: () => void
  openCon?: () => void
}
