import { useEffect, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { BottomNav } from './BottomNav'
import { ToastProvider } from '../lib/toast'

const TAB_ROUTES = ['/', '/equipment', '/bookings', '/profile']

export function PhoneShell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const showNav = TAB_ROUTES.includes(location.pathname)

  return (
    <div className="flex min-h-screen w-full justify-center bg-[#dfe3de] font-body sm:items-center sm:py-8">
      <div className="relative flex h-dvh w-full flex-col overflow-hidden bg-relay-sand sm:h-[880px] sm:max-w-[402px] sm:rounded-[2.75rem] sm:border-[6px] sm:border-relay-ink sm:shadow-2xl">
        <StatusBar />
        <ToastProvider>
          <div className="flex-1 overflow-y-auto overscroll-contain">{children}</div>
          {showNav && <BottomNav />}
        </ToastProvider>
      </div>
    </div>
  )
}

function StatusBar() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const id = window.setInterval(() => setTime(new Date()), 30_000)
    return () => window.clearInterval(id)
  }, [])
  const label = time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  return (
    <div className="hidden shrink-0 items-center justify-center px-7 pb-1 pt-3 text-[13px] font-semibold text-relay-ink sm:flex">
      <span>{label}</span>
    </div>
  )
}
