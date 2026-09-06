import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Construction, CalendarCheck2 } from 'lucide-react'
import { ActionCard } from '../components/ActionCard'
import { BookingCard } from '../components/BookingCard'
import { ChatDemo } from '../components/ChatDemo'
import { ScreenHero } from '../components/ScreenHero'
import { ScreenBody } from '../components/ScreenBody'
import { supabase } from '../lib/supabase'
import type { Booking } from '../lib/types'
import { timeGreeting, formatDateLong } from '../lib/format'

export function Home() {
  const navigate = useNavigate()
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    supabase
      .from('bookings')
      .select('*, equipment:equipment_id(name)')
      .order('created_at', { ascending: false })
      .limit(2)
      .then(({ data }) => {
        if (!active) return
        setBookings((data as Booking[]) ?? [])
        setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  return (
    <div className="screen-enter flex flex-col">
      <ScreenHero title={`${timeGreeting()}, James.`} subtitle={formatDateLong(new Date())} />

      <ScreenBody>
        <div className="mx-auto flex max-w-7xl flex-col gap-10">
          <div className="flex max-w-2xl gap-4">
            <ActionCard
              icon={Construction}
              label="Book Equipment"
              subtitle="Browse & reserve gear"
              tone="green"
              onClick={() => navigate('/equipment')}
            />
            <ActionCard
              icon={CalendarCheck2}
              label="My Bookings"
              subtitle="Track your jobs"
              tone="green"
              onClick={() => navigate('/bookings')}
            />
          </div>

          <div className="grid gap-10 lg:grid-cols-[1.6fr_1fr]">
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold text-relay-ink">Recent Bookings</h2>
                <button onClick={() => navigate('/bookings')} className="text-xs font-semibold text-relay-green-700">
                  See all
                </button>
              </div>
              {loading ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="h-24 skeleton rounded-2xl" />
                  <div className="h-24 skeleton rounded-2xl" />
                </div>
              ) : bookings.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-black/10 bg-white p-6 text-center">
                  <p className="text-sm text-relay-muted">
                    No bookings yet. Browse equipment to get your first job scheduled.
                  </p>
                  <button
                    onClick={() => navigate('/equipment')}
                    className="mt-3 rounded-full bg-relay-green-700 px-4 py-2 text-xs font-semibold text-relay-cream"
                  >
                    Browse Equipment
                  </button>
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  {bookings.map((b) => (
                    <BookingCard key={b.booking_id} booking={b} />
                  ))}
                </div>
              )}
            </div>

            <div>
              <h2 className="mb-1 font-display text-lg font-semibold text-relay-ink">Book by text</h2>
              <p className="mb-4 text-sm text-relay-muted">
                No app, no hassle — contractors can also book straight from WhatsApp or SMS.
              </p>
              <ChatDemo />
            </div>
          </div>
        </div>
      </ScreenBody>
    </div>
  )
}
