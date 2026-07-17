'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useMe } from '@/lib/useMe'
import { useFeatureGate } from '@/lib/useFeatureGate'
import PaywallModal from './PaywallModal'

interface FollowCompetitorButtonProps {
  supplierName: string
}

export default function FollowCompetitorButton({ supplierName }: FollowCompetitorButtonProps) {
  const { isLoggedIn, clerkUser } = useMe()
  const { getToken } = useAuth()
  const { attempt, showPaywall, closePaywall, feature } = useFeatureGate('competitor_monitor')
  const queryClient = useQueryClient()
  const [busy, setBusy] = useState(false)

  const listQ = useQuery({
    queryKey: ['my-competitors', clerkUser?.id],
    queryFn: () => api.listCompetitors(getToken),
    enabled: isLoggedIn,
    retry: false,
  })

  const existing = listQ.data?.find(c => c.supplier_name === supplierName)

  const follow = async () => {
    setBusy(true)
    try {
      await api.followCompetitor(getToken, { supplier_name: supplierName })
      queryClient.invalidateQueries({ queryKey: ['my-competitors', clerkUser?.id] })
    } finally {
      setBusy(false)
    }
  }

  const unfollow = async () => {
    if (!existing) return
    setBusy(true)
    try {
      await api.unfollowCompetitor(getToken, existing.id)
      queryClient.invalidateQueries({ queryKey: ['my-competitors', clerkUser?.id] })
    } finally {
      setBusy(false)
    }
  }

  const handleClick = () => {
    if (existing) {
      unfollow()
      return
    }
    attempt(follow)
  }

  return (
    <>
      <button
        onClick={handleClick}
        disabled={busy}
        style={{
          background: existing ? 'rgba(16,185,129,0.15)' : 'var(--surface2)',
          color: existing ? 'var(--success)' : 'var(--text)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '9px 14px',
          fontSize: 13,
          fontWeight: 600,
          cursor: busy ? 'wait' : 'pointer',
          opacity: busy ? 0.7 : 1,
        }}
      >
        {existing ? '✓ Siguiendo competidor' : '+ Seguir competidor'}
      </button>

      {showPaywall && <PaywallModal feature={feature} onClose={closePaywall} />}
    </>
  )
}
