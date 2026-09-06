import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { supabase } from '../lib/supabase'
import type { Equipment } from '../lib/types'
import { EquipmentGridCard } from '../components/EquipmentGridCard'
import { ScreenHero } from '../components/ScreenHero'
import { ScreenBody } from '../components/ScreenBody'
import { CATEGORY_CHIPS, matchesChip, type CategoryChip } from '../lib/equipment'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export function Browse() {
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [bookedIds, setBookedIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [chip, setChip] = useState<CategoryChip>('All')

  useEffect(() => {
    supabase
      .from('equipment')
      .select('*')
      .order('daily_rate', { ascending: true })
      .then(({ data, error }) => {
        if (error) setError(error.message)
        setEquipment((data as Equipment[]) ?? [])
        setLoading(false)
      })

    supabase
      .from('bookings')
      .select('equipment_id, start_date, end_date, status')
      .then(({ data }) => {
        const today = todayISO()
        const ids = new Set<string>()
        for (const b of data ?? []) {
          if (b.status !== 'completed' && b.start_date <= today && b.end_date >= today) {
            ids.add(b.equipment_id)
          }
        }
        setBookedIds(ids)
      })
  }, [])

  const filtered = equipment.filter(
    (e) => e.name.toLowerCase().includes(query.toLowerCase()) && matchesChip(e.type, chip),
  )

  return (
    <div className="screen-enter flex flex-col">
      <ScreenHero title="Equipment" subtitle="Live availability, delivered across Barbados" />

      <ScreenBody>
        <div className="mx-auto flex max-w-7xl flex-col gap-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="flex flex-1 items-center gap-2 rounded-2xl bg-white px-4 py-3 shadow-sm shadow-black/5">
              <Search size={18} className="text-relay-muted" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search excavators, trucks, generators..."
                className="w-full bg-transparent text-sm text-relay-ink outline-none placeholder:text-relay-muted"
              />
            </div>

            <div className="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
              {CATEGORY_CHIPS.map((c) => (
                <button
                  key={c}
                  onClick={() => setChip(c)}
                  className={`shrink-0 rounded-full px-4 py-2 text-xs font-semibold transition-colors ${
                    chip === c
                      ? 'bg-relay-green-800 text-relay-cream'
                      : 'bg-white text-relay-muted shadow-sm shadow-black/5'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {error ? (
            <div className="rounded-2xl bg-relay-orange-50 p-4 text-sm text-relay-orange-600">
              Couldn't load equipment: {error}
            </div>
          ) : loading ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[0, 1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-72 skeleton rounded-2xl" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-black/10 bg-white p-6 text-center text-sm text-relay-muted">
              No equipment matches yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((item) => (
                <EquipmentGridCard
                  key={item.id}
                  equipment={item}
                  available={item.active && !bookedIds.has(item.id)}
                  onSelect={() => navigate(`/booking/${item.id}`)}
                />
              ))}
            </div>
          )}
        </div>
      </ScreenBody>
    </div>
  )
}
