import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookingCard } from '../components/BookingCard'
import { ScreenHero } from '../components/ScreenHero'
import { ScreenBody } from '../components/ScreenBody'
import { supabase } from '../lib/supabase'
import type { Booking } from '../lib/types'

export function BookingsList() {
  const navigate = useNavigate()
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase
      .from('bookings')
      .select('*, equipment:equipment_id(name)')
      .order('created_at', { ascending: false })
      .then(({ data }) => {
        setBookings((data as Booking[]) ?? [])
        setLoading(false)
      })
  }, [])

  return (
    <div className="flex flex-col screen-enter">
      <ScreenHero title="My Bookings" subtitle="Every job you've scheduled, in one place" />

      <ScreenBody>
        {loading ? (
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-24 skeleton rounded-2xl" />
            ))}
          </div>
        ) : bookings.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-black/10 bg-white p-6 text-center">
            <p className="text-sm text-relay-muted">No bookings yet.</p>
            <button
              onClick={() => navigate('/equipment')}
              className="mt-3 rounded-full bg-relay-green-700 px-4 py-2 text-xs font-semibold text-relay-cream"
            >
              Browse Equipment
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {bookings.map((b) => (
              <BookingCard key={b.booking_id} booking={b} />
            ))}
          </div>
        )}
      </ScreenBody>
    </div>
  )
}
