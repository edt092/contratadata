export const fmtInt = (n: number) =>
  new Intl.NumberFormat('es-CO').format(Math.round(n))

export const fmtCOP = (n: number) =>
  '$' + new Intl.NumberFormat('es-CO').format(Math.round(n))

export const fmtAbbr = (v: number): string => {
  if (v >= 1e12) return '$' + (v / 1e12).toFixed(2) + ' B'
  if (v >= 1e9) return '$' + fmtInt(v / 1e9) + ' MM'
  if (v >= 1e6) return '$' + fmtInt(v / 1e6) + ' M'
  return '$' + fmtInt(v)
}

export const hexA = (h: string, a: number): string => {
  const n = parseInt(h.slice(1), 16)
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`
}

export const estadoStyle = (e: string | null | undefined) => {
  const map: Record<string, string> = {
    Activo: '#10B981',
    Liquidado: '#94A3B8',
    Terminado: '#6366F1',
    Suspendido: '#F59E0B',
  }
  const c = map[e ?? ''] ?? '#94A3B8'
  return { fg: c, bg: hexA(c, 0.15) }
}

export const fuenteStyle = (f: string) => {
  const c = f === 'SECOP' ? '#3B82F6' : '#8B5CF6'
  return { fg: c, bg: hexA(c, 0.15) }
}
