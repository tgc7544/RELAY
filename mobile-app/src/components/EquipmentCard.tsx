import { MapPin } from 'lucide-react'
import type { Equipment } from '../lib/types'
import { typeLabel, parishFor, photoForType } from '../lib/equipment'
import { formatBBD } from '../lib/format'
import { StatusBadge } from './StatusBadge'

interface EquipmentCardProps {
  equipment: Equipment
  available: boolean
  onSelect: () => void
}

export function EquipmentCard({ equipment, available, onSelect }: EquipmentCardProps) {
  return (
    <div
      onClick={onSelect}
      className="flex w-full cursor-pointer gap-3 rounded-2xl bg-white p-3 shadow-sm shadow-black/5 transition-transform active:scale-[0.98]"
    >
      <img
        src={photoForType(equipment.type)}
        alt={equipment.name}
        loading="lazy"
        className="h-20 w-20 shrink-0 rounded-xl object-cover"
      />
      <div className="flex flex-1 flex-col justify-between py-0.5">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-display text-[15px] font-semibold leading-tight text-relay-ink">{equipment.name}</h3>
            <StatusBadge status={available ? 'available' : 'booked'} />
          </div>
          <p className="mt-0.5 text-xs text-relay-muted">
            {typeLabel(equipment.type)} · {typeLabel(equipment.size_category)}
          </p>
          <p className="mt-1 flex items-center gap-1 text-xs text-relay-muted">
            <MapPin size={12} /> {parishFor(equipment.id)}
          </p>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <span className="font-display text-[15px] font-bold text-relay-ink">
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
