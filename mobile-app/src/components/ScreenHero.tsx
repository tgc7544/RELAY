import type { ReactNode } from 'react'
import { Logo } from './Logo'

interface ScreenHeroProps {
  title: string
  subtitle?: string
  left?: ReactNode
  right?: ReactNode
  children?: ReactNode
}

export function ScreenHero({ title, subtitle, left, right, children }: ScreenHeroProps) {
  return (
    <div className="bg-relay-green-950 px-5 pb-9 pt-5 text-relay-cream">
      <div className="flex items-center justify-between">
        {left ?? <Logo dark />}
        {right}
      </div>
      <div className="mt-6">
        <h1 className="font-display text-[26px] font-bold leading-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-relay-green-100/70">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}
