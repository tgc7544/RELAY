import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react'

interface ToastContextValue {
  showToast: (message: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState<string | null>(null)
  const timeoutRef = useRef<number | null>(null)

  const showToast = useCallback((msg: string) => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current)
    setMessage(msg)
    timeoutRef.current = window.setTimeout(() => setMessage(null), 2200)
  }, [])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        className={`pointer-events-none absolute inset-x-0 z-50 flex justify-center transition-all duration-300 ${
          message ? 'bottom-24 opacity-100' : 'bottom-16 opacity-0'
        }`}
      >
        {message && (
          <div className="rounded-full bg-relay-ink/95 px-4 py-2.5 text-center text-sm font-medium text-relay-cream shadow-lg">
            {message}
          </div>
        )}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
