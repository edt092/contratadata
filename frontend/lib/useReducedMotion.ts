'use client'

import { useEffect, useState } from 'react'

/** `prefers-reduced-motion`. Necesario en JS además de la regla CSS global
 * en globals.css porque las animaciones SMIL de SVG (<animate>) no
 * respetan esa media query — hay que omitir los nodos <animate> a mano. */
export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false)

  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    // `matchMedia` no existe en el servidor, así que el valor inicial real
    // solo puede leerse tras montar en cliente — no hay forma de evitar
    // este setState síncrono sin arriesgar un mismatch de hidratación.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setReduced(query.matches)
    const onChange = () => setReduced(query.matches)
    query.addEventListener('change', onChange)
    return () => query.removeEventListener('change', onChange)
  }, [])

  return reduced
}
