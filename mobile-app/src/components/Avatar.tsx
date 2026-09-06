export function Avatar({
  initials = 'JC',
  size = 40,
  tone = 'light',
}: {
  initials?: string
  size?: number
  tone?: 'light' | 'dark'
}) {
  const toneClasses =
    tone === 'dark'
      ? 'bg-white/15 text-relay-cream ring-1 ring-white/25'
      : 'bg-relay-green-800 text-relay-cream'
  return (
    <div
      className={`flex shrink-0 items-center justify-center rounded-full font-display font-semibold ${toneClasses}`}
      style={{ width: size, height: size, fontSize: size * 0.38 }}
    >
      {initials}
    </div>
  )
}
