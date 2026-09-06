import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { CheckCircle2, Navigation } from 'lucide-react'
import { supabase } from '../lib/supabase'
import type { Booking } from '../lib/types'
import { formatBBD, formatDateShort } from '../lib/format'
import { Logo } from '../components/Logo'

export function Confirmed() {
  const { bookingId } = useParams()
  const navigate = useNavigate()
  const [booking, setBooking] = useState<Booking | null>(null)

  useEffect(() => {
    if (!bookingId) return
    supabase
      .from('bookings')
      .select('*, equipment:equipment_id(name)')
      .eq('booking_id', bookingId)
      .single()
      .then(({ data }) => setBooking((data as Booking) ?? null))
  }, [bookingId])

  const reference = bookingId ? `REL-${bookingId.slice(0, 8).toUpperCase()}` : ''
  const deposit = booking?.deposit_amount ?? 0
  const paypalUrl = `https://paypal.me/buildwithrelay/${deposit.toFixed(2)}`

  return (
    <div className="screen-enter flex flex-col items-center gap-6 px-6 pb-8 pt-5 text-center">
      <div className="w-full">
        <Logo />
      </div>

      <div className="flex h-20 w-20 animate-[pop_0.4s_ease-out] items-center justify-center rounded-full bg-relay-green-100">
        <CheckCircle2 size={44} className="text-relay-green-600" strokeWidth={1.6} />
      </div>

      <div>
        <h1 className="font-display text-xl font-bold text-relay-ink">Booking Confirmed</h1>
        <p className="mt-1 text-sm text-relay-muted">Reference {reference}</p>
      </div>

      {booking && (
        <div className="w-full space-y-2 rounded-2xl bg-white p-4 text-left shadow-sm shadow-black/5">
          <div className="flex justify-between text-sm">
            <span className="text-relay-muted">Equipment</span>
            <span className="font-semibold text-relay-ink">{booking.equipment?.name ?? '—'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-relay-muted">Dates</span>
            <span className="font-semibold text-relay-ink">
              {formatDateShort(booking.start_date)} – {formatDateShort(booking.end_date)}
            </span>
          </div>
          <div className="flex justify-between border-t border-black/5 pt-2 text-sm">
            <span className="text-relay-muted">Deposit due</span>
            <span className="font-semibold text-relay-ink">{formatBBD(deposit)}</span>
          </div>
        </div>
      )}

      <a
        href={paypalUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="w-full rounded-2xl bg-relay-orange-500 py-4 text-center font-display text-base font-semibold text-relay-cream transition-transform active:scale-[0.98]"
      >
        Pay Deposit — {formatBBD(deposit)}
      </a>

      {bookingId && (
        <button
          onClick={() => navigate(`/track/${bookingId}`)}
          className="flex w-full items-center justify-center gap-2 rounded-2xl border border-relay-green-700/20 bg-relay-green-50 py-3.5 font-display text-sm font-semibold text-relay-green-700 transition-transform active:scale-[0.98]"
        >
          <Navigation size={16} /> Track Delivery
        </button>
      )}

      <p className="text-xs leading-relaxed text-relay-muted">
        Your equipment owner has been notified. Expect confirmation within 1 hour.
      </p>

      <button onClick={() => navigate('/')} className="text-sm font-semibold text-relay-green-700">
        Return to Home
      </button>
    </div>
  )
}
