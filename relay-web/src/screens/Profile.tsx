import { useNavigate } from 'react-router-dom'
import { ChevronRight, Phone, MapPin, ShieldCheck, type LucideIcon } from 'lucide-react'
import { Avatar } from '../components/Avatar'
import { ScreenHero } from '../components/ScreenHero'
import { ScreenBody } from '../components/ScreenBody'

export function Profile() {
  const navigate = useNavigate()
  return (
    <div className="screen-enter flex flex-col">
      <ScreenHero title="Profile" subtitle="Manage your account" />

      <ScreenBody>
        <div className="mx-auto flex max-w-xl flex-col gap-6">
          <div className="flex flex-col items-center gap-3 rounded-2xl bg-white p-6 text-center shadow-sm shadow-black/5">
            <Avatar size={64} />
            <div>
              <h2 className="font-display text-lg font-bold text-relay-ink">James Clarke</h2>
              <p className="text-sm text-relay-muted">Contractor · Barbados</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <InfoRow icon={Phone} label="Phone" value="+1 246 555 0148" />
            <InfoRow icon={MapPin} label="Base parish" value="St. Michael" />
            <InfoRow icon={ShieldCheck} label="Member since" value="2026" />
          </div>

          <button
            onClick={() => navigate('/owner')}
            className="flex items-center justify-between rounded-2xl bg-relay-green-800 p-5 text-left shadow-lg shadow-black/10 transition-transform active:scale-[0.98]"
          >
            <div>
              <p className="font-display text-sm font-semibold text-relay-cream">Owner Dashboard</p>
              <p className="text-xs text-relay-green-100/80">List equipment & track payouts</p>
            </div>
            <ChevronRight size={18} className="text-relay-cream" />
          </button>
        </div>
      </ScreenBody>
    </div>
  )
}

function InfoRow({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl bg-white p-4 text-center shadow-sm shadow-black/5">
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-relay-green-50 text-relay-green-700">
        <Icon size={16} />
      </span>
      <div>
        <p className="text-xs text-relay-muted">{label}</p>
        <p className="text-sm font-medium text-relay-ink">{value}</p>
      </div>
    </div>
  )
}
