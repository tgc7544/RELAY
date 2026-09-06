import { useNavigate } from 'react-router-dom'
import { ChevronLeft, Plus } from 'lucide-react'
import { StatusBadge } from '../components/StatusBadge'
import { ScreenHero } from '../components/ScreenHero'
import { ScreenBody } from '../components/ScreenBody'
import { formatBBD } from '../lib/format'
import { useToast } from '../lib/toast'

const MOCK_EQUIPMENT = [
  { name: 'Mini Excavator 2T', status: 'Booked', rate: 180 },
  { name: 'Tandem-Axle Dump Truck', status: 'Available', rate: 400 },
  { name: 'Generator 60kVA', status: 'Available', rate: 260 },
  { name: 'Boom Lift 45ft', status: 'Booked', rate: 280 },
]

const MOCK_BOOKINGS = [
  { contractor: 'Andre Forde', equipment: 'Mini Excavator 2T', dates: 'Sep 2 – Sep 5', total: 540 },
  { contractor: 'Kerry-Ann Straker', equipment: 'Boom Lift 45ft', dates: 'Sep 4 – Sep 6', total: 560 },
]

export function Owner() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const monthRevenue = 6420

  return (
    <div className="screen-enter flex flex-col">
      <ScreenHero
        title="Owner Dashboard"
        subtitle="Your listings, bookings & payouts"
        eyebrow={
          <button
            onClick={() => navigate('/profile')}
            className="flex items-center gap-1 text-sm font-medium text-relay-cream/70 hover:text-relay-cream"
          >
            <ChevronLeft size={16} /> Back to Profile
          </button>
        }
      >
        <div className="mt-6 grid max-w-lg grid-cols-3 gap-3">
          <div className="rounded-2xl bg-white/10 p-4 text-center">
            <p className="font-display text-2xl font-bold text-relay-cream">{MOCK_EQUIPMENT.length}</p>
            <p className="text-xs text-relay-green-100/70">Listings</p>
          </div>
          <div className="rounded-2xl bg-white/10 p-4 text-center">
            <p className="font-display text-2xl font-bold text-relay-cream">{MOCK_BOOKINGS.length}</p>
            <p className="text-xs text-relay-green-100/70">Active Bookings</p>
          </div>
          <div className="rounded-2xl bg-white/10 p-4 text-center">
            <p className="font-display text-lg font-bold text-relay-cream">{formatBBD(monthRevenue)}</p>
            <p className="text-xs text-relay-green-100/70">This Month</p>
          </div>
        </div>
      </ScreenHero>

      <ScreenBody>
        <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h2 className="mb-3 font-display text-base font-semibold text-relay-ink">My Equipment</h2>
            <div className="space-y-2">
              {MOCK_EQUIPMENT.map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between rounded-2xl bg-white p-3.5 shadow-sm shadow-black/5"
                >
                  <div>
                    <p className="text-sm font-semibold text-relay-ink">{item.name}</p>
                    <p className="text-xs text-relay-muted">{formatBBD(item.rate)} / day</p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="mb-3 font-display text-base font-semibold text-relay-ink">Upcoming Bookings</h2>
            <div className="space-y-2">
              {MOCK_BOOKINGS.map((b) => (
                <div key={b.contractor} className="rounded-2xl bg-white p-3.5 shadow-sm shadow-black/5">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-relay-ink">{b.contractor}</p>
                    <p className="text-sm font-bold text-relay-green-700">{formatBBD(b.total * 0.85)}</p>
                  </div>
                  <p className="mt-0.5 text-xs text-relay-muted">
                    {b.equipment} · {b.dates}
                  </p>
                  <p className="text-[11px] text-relay-muted">Payout after 15% Relay fee</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={() => showToast('Add Equipment flow is coming soon')}
          className="flex w-fit items-center justify-center gap-2 rounded-2xl bg-relay-green-700 px-6 py-3.5 font-display text-sm font-semibold text-relay-cream shadow-lg shadow-black/10 transition-transform active:scale-[0.98]"
        >
          <Plus size={18} /> Add Equipment
        </button>
        </div>
      </ScreenBody>
    </div>
  )
}
