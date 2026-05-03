import { Send, Trash2 } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import type { Lang, Level } from '../App'
import VoiceInput from './VoiceInput'

interface Message { role: 'user' | 'assistant'; text: string; citations?: string[] }

const SAMPLES: Record<Lang, string[]> = {
  en: ['How do I register to vote?', 'What is the Model Code of Conduct?', 'What ID is accepted at polling booth?'],
  hi: ['मतदाता पंजीकरण कैसे करूं?', 'आदर्श आचार संहिता क्या है?', 'EVM कैसे काम करती है?'],
}

interface Props { lang: Lang; level: Level }

export default function ChatPanel({ lang, level }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState('')
  const sessionId = useRef(crypto.randomUUID())
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text: string) => {
    const msg = text.trim()
    if (!msg || streaming) return
    setInput('')
    setError('')
    setMessages(prev => [...prev, { role: 'user', text: msg }, { role: 'assistant', text: '' }])
    setStreaming(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: sessionId.current, lang, level }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buf = ''
      let citations: string[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        const parts = buf.split('\n\n')
        buf = parts.pop() ?? ''
        for (const part of parts) {
          const eventMatch = part.match(/event:\s*(\w+)/)
          const dataMatch = part.match(/data:\s*(.+)/s)
          if (!eventMatch || !dataMatch) continue
          const event = eventMatch[1]
          const raw = dataMatch[1].trim()
          if (event === 'token') {
            const token = JSON.parse(raw) as string
            setMessages(prev => {
              const copy = [...prev]
              copy[copy.length - 1] = { ...copy[copy.length - 1], text: copy[copy.length - 1].text + token }
              return copy
            })
          } else if (event === 'done') {
            citations = (JSON.parse(raw) as { citations: string[] }).citations
            setMessages(prev => {
              const copy = [...prev]
              copy[copy.length - 1] = { ...copy[copy.length - 1], citations }
              return copy
            })
          }
        }
      }
    } catch (e) {
      setError(lang === 'hi' ? 'कुछ गलत हुआ। पुनः प्रयास करें।' : 'Something went wrong. Try again.')
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setStreaming(false)
      textareaRef.current?.focus()
    }
  }

  return (
    <div className="flex flex-col h-full" aria-busy={streaming}>
      {/* Message list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" aria-live="polite" aria-atomic="false">
        {messages.length === 0 && (
          <div className="text-center text-text-muted py-8">
            <p className="text-lg font-medium mb-4">
              {lang === 'hi' ? 'नमस्ते! कुछ भी पूछें।' : 'Hello! Ask anything about Indian elections.'}
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SAMPLES[lang].map(s => (
                <button key={s} onClick={() => send(s)} className="px-3 py-1.5 bg-accent-light text-accent rounded-full text-sm hover:bg-accent hover:text-white transition-colors">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${m.role === 'user' ? 'bg-accent text-white rounded-br-sm' : 'bg-white border border-slate-200 rounded-bl-sm'}`}>
              <p className="text-xs font-medium mb-1 opacity-70">
                {m.role === 'user' ? (lang === 'hi' ? 'आप' : 'You') : (lang === 'hi' ? 'चुनाव साथी' : 'Chunav Saathi')}
              </p>
              {m.role === 'assistant'
                ? <div className="prose prose-sm max-w-none"><ReactMarkdown>{m.text || (streaming && i === messages.length - 1 ? '▋' : '')}</ReactMarkdown></div>
                : <p className="text-sm whitespace-pre-wrap">{m.text}</p>
              }
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100 flex flex-wrap gap-1">
                  {m.citations.slice(0, 3).map(c => (
                    <span key={c} className="text-xs bg-slate-100 text-text-muted px-2 py-0.5 rounded-full">{c.split(':')[0]}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && <div role="alert" className="mx-4 mb-2 px-3 py-2 bg-error-light text-error rounded-lg text-sm">{error}</div>}

      {/* Input bar */}
      <div className="border-t border-slate-200 bg-white p-3 flex items-end gap-2">
        {messages.length > 0 && (
          <button onClick={() => setMessages([])} aria-label={lang === 'hi' ? 'चैट साफ़ करें' : 'Clear chat'} className="p-2 text-text-muted hover:text-error transition-colors flex-shrink-0">
            <Trash2 className="w-4 h-4" />
          </button>
        )}
        <label className="sr-only" htmlFor="chat-input">{lang === 'hi' ? 'संदेश' : 'Message'}</label>
        <textarea
          id="chat-input"
          ref={textareaRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }}
          placeholder={lang === 'hi' ? 'चुनाव के बारे में पूछें…' : 'Ask about elections…'}
          rows={1}
          className="flex-1 resize-none border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
          disabled={streaming}
        />
        <VoiceInput lang={lang} onResult={t => send(t)} />
        <button
          onClick={() => send(input)}
          disabled={!input.trim() || streaming}
          aria-label={lang === 'hi' ? 'भेजें' : 'Send'}
          className="p-2 bg-accent text-white rounded-xl disabled:opacity-40 hover:bg-accent-hover transition-colors flex-shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
