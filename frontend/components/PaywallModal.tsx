'use client'

import type { FeatureKey } from '@/lib/api'
import ProUpgradeCard from './ProUpgradeCard'

interface PaywallModalProps {
  feature?: FeatureKey
  onClose: () => void
}

export default function PaywallModal({ feature, onClose }: PaywallModalProps) {
  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 200,
        background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(3px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
      }}
    >
      <div onClick={e => e.stopPropagation()} className="animate-fade" style={{ width: '100%', maxWidth: 440, position: 'relative' }}>
        <button
          onClick={onClose}
          aria-label="Cerrar"
          style={{
            position: 'absolute', top: -12, right: -12, zIndex: 1,
            background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '50%',
            width: 28, height: 28, cursor: 'pointer', color: 'var(--muted)', fontSize: 14,
          }}
        >
          ✕
        </button>
        <ProUpgradeCard feature={feature} />
      </div>
    </div>
  )
}
