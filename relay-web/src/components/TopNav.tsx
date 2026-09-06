import { NavLink } from 'react-router-dom'
import { Home, Truck, CalendarDays, UserRound } from 'lucide-react'
import { Logo } from './Logo'
import { Avatar } from './Avatar'

const ITEMS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/equipment', label: 'Equipment', icon: Truck },
  { to: '/bookings', label: 'Bookings', icon: CalendarDays },
  { to: '/profile', label: 'Profile', icon: UserRound },
]

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-black/5 bg-relay-cream/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-8 py-4">
        <Logo />

        <nav className="flex items-center gap-1">
          {ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
                  isActive ? 'bg-relay-green-800 text-relay-cream' : 'text-relay-muted hover:bg-black/5'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <Avatar />
      </div>
    </header>
  )
}
