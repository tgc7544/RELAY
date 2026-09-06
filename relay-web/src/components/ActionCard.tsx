import type { LucideIcon } from 'lucide-react'

interface ActionCardProps {
  icon: LucideIcon
  label: string
  subtitle: string
  tone: 'green' | 'orange'
  onClick: () => void
}

const TONE_STYLES = {
  green: 'bg-relay-green-800',
  orange: 'bg-relay-orange-500',
}

export function ActionCard({ icon: Icon, label, subtitle, tone, onClick }: ActionCardProps) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-1 flex-col items-start gap-8 rounded-[22px] ${TONE_STYLES[tone]} p-5 text-left shadow-lg shadow-black/10 transition-transform active:scale-[0.97]`}
    >
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/15 text-relay-cream">
        <Icon size={24} strokeWidth={1.8} />
      </span>
      <span>
        <span className="block font-display text-[17px] font-bold leading-tight text-relay-cream">{label}</span>
        <span className="mt-1 block text-xs font-medium text-white/70">{subtitle}</span>
      </span>
    </button>
  )
}
