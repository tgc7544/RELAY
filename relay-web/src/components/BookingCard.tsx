import { useNavigate } from 'react-router-dom'
import { MapPin, CalendarRange, Navigation, ChevronRight } from 'lucide-react'
import type { Booking } from '../lib/types'
import { formatDateShort } from '../lib/format'
import { StatusBadge } from './StatusBadge'

export function BookingCard({ booking }: { booking: Booking }) {
  const navigate = useNavigate()
  const equipmentName = booking.equipment?.name ?? 'Equipment'

  return (
    <div
      onClick={() => navigate(`/track/${booking.booking_id}`)}
      className="cursor-pointer rounded-2xl bg-white p-4 shadow-sm shadow-black/5 transition-transform active:scale-[0.98]"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-display text-[15px] font-semibold text-relay-ink">{equipmentName}</h3>
        <StatusBadge status={booking.status} />
      </div>
      <p className="mt-1.5 flex items-center gap-1.5 text-xs text-relay-muted">
        <CalendarRange size={13} />
        {formatDateShort(booking.start_date)} – {formatDateShort(booking.end_date)}
      </p>
      {booking.delivery_location && (
        <p className="mt-1 flex items-center gap-1.5 text-xs text-relay-muted">
          <MapPin size={13} /> {booking.delivery_location}
        </p>
      )}
      {booking.status !== 'completed' && (
        <div className="mt-3 flex items-center justify-between border-t border-black/5 pt-3 text-xs font-semibold text-relay-green-700">
          <span className="flex items-center gap-1.5">
            <Navigation size={13} /> Track delivery
          </span>
          <ChevronRight size={14} />
        </div>
      )}
    </div>
  )
}
