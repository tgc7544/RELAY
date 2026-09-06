import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ChevronLeft, MapPin, CheckCircle2 } from 'lucide-react'
import { supabase } from '../lib/supabase'
import type { Booking } from '../lib/types'
import { photoForType } from '../lib/equipment'
import { formatDateShort } from '../lib/format'

interface TrackedBooking extends Booking {
  equipment?: { name: string; type: string } | null
}

const STAGES = [
  { title: 'Booking Requested', detail: 'Your request was sent to the equipment owner.' },
  { title: 'Owner Confirmed', detail: 'The owner has locked in your dates.' },
  { title: 'Out for Delivery', detail: 'Equipment is en route to your site.' },
  { title: 'Delivered on Site', detail: 'Ready to work — enjoy the job.' },
]

function completedCount(status: string): number {
  if (status === 'completed') return 4
  if (status === 'confirmed') return 2
  return 1
}

export function TrackDelivery() {
  const { bookingId } = useParams()
  const navigate = useNavigate()
  const [booking, setBooking] = useState<TrackedBooking | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!bookingId) return
    supabase
      .from('bookings')
      .select('*, equipment:equipment_id(name, type)')
      .eq('booking_id', bookingId)
      .single()
      .then(({ data }) => {
        setBooking((data as TrackedBooking) ?? null)
        setLoading(false)
      })
  }, [bookingId])

  const done = booking ? completedCount(booking.status) : 0

  return (
    <div className="screen-enter mx-auto flex max-w-2xl flex-col gap-5 px-8 py-10">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm font-medium text-relay-muted hover:text-relay-ink"
      >
        <ChevronLeft size={18} /> Back
      </button>

      {loading ? (
        <div className="h-64 skeleton rounded-2xl" />
      ) : !booking ? (
        <p className="text-sm text-relay-muted">Booking not found.</p>
      ) : (
        <>
          <div>
            <h1 className="font-display text-xl font-bold text-relay-ink">Track Delivery</h1>
            <p className="mt-0.5 text-sm text-relay-muted">
              {booking.equipment?.name ?? 'Equipment'} · {formatDateShort(booking.start_date)} –{' '}
              {formatDateShort(booking.end_date)}
            </p>
          </div>

          <div className="flex gap-3 rounded-2xl bg-white p-3 shadow-sm shadow-black/5">
            <img
              src={photoForType(booking.equipment?.type ?? 'excavator')}
              alt={booking.equipment?.name ?? 'Equipment'}
              className="h-16 w-16 shrink-0 rounded-xl object-cover"
            />
            <div className="flex flex-col justify-center">
              <p className="font-display text-sm font-semibold text-relay-ink">{booking.equipment?.name ?? 'Equipment'}</p>
              {booking.delivery_location && (
                <p className="mt-0.5 flex items-center gap-1 text-xs text-relay-muted">
                  <MapPin size={12} /> {booking.delivery_location}
                </p>
              )}
            </div>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-sm shadow-black/5">
            {STAGES.map((stage, i) => {
              const state = i < done ? 'done' : i === done && done < 4 ? 'current' : 'upcoming'
              const isLast = i === STAGES.length - 1
              return (
                <div key={stage.title} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <span
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                        state === 'done'
                          ? 'bg-relay-green-700 text-relay-cream'
                          : state === 'current'
                            ? 'bg-relay-green-100 text-relay-green-700 ring-2 ring-relay-green-700'
                            : 'bg-black/5 text-relay-muted'
                      }`}
                    >
                      {state === 'done' ? (
                        <CheckCircle2 size={18} />
                      ) : (
                        <span className="h-2 w-2 rounded-full bg-current" />
                      )}
                    </span>
                    {!isLast && (
                      <span className={`w-0.5 flex-1 ${i < done - 1 ? 'bg-relay-green-700' : 'bg-black/10'}`} />
                    )}
                  </div>
                  <div className={`pb-6 ${isLast ? 'pb-0' : ''}`}>
                    <p
                      className={`font-display text-sm font-semibold ${
                        state === 'upcoming' ? 'text-relay-muted' : 'text-relay-ink'
                      }`}
                    >
                      {stage.title}
                    </p>
                    <p className="mt-0.5 text-xs text-relay-muted">{stage.detail}</p>
                  </div>
                </div>
              )
            })}
          </div>

          {done < 4 && (
            <div className="rounded-2xl bg-relay-green-50 p-4 text-center text-sm text-relay-green-800">
              {done < 2
                ? "We'll notify you the moment your owner confirms delivery."
                : 'Arriving within the scheduled window — no action needed from you.'}
            </div>
          )}
        </>
      )}
    </div>
  )
}
