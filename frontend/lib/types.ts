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
