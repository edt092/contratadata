export interface Contract {
  id: string
  entidad: string
  sigla: string
  contratista: string
  valor: number
  fecha: string
  estado: 'Activo' | 'Liquidado' | 'Terminado' | 'Suspendido'
  fuente: 'SECOP' | 'datos.gov.co'
  mIdx: number
}

export interface Entity {
  n: string
  s: string
}

export interface BarItem {
  name: string
  valorFmt: string
  pct: number
  open?: () => void
}

export interface DonutSlice {
  estado: string
  count: number
  pct: number
  color: string
  dash: string
  offset: string
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
