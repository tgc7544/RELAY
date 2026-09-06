import { Link } from 'react-router-dom'

export function Logo({ dark = false }: { dark?: boolean }) {
  return (
    <Link
      to="/"
      className="flex items-center font-display text-xl font-bold tracking-tight transition-transform active:scale-95"
      style={{ color: dark ? '#fdfcf9' : '#002518' }}
    >
      Relay
      <span style={{ color: '#d15e30' }}>.</span>
    </Link>
  )
}
