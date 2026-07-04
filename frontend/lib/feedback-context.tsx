'use client'

import { createContext, useContext, useState, type ReactNode } from 'react'
import FeedbackModal from '@/components/FeedbackModal'

interface FeedbackContextValue {
  openFeedback: () => void
}

const FeedbackContext = createContext<FeedbackContextValue>({ openFeedback: () => {} })

export function FeedbackProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <FeedbackContext.Provider value={{ openFeedback: () => setOpen(true) }}>
      {children}
      <FeedbackModal open={open} onClose={() => setOpen(false)} />
    </FeedbackContext.Provider>
  )
}

export const useFeedback = () => useContext(FeedbackContext)
