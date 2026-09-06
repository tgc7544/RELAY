import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { supabase } from '../lib/supabase'
import type { Equipment } from '../lib/types'
import { parishFor, typeLabel, photoForType } from '../lib/equipment'
import { formatBBD, dayCount } from '../lib/format'
import { Logo } from '../components/Logo'

const CONTRACTOR_NAME = 'James Clarke'
const CONTRACTOR_PHONE = '+1 246 555 0148'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}
function addDaysISO(dateStr: string, days: number) {
  const d = new Date(`${dateStr}T00:00:00`)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export function Booking() {
  const { equipmentId } = useParams()
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment | null>(null)
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState(todayISO())
  const [endDate, setEndDate] = useState(addDaysISO(todayISO(), 1))
  const [location, setLocation] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!equipmentId) return
    supabase
      .from('equipment')
      .select('*')
      .eq('id', equipmentId)
      .single()
      .then(({ data }) => {
        setEquipment((data as Equipment) ?? null)
        setLoading(false)
      })
  }, [equipmentId])

  const days = useMemo(() => dayCount(startDate, endDate), [startDate, endDate])
  const total = useMemo(() => (equipment ? equipment.daily_rate * days : 0), [equipment, days])
  const deposit = total * 0.3
  const balance = total - deposit
  const canConfirm = !!equipment && !!location.trim() && days > 0 && !submitting

  async function handleConfirm() {
    if (!equipment) return
    setSubmitting(true)
    setError(null)
    const { data, error } = await supabase
      .from('bookings')
      .insert({
        equipment_id: equipment.id,
        contractor_name: CONTRACTOR_NAME,
        contractor_phone: CONTRACTOR_PHONE,
        start_date: startDate,
        end_date: endDate,
        delivery_location: location.trim(),
        total_amount: Number(total.toFixed(2)),
        deposit_amount: Number(deposit.toFixed(2)),
        balance_amount: Number(balance.toFixed(2)),
        status: 'pending',
      })
      .select()
      .single()

    setSubmitting(false)
    if (error) {
      setError(error.message)
      return
    }
    navigate(`/confirmed/${data.booking_id}`)
  }

  return (
    <div className="screen-enter flex flex-col gap-5 px-5 pb-8 pt-5">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm font-medium text-relay-muted">
          <ChevronLeft size={18} /> Back
        </button>
        <Logo />
      </div>

      {loading ? (
        <div className="h-40 skeleton rounded-2xl" />
      ) : !equipment ? (
        <p className="text-sm text-relay-muted">Equipment not found.</p>
      ) : (
        <>
          <img
            src={photoForType(equipment.type)}
            alt={equipment.name}
            className="h-44 w-full rounded-3xl object-cover"
          />

          <div>
            <h1 className="font-display text-xl font-bold text-relay-ink">{equipment.name}</h1>
            <p className="mt-0.5 text-sm text-relay-muted">
              {typeLabel(equipment.type)} · {typeLabel(equipment.size_category)} · {parishFor(equipment.id)}
            </p>
            <p className="mt-2 font-display text-lg font-bold text-relay-green-800">
              {formatBBD(equipment.daily_rate)} <span className="text-sm font-medium text-relay-muted">/ day</span>
            </p>
          </div>

          <div className="space-y-3 rounded-2xl bg-white p-4 shadow-sm shadow-black/5">
            <div className="grid grid-cols-2 gap-3">
              <label className="flex flex-col gap-1 text-xs font-semibold text-relay-muted">
                Start date
                <input
                  type="date"
                  value={startDate}
                  min={todayISO()}
                  onChange={(e) => {
                    setStartDate(e.target.value)
                    if (e.target.value >= endDate) setEndDate(addDaysISO(e.target.value, 1))
                  }}
                  className="rounded-xl border border-black/10 px-3 py-2 text-sm text-relay-ink outline-none focus:border-relay-green-700"
                />
              </label>
              <label className="flex flex-col gap-1 text-xs font-semibold text-relay-muted">
                End date
                <input
                  type="date"
                  value={endDate}
                  min={addDaysISO(startDate, 1)}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="rounded-xl border border-black/10 px-3 py-2 text-sm text-relay-ink outline-none focus:border-relay-green-700"
                />
              </label>
            </div>
            <label className="flex flex-col gap-1 text-xs font-semibold text-relay-muted">
              Delivery location
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Fontabelle, Bridgetown"
                className="rounded-xl border border-black/10 px-3 py-2 text-sm text-relay-ink outline-none focus:border-relay-green-700"
              />
            </label>
          </div>

          <div className="space-y-2 rounded-2xl bg-relay-green-50 p-4">
            <div className="flex justify-between text-sm text-relay-ink">
              <span>
                {formatBBD(equipment.daily_rate)} × {days} day{days > 1 ? 's' : ''}
              </span>
              <span className="font-semibold">{formatBBD(total)}</span>
            </div>
            <div className="flex justify-between border-t border-relay-green-100 pt-2 text-sm text-relay-ink">
              <span>Deposit due now (30%)</span>
              <span className="font-semibold">{formatBBD(deposit)}</span>
            </div>
            <div className="flex justify-between text-xs text-relay-muted">
              <span>Balance on delivery</span>
              <span>{formatBBD(balance)}</span>
            </div>
          </div>

          {error && (
            <div className="rounded-xl bg-relay-orange-50 p-3 text-xs text-relay-orange-600">
              Couldn't save your booking: {error}
            </div>
          )}

          <button
            onClick={handleConfirm}
            disabled={!canConfirm}
            className="rounded-2xl bg-relay-green-700 py-4 text-center font-display text-base font-semibold text-relay-cream transition-transform active:scale-[0.98] disabled:opacity-40"
          >
            {submitting ? 'Confirming…' : 'Confirm Booking'}
          </button>
        </>
      )}
    </div>
  )
}
