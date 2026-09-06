interface ChatMessage {
  from: 'contractor' | 'relay'
  text: string
}

const THREAD: ChatMessage[] = [
  { from: 'contractor', text: 'I need a mini excavator for 3 days starting Monday in Bridgetown.' },
  {
    from: 'relay',
    text: 'Mini Excavator 2T is available Mon–Wed in Bridgetown — BBD $540 total, BBD $162 deposit. Want me to lock it in?',
  },
  { from: 'contractor', text: 'Yes, book it.' },
  {
    from: 'relay',
    text: "Booked! Reference REL-4F2A91C0. I've texted a deposit link — pay BBD $162 to confirm delivery.",
  },
]

export function ChatDemo() {
  return (
    <div className="overflow-hidden rounded-3xl bg-relay-green-950 p-6 text-relay-cream md:p-7">
      <div className="flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 font-display text-sm font-bold">
          R
        </span>
        <div>
          <p className="font-display text-sm font-semibold">Relay</p>
          <p className="text-xs text-relay-green-100/60">WhatsApp · SMS</p>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3">
        {THREAD.map((m, i) => (
          <div key={i} className={`flex ${m.from === 'contractor' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-snug ${
                m.from === 'contractor' ? 'bg-relay-orange-500 text-relay-cream' : 'bg-white/10 text-relay-cream'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
