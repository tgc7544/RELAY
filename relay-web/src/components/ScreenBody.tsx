import type { ReactNode } from 'react'

export function ScreenBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`relative z-10 -mt-6 rounded-t-[32px] bg-relay-sand px-8 pb-16 pt-10 ${className}`}>{children}</div>
}
