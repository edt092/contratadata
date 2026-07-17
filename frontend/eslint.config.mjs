import nextConfig from 'eslint-config-next'

// eslint-config-next 16 ya exporta un flat config nativo (incluye
// core-web-vitals + reglas de TypeScript) — no se necesita FlatCompat.
const eslintConfig = [
  ...nextConfig,
  { ignores: ['node_modules/**'] },
]

export default eslintConfig
