import { Mic, MicOff } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import type { Lang } from '../App'

interface Props { lang: Lang; onResult: (text: string) => void }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecognition = any

const getSR = (): AnyRecognition | undefined => {
  if (typeof window === 'undefined') return undefined
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = window as any
  return w.SpeechRecognition || w.webkitSpeechRecognition
}

export default function VoiceInput({ lang, onResult }: Props) {
  const [listening, setListening] = useState(false)
  const recogRef = useRef<AnyRecognition>(null)
  const SR = getSR()

  useEffect(() => { return () => recogRef.current?.abort() }, [])

  if (!SR) return null

  const toggle = () => {
    if (listening) { recogRef.current?.stop(); setListening(false); return }
    const r = new SR()
    r.lang = lang === 'hi' ? 'hi-IN' : 'en-IN'
    r.interimResults = false
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    r.onresult = (e: any) => { onResult(e.results[0][0].transcript); setListening(false) }
    r.onerror = () => setListening(false)
    r.onend = () => setListening(false)
    recogRef.current = r; r.start(); setListening(true)
  }

  return (
    <button
      type="button"
      aria-pressed={listening}
      aria-label={listening ? 'Stop recording' : 'Voice input'}
      onClick={toggle}
      className={`p-2 rounded-full transition-colors flex-shrink-0 ${listening ? 'bg-error text-white animate-pulse' : 'text-text-muted hover:text-accent'}`}
    >
      {listening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
    </button>
  )
}
