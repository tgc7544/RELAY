import type { ReactNode } from 'react'

export function ScreenBody({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`relative z-10 -mt-5 flex flex-1 flex-col gap-5 rounded-t-[28px] bg-relay-sand px-5 pb-8 pt-6 ${className}`}>
      {children}
    </div>
  )
}
