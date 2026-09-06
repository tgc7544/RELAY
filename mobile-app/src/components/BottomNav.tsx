import { Home, Truck, CalendarDays, UserRound } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const ITEMS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/equipment', label: 'Equipment', icon: Truck },
  { to: '/bookings', label: 'Bookings', icon: CalendarDays },
  { to: '/profile', label: 'Profile', icon: UserRound },
]

export function BottomNav() {
  return (
    <nav className="flex shrink-0 items-stretch border-t border-black/5 bg-relay-sand/95 px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-1.5 backdrop-blur">
      {ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end
          className={({ isActive }) =>
            `flex flex-1 flex-col items-center gap-1 rounded-2xl py-2 transition-colors ${
              isActive ? 'text-relay-green-700' : 'text-relay-muted'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Icon size={22} strokeWidth={isActive ? 2.4 : 1.8} />
              <span className={`text-[11px] ${isActive ? 'font-semibold' : 'font-medium'}`}>{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )
}
