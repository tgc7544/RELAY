import { MapPin } from 'lucide-react'
import type { Equipment } from '../lib/types'
import { typeLabel, parishFor, photoForType } from '../lib/equipment'
import { formatBBD } from '../lib/format'
import { StatusBadge } from './StatusBadge'

interface EquipmentGridCardProps {
  equipment: Equipment
  available: boolean
  onSelect: () => void
}

export function EquipmentGridCard({ equipment, available, onSelect }: EquipmentGridCardProps) {
  return (
    <div
      onClick={onSelect}
      className="group cursor-pointer overflow-hidden rounded-2xl bg-white shadow-sm shadow-black/5 transition-all hover:-translate-y-1 hover:shadow-lg"
    >
      <div className="relative h-44 w-full overflow-hidden">
        <img
          src={photoForType(equipment.type)}
          alt={equipment.name}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute right-3 top-3">
          <StatusBadge status={available ? 'available' : 'booked'} />
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-display text-base font-semibold leading-tight text-relay-ink">{equipment.name}</h3>
        <p className="mt-0.5 text-xs text-relay-muted">
          {typeLabel(equipment.type)} · {typeLabel(equipment.size_category)}
        </p>
        <p className="mt-1 flex items-center gap-1 text-xs text-relay-muted">
          <MapPin size={12} /> {parishFor(equipment.id)}
        </p>
        <div className="mt-3 flex items-center justify-between">
          <span className="font-display text-base font-bold text-relay-ink">
            {formatBBD(equipment.daily_rate)}
            <span className="text-xs font-medium text-relay-muted"> /day</span>
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onSelect()
            }}
            className="rounded-full bg-relay-green-700 px-4 py-1.5 text-xs font-semibold text-relay-cream transition-transform active:scale-95"
          >
            Book
          </button>
        </div>
      </div>
    </div>
  )
}
