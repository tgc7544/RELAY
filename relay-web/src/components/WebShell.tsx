import type { ReactNode } from 'react'
import { TopNav } from './TopNav'
import { ToastProvider } from '../lib/toast'

export function WebShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen bg-relay-sand font-body">
      <ToastProvider>
        <TopNav />
        <main>{children}</main>
      </ToastProvider>
    </div>
  )
}
