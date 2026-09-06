const STYLES: Record<string, string> = {
  confirmed: 'bg-relay-green-100 text-relay-green-700',
  pending: 'bg-relay-amber-100 text-relay-amber-600',
  completed: 'bg-black/5 text-relay-muted',
  available: 'bg-relay-green-100 text-relay-green-700',
  unavailable: 'bg-black/5 text-relay-muted',
  booked: 'bg-relay-amber-100 text-relay-amber-600',
}

export function StatusBadge({ status }: { status: string }) {
  const key = status.toLowerCase()
  return (
    <span
      className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${
        STYLES[key] ?? 'bg-black/5 text-relay-muted'
      }`}
    >
      {status}
    </span>
  )
}
