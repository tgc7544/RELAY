import type { ReactNode } from 'react'

interface ScreenHeroProps {
  title: string
  subtitle?: string
  eyebrow?: ReactNode
  right?: ReactNode
  children?: ReactNode
}

export function ScreenHero({ title, subtitle, eyebrow, right, children }: ScreenHeroProps) {
  return (
    <div className="bg-relay-green-950 px-8 py-10 text-relay-cream md:py-14">
      <div className="mx-auto max-w-7xl">
        {(eyebrow || right) && (
          <div className="mb-4 flex items-center justify-between">
            <div>{eyebrow}</div>
            <div>{right}</div>
          </div>
        )}
        <h1 className="font-display text-3xl font-bold leading-tight md:text-4xl">{title}</h1>
        {subtitle && <p className="mt-2 max-w-xl text-base text-relay-green-100/70">{subtitle}</p>}
        {children}
      </div>
    </div>
  )
}
