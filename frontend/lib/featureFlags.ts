// Funcionalidades premium (alertas guardadas, monitor de competidores,
// reportes, plan Pro) — reactivadas con cobros reales vía Wompi (ver
// auth.md y src/api/routers/premium.py::create_checkout). Un solo flag
// controla si se montan en la UI; ponerlo en `false` las oculta todas de
// nuevo sin tocar el resto del código.
export const PREMIUM_ENABLED = true
